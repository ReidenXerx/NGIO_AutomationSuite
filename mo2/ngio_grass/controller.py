"""One generation run inside MO2: preflight checks, the per-season loop, and the hand-over.

Rules this keeps:
- The user's own files are never edited. The settings a run needs go into a top-priority mod
  ("NGIO Grass - Run Settings") that wins inside the virtual Data folder and is removed afterwards.
- Every mod this creates carries a marker file; only a marked mod is ever emptied or removed.
- The game is started by MO2 (startApplication), so it sees the virtual Data folder, and every
  file NGIO writes lands in that season's output mod (forcedCustomOverwrite), not in Overwrite.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import dataclass, field
from typing import Callable

import mobase

from . import winproc
from .core import cgid
from .core.ini import IniText
from .core.seasons import BY_KEY, LOD_MOD, NO_SEASONS, RUN_SETTINGS_MOD, Season
from .core.watchdog import Action, Observation, SeasonWatch, State, WatchConfig

NGIO_INI = "SKSE/Plugins/GrassControl.ini"
SEASONS_INI = "SKSE/Plugins/po3_SeasonsOfSkyrim.ini"
MARKER = "ngio-grass.json"
TRIGGER = "PrecacheGrass.txt"
GiB = 1024 ** 3


@dataclass
class Check:
    level: str          # "ok", "warn", "error"
    text: str
    fix_label: str = ""
    fix: Callable[[], None] | None = None


@dataclass
class SeasonResult:
    season: Season
    state: str = "waiting"
    cells: int = 0
    restarts: int = 0
    files: int = 0
    note: str = ""


@dataclass
class RunPlan:
    seasons: list[Season]
    lod_from: Season | None = None
    config: WatchConfig = field(default_factory=WatchConfig)


class RunController:
    def __init__(self, organizer: mobase.IOrganizer, log: Callable[[str], None]):
        self.o = organizer
        self.log = log
        self.plan: RunPlan | None = None
        self.results: list[SeasonResult] = []
        self.index = -1
        self.watch: SeasonWatch | None = None
        self.running = False
        self.finished = False
        self._launch_at = 0.0
        self._was_active: set[str] = set()
        self.resume = False

    # ---- where things are -------------------------------------------------------------
    def game(self) -> mobase.IPluginGame:
        return self.o.managedGame()

    def game_dir(self) -> str:
        return str(self.game().gameDirectory().absolutePath())

    def game_exe(self) -> str:
        return os.path.join(self.game_dir(), self.game().binaryName())

    def loader(self) -> str:
        name = "sksevr_loader.exe" if self.game().gameShortName().lower() == "skyrimvr" else "skse64_loader.exe"
        return os.path.join(self.game_dir(), name)

    def trigger(self) -> str:
        return os.path.join(self.game_dir(), TRIGGER)

    def state_file(self) -> str:
        d = os.path.join(self.o.pluginDataPath(), "ngio_grass")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "run.json")

    def _mod_dir(self, name: str) -> str:
        path = self.mod_path(name)
        if path is None:
            raise RuntimeError(f"the mod '{name}' is missing; was it removed during the run?")
        return path

    def parked(self) -> str:
        return os.path.join(os.path.dirname(self.state_file()), "PrecacheGrass.parked.txt")

    def _park(self) -> None:
        """Move the trigger (and NGIO's progress in it) out of the game folder.

        Left in place, it makes NGIO start precaching on the player's next normal launch, even
        outside MO2, writing straight into the real Data folder. Resume moves it back."""
        trig = self.trigger()
        for _ in range(10):                      # a just-killed game can still hold the file
            if not os.path.isfile(trig):
                return
            try:
                shutil.move(trig, self.parked())
                self.log(f"{TRIGGER} moved out of the game folder; Resume puts it back.")
                return
            except OSError:
                time.sleep(0.3)
        self.log(f"Could not move {TRIGGER} out of the game folder. Delete it before playing, "
                 "or NGIO will start generating grass on the next launch.")

    def _unpark(self) -> bool:
        if os.path.isfile(self.parked()) and not os.path.isfile(self.trigger()):
            shutil.move(self.parked(), self.trigger())
            return True
        return os.path.isfile(self.trigger())

    def mod_path(self, name: str) -> str | None:
        mod = self.o.modList().getMod(name)
        return mod.absolutePath() if mod is not None else None

    @staticmethod
    def _is_ours(path: str | None) -> bool:
        return path is not None and os.path.isfile(os.path.join(path, MARKER))

    def _ensure_mod(self, name: str) -> str:
        path = self.mod_path(name)
        if path is None:
            mod = self.o.createMod(mobase.GuessedString(name))
            if mod is None:
                raise RuntimeError(f"MO2 did not create the mod '{name}'")
            path = str(mod.absolutePath())
            with open(os.path.join(path, MARKER), "w", encoding="utf-8") as f:
                json.dump({"createdBy": "NGIO Grass Cache (MO2 plugin)"}, f)
        elif not self._is_ours(path):
            raise RuntimeError(f"A mod named '{name}' exists but was not made by this tool; rename it first")
        return path

    def _origin_path(self, origin: str) -> str:
        if origin.lower() == "data":
            return str(self.game().dataDirectory().absolutePath())
        if origin.lower() == "overwrite":
            return str(self.o.overwritePath())
        return self.mod_path(origin) or ""

    @staticmethod
    def _find_ci(root: str, rel: str) -> str | None:
        """Case-insensitive lookup of a relative path under root."""
        cur = root
        for part in rel.replace("\\", "/").split("/"):
            if not os.path.isdir(cur):
                return None
            match = next((n for n in os.listdir(cur) if n.lower() == part.lower()), None)
            if match is None:
                return None
            cur = os.path.join(cur, match)
        return cur

    def _winner(self, origins: list[str]) -> str:
        """The origin the game sees. Ranked here by priority rather than trusting the order of
        getFileOrigins, whose documentation does not say which way it is sorted."""
        ml = self.o.modList()

        def rank(o: str) -> int:
            if o.lower() == "overwrite":
                return 1 << 30
            if o.lower() == "data":
                return -1
            return ml.priority(o)

        return max(origins, key=rank)

    def user_file(self, rel: str) -> tuple[str, str] | None:
        """(origin, real path) of the copy the game would use if this tool's mods were not there."""
        origins = [o for o in self.o.getFileOrigins(rel) if o != RUN_SETTINGS_MOD]
        if not origins:
            return None
        best = self._winner(origins)
        path = self._find_ci(self._origin_path(best), rel)
        return (best, path) if path else None

    def _active(self, name: str) -> bool:
        st = self.o.modList().state(name)
        try:
            return bool(int(st) & int(mobase.ModState.ACTIVE))
        except TypeError:
            return bool(int(st) & int(mobase.ModState.ACTIVE.value))

    def dll_present(self, *names: str) -> bool:
        return any(self.o.resolvePath(f"SKSE/Plugins/{n}") for n in names)

    # ---- preflight --------------------------------------------------------------------
    def preflight(self, seasonal: bool) -> list[Check]:
        c: list[Check] = []
        short = self.game().gameShortName()
        if short.lower() not in ("skyrimse", "skyrimvr"):
            return [Check("error", f"This instance manages {self.game().gameName()}. NGIO grass cache is for Skyrim SE/AE.")]
        if short.lower() == "skyrimvr":
            c.append(Check("warn", "Skyrim VR: the tool starts sksevr_loader.exe. VR runs have not been tested yet."))
        c.append(Check("ok", "Script extender found.") if os.path.isfile(self.loader())
                 else Check("error", f"{os.path.basename(self.loader())} is not in the game folder. Install SKSE first."))

        if self.dll_present("NGIO-NG.dll", "GrassControl.dll"):
            c.append(Check("ok", "No Grass In Objects found."))
        else:
            c.append(Check("error", "No Grass In Objects is not active (no NGIO-NG.dll or GrassControl.dll)."))
        ngio = self.user_file(NGIO_INI)
        if ngio is None:
            c.append(Check("error", "GrassControl.ini was not found. Reinstall No Grass In Objects."))
        elif ngio[0].lower() == "overwrite":
            c.append(Check("warn", "Your GrassControl.ini in Overwrite overrides NGIO's own. NGIO's page warns about "
                                   "this; an older tool may have left it. It is used as your settings for this run."))

        if seasonal:
            if not self.dll_present("po3_SeasonsOfSkyrim.dll"):
                c.append(Check("error", "Seasons of Skyrim is not active (no po3_SeasonsOfSkyrim.dll), so every "
                                        "season would get the same grass. Install it, or choose No seasons."))
            elif self.user_file(SEASONS_INI) is None:
                c.append(Check("error", "po3_SeasonsOfSkyrim.ini was not found."))
            else:
                c.append(Check("ok", "Seasons of Skyrim found."))
            if not self.dll_present("GrassCacheHelperNG.dll"):
                c.append(Check("warn", "Grass Cache Helper NG is not active. You need it in game to load seasonal caches."))

        c += self._existing_cache_checks()

        if os.path.isfile(self.trigger()):
            c.append(Check("warn", f"{TRIGGER} is in the game folder, so NGIO will start generating grass on the "
                                   "next launch of the game, in MO2 or not. Start here uses it; to play first, move it out.",
                           "Move it out", self._park))
        if winproc.find_game(self.game_exe()):
            c.append(Check("error", "Skyrim is running. Close it before starting."))

        mem = winproc.memory()
        if mem:
            pf = mem["pagefile"] / GiB
            if pf < 10:
                c.append(Check("error", f"Pagefile is {pf:.0f} GB. The precache can use more memory than you have RAM; "
                                        "set a pagefile of 20 GB or more (System Properties > Advanced > Performance)."))
            elif pf < 20:
                c.append(Check("warn", f"Pagefile is {pf:.0f} GB. 20 GB or more is safer for large load orders."))
        return c

    def _existing_cache_checks(self) -> list[Check]:
        files = [f for f in self.o.findFiles("Grass", "*.cgid") if cgid.is_plain(os.path.basename(f))]
        if not files:
            return []
        origins: dict[str, int] = {}
        for f in files[:400]:
            found = list(self.o.getFileOrigins("Grass/" + os.path.basename(f)))
            if found:
                origin = self._winner(found)
                origins[origin] = origins.get(origin, 0) + 1
        ours = {s.mod_name for s in BY_KEY.values()} | {LOD_MOD}
        foreign = [o for o in origins if o not in ours]
        if not foreign:
            return []
        mods = [o for o in foreign if o.lower() not in ("data", "overwrite")]
        where = ", ".join("your game folder" if o.lower() == "data" else o for o in foreign)
        text = (f"{len(files)} grass cache files are already visible (from {where}). NGIO skips every cell that "
                "already has one, so those cells would keep their old grass.")
        if mods:
            def disable() -> None:
                for m in mods:
                    self.o.modList().setActive(m, False)
            return [Check("warn", text, "Disable those mods", disable)]
        return [Check("warn", text + " Files in the game folder or Overwrite have to be moved out by hand.")]

    # ---- the run ----------------------------------------------------------------------
    def start(self, plan: RunPlan, resume: bool = False) -> None:
        self.plan = plan
        self.results = [SeasonResult(s) for s in plan.seasons]
        self.index = -1
        self.running = True
        self.finished = False
        self.resume = resume
        # Our cache mods that were on before the run are switched back on at the end.
        self._was_active = {n for n in {x.mod_name for x in BY_KEY.values()} if self.mod_path(n) and self._active(n)}
        self._write_state()
        try:
            self._prepare_settings_mod()
            self._next_season()
        except Exception as e:
            self._abort(str(e))
            raise

    def _prepare_settings_mod(self) -> None:
        path = self._ensure_mod(RUN_SETTINGS_MOD)
        src = self.user_file(NGIO_INI)
        if src is None:
            raise RuntimeError("GrassControl.ini was not found")
        with open(src[1], "rb") as f:
            ini = IniText.from_bytes(f.read())
        # NGIO's own precache recipe: use the cache, and only load from it.
        ini.set("GrassConfig", "Use-grass-cache", "true")
        ini.set("GrassConfig", "Only-load-from-cache", "true")
        self._write(path, NGIO_INI, ini.to_bytes())
        self.log(f"Run settings: your GrassControl.ini (from {src[0]}) with use-grass-cache and "
                 "only-load-from-cache set to true. Your own file is not changed.")
        ml = self.o.modList()
        ml.setActive(RUN_SETTINGS_MOD, True)
        ml.setPriority(RUN_SETTINGS_MOD, len(ml.allModsByProfilePriority()) - 1)

    @staticmethod
    def _write(mod_path: str, rel: str, data: bytes) -> None:
        full = os.path.join(mod_path, *rel.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(data)

    def _set_season(self, season: Season) -> None:
        src = self.user_file(SEASONS_INI)
        if src is None:
            return
        with open(src[1], "rb") as f:
            ini = IniText.from_bytes(f.read())
        ini.set("Settings", "Season Type", str(season.type_number))
        self._write(self._mod_dir(RUN_SETTINGS_MOD), SEASONS_INI, ini.to_bytes())

    def _abort(self, why: str) -> None:
        """Any error mid-run ends the run cleanly: no stale watcher can act on another season."""
        self.log(f"The run stopped: {why}. Progress is kept; Resume continues it.")
        self.watch = None
        self.running = False
        for pid in winproc.find_game(self.game_exe()):
            winproc.terminate(pid)
        self._park()
        try:
            self._cleanup(success=False)
        except Exception as e:  # cleanup must not hide the original error
            self.log(f"Cleanup after the error failed too: {e}")

    def _next_season(self) -> None:
        self.watch = None                   # nothing may tick against the previous season
        self.index += 1
        if self.index >= len(self.results):
            self._finish()
            return
        r = self.results[self.index]
        s = r.season
        out = self._ensure_mod(s.mod_name)
        grass = os.path.join(out, "Grass")
        resuming = self.resume and self._unpark()
        if not resuming:
            if os.path.isfile(self.parked()):
                os.remove(self.parked())        # a fresh start drops old parked progress
            if os.path.isdir(grass):
                shutil.rmtree(grass)            # our own marked mod: last run's files for this season
            with open(self.trigger(), "w", encoding="utf-8"):
                pass
        self.resume = False
        self._set_season(s)
        ml = self.o.modList()
        # Every other cache mod of ours stays off while NGIO generates: finished seasons until the
        # end, and a LOD copy always, because its plain .cgid names would make NGIO skip cells.
        for name in {x.mod_name for x in BY_KEY.values()} | {LOD_MOD}:
            if name != s.mod_name and self.mod_path(name):
                ml.setActive(name, False)
        ml.setActive(s.mod_name, True)
        self.o.refresh(True)                # MO2 must see the new files before the game starts
        r.state = "starting"
        assert self.plan is not None
        self.watch = SeasonWatch(self.plan.config)
        self.watch.start(time.time())
        self._launch_at = time.time() + 5   # launch on a later tick, after the refresh settles
        self._write_state()
        self.log(f"{s.name}: {'resuming' if resuming else 'starting'}.")

    def _launch(self) -> None:
        s = self.results[self.index].season
        handle = self.o.startApplication(self.loader(), [], self.game_dir(), "", s.mod_name, False)
        self.log(f"{s.name}: game launched through MO2." if handle else f"{s.name}: MO2 could not start the game.")

    def tick(self) -> None:
        if not self.running or self.watch is None:
            return
        try:
            self._tick()
        except Exception as e:
            self._abort(str(e))

    def _vfs_ready(self) -> bool:
        """refresh() is asynchronous: launch only once MO2 serves the run's INI from our mod."""
        mod = self.mod_path(RUN_SETTINGS_MOD)
        got = self.o.resolvePath(NGIO_INI)
        if not mod or not got:
            return False
        return os.path.normcase(os.path.abspath(got)).startswith(os.path.normcase(os.path.abspath(mod)))

    def _tick(self) -> None:
        assert self.watch is not None
        r = self.results[self.index]
        if self._launch_at and time.time() >= self._launch_at:
            if not self._vfs_ready():
                if time.time() - self._launch_at > 90:
                    raise RuntimeError("MO2 did not pick up the run settings mod within 90 seconds")
                return                      # check again next tick
            self._launch_at = 0.0
            self._launch()
            return
        if self._launch_at:
            return
        trig = self.trigger()
        exists = os.path.isfile(trig)
        size = os.path.getsize(trig) if exists else 0
        pids = winproc.find_game(self.game_exe())
        if exists:
            try:
                with open(trig, "rb") as f:
                    r.cells = sum(1 for line in f if line.strip())
            except OSError:
                pass
        assert self.plan is not None
        before = self.watch.restarts
        action = self.watch.tick(Observation(time.time(), exists, size, bool(pids)))
        r.restarts = self.watch.restarts
        r.state = self.watch.state.value
        if self.watch.restarts != before:
            self.log(f"{r.season.name}: {self.watch.reason}. Restart {self.watch.restarts} of {self.plan.config.max_restarts}.")
        if action is Action.KILL:
            for pid in pids:
                winproc.terminate(pid)
        elif action is Action.LAUNCH:
            self._launch_at = time.time() + 2
        elif action is Action.FINISHED:
            self._season_done(r)
        elif action is Action.FAILED:
            r.note = self.watch.reason
            self.log(f"{r.season.name}: failed, {self.watch.reason}. Its progress is kept, so Resume continues it.")
            self.running = False
            self._park()
            self._cleanup(success=False)

    def _season_done(self, r: SeasonResult) -> None:
        if r is not self.current or self.watch is None:
            raise RuntimeError("a season finished that was not running")
        grass = os.path.join(self._mod_dir(r.season.mod_name), "Grass")
        renamed = cgid.add_suffix(grass, r.season.suffix)
        r.files = cgid.count(grass)
        r.state = "done"
        self.log(f"{r.season.name}: done, {r.files} cache files" + (f", renamed to *{r.season.suffix}.cgid." if renamed else "."))
        self._write_state()
        self._next_season()

    def _finish(self) -> None:
        self.running = False
        ml = self.o.modList()
        plan = self.plan
        assert plan is not None
        if plan.lod_from is not None and plan.lod_from is not NO_SEASONS:
            try:
                lod = self._ensure_mod(LOD_MOD)
                dst = os.path.join(lod, "Grass")
                if os.path.isdir(dst):
                    shutil.rmtree(dst)      # our own marked mod; no cells left over from an older run
                src = os.path.join(self._mod_dir(plan.lod_from.mod_name), "Grass")
                n = cgid.copy_without_suffix(src, plan.lod_from.suffix, dst)
                self.log(f"DynDOLOD LOD copy: {n} files from {plan.lod_from.name}, in '{LOD_MOD}' (left disabled; "
                         "enable it only while running TexGen/DynDOLOD).")
                ml.setActive(LOD_MOD, False)
            except Exception as e:
                self.log(f"The DynDOLOD LOD copy failed ({e}); the season caches are unaffected.")
        for name in self._was_active | {r.season.mod_name for r in self.results}:
            ml.setActive(name, True)
        self._cleanup(success=True)
        self.finished = True
        self.log("All done. The cache mods are enabled; keep Grass Cache Helper NG enabled to load seasonal grass.")

    def _cleanup(self, success: bool) -> None:
        mod = self.o.modList().getMod(RUN_SETTINGS_MOD)
        if mod is not None and self._is_ours(mod.absolutePath()):
            self.o.modList().removeMod(mod)
        self.o.refresh(True)
        if success:
            try:
                os.remove(self.state_file())
            except OSError:
                pass

    def stop(self) -> None:
        """Stop now; progress stays in PrecacheGrass.txt, so the next run resumes this season."""
        for pid in winproc.find_game(self.game_exe()):
            winproc.terminate(pid)
        for _ in range(10):
            if not winproc.find_game(self.game_exe()):
                break
            time.sleep(0.3)
        if self.running:
            self._park()
            self.log("Stopped. The current season resumes from where it was on the next run.")
        self.running = False
        self._cleanup(success=False)

    # ---- resume across MO2 restarts ----------------------------------------------------
    def _write_state(self) -> None:
        if self.plan is None:
            return
        data = {
            "seasons": [r.season.key for r in self.results if r.state != "done"],
            "lod_from": self.plan.lod_from.key if self.plan.lod_from else None,
        }
        with open(self.state_file(), "w", encoding="utf-8") as f:
            json.dump(data, f)

    def unfinished(self) -> RunPlan | None:
        try:
            with open(self.state_file(), encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return None
        seasons = [BY_KEY[k] for k in data.get("seasons", []) if k in BY_KEY]
        if not seasons:
            return None
        lod = BY_KEY.get(data.get("lod_from") or "")
        return RunPlan(seasons=seasons, lod_from=lod)

    @property
    def current(self) -> SeasonResult | None:
        return self.results[self.index] if 0 <= self.index < len(self.results) else None

    def is_active(self) -> bool:
        return self.running and self.watch is not None and self.watch.state not in (State.FINISHED, State.FAILED)
