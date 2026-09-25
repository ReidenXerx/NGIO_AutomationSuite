"use strict";
/**
 * One generation run inside Vortex: preflight checks, the per-season loop, and the hand-over.
 *
 * Under Vortex the game's Data folder holds real files (hardlinks into the staging folder), so:
 * - The run's settings are a real mod ("NGIO Grass - Run Settings") with rules that make it win
 *   over the mods that provide GrassControl.ini and po3_SeasonsOfSkyrim.ini. It is deployed once
 *   at the start and removed (and redeployed away) at the end. The user's own mods are never edited.
 * - Between seasons only the Season Type line changes. The staging file is rewritten in place, so a
 *   hardlink deployment sees it at once; any other deployment method gets a redeploy.
 * - NGIO writes new .cgid files straight into Data/Grass. After each season exactly the names that
 *   were not there before the season started are moved into that season's own mod. Files that were
 *   already there belong to other mods and are never touched.
 * - Every mod folder this creates carries a marker file; only a marked folder is emptied or removed.
 * - PrecacheGrass.txt never stays in the game folder while no run is active (it would make NGIO
 *   precache on the next normal launch): Stop, failure and a Vortex exit park it; Resume restores it.
 */
const fs = require("fs");
const path = require("path");
const { actions, selectors, util } = require("vortex-api");

const procs = require("./procs");
const cgid = require("./core/cgid");
const { IniText } = require("./core/ini");
const { BY_KEY, FOUR, ALL, NO_SEASONS, RUN_SETTINGS, LOD } = require("./core/seasons");
const { Action, State, SeasonWatch } = require("./core/watchdog");

const NGIO_INI = path.join("SKSE", "Plugins", "GrassControl.ini");
const SEASONS_INI = path.join("SKSE", "Plugins", "po3_SeasonsOfSkyrim.ini");
const MARKER = "ngio-grass.json";
const TRIGGER = "PrecacheGrass.txt";
const GAMES = ["skyrimse", "skyrimvr"];
const GiB = 1024 ** 3;

const exists = (p) => { try { fs.statSync(p); return true; } catch { return false; } };

class Runner {
  constructor(api) {
    this.api = api;
    this.listeners = new Set();
    this.logLines = [];
    this.results = [];
    this.running = false;
    this.finished = false;
    this.busy = false;
    this.index = -1;
    this.watch = null;
    this.plan = null;
    this.timer = null;
    this.launchAt = 0;
    this.before = new Set();
    this.wasEnabled = new Set();
    this.lastPids = [];
    this.resume = false;
    this.resumedInto = false;
  }

  // ---- plumbing ---------------------------------------------------------------------
  onChange(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
  emit() { for (const fn of this.listeners) { try { fn(); } catch { /* a view must not stop the run */ } } }

  log(text) {
    const line = `${new Date().toLocaleTimeString()}  ${text}`;
    this.logLines.push(line);
    if (this.logLines.length > 500) this.logLines.shift();
    try {
      fs.mkdirSync(path.dirname(this.logFile()), { recursive: true });
      fs.appendFileSync(this.logFile(), `${new Date().toISOString().slice(0, 10)} ${line}\n`);
    } catch { /* logging never stops a run */ }
    this.emit();
  }

  dataDir() { return path.join(util.getVortexPath("appData"), "ngio-grass"); }
  logFile() { return path.join(this.dataDir(), "run.log"); }
  stateFile() { return path.join(this.dataDir(), "run.json"); }
  parked() { return path.join(this.dataDir(), "PrecacheGrass.parked.txt"); }

  ctx() {
    const state = this.api.getState();
    const gameId = selectors.activeGameId(state);
    const discovery = state.settings?.gameMode?.discovered?.[gameId];
    const gamePath = discovery?.path;
    const profile = selectors.activeProfile(state);
    const staging = gameId ? selectors.installPathForGame(state, gameId) : undefined;
    const exe = gameId === "skyrimvr" ? "SkyrimVR.exe" : "SkyrimSE.exe";
    const loader = gameId === "skyrimvr" ? "sksevr_loader.exe" : "skse64_loader.exe";
    return {
      state, gameId, gamePath, profileId: profile?.id, staging,
      data: gamePath ? path.join(gamePath, "Data") : undefined,
      gameExe: gamePath ? path.join(gamePath, exe) : undefined,
      loader: gamePath ? path.join(gamePath, loader) : undefined,
      trigger: gamePath ? path.join(gamePath, TRIGGER) : undefined,
      mods: state.persistent?.mods?.[gameId] ?? {},
      enabled: (id) => !!state.persistent?.profiles?.[profile?.id]?.modState?.[id]?.enabled,
    };
  }

  /** Vortex's own record of which mod deployed which file into Data. */
  deploymentOwners(c) {
    try {
      const m = JSON.parse(fs.readFileSync(path.join(c.data, "vortex.deployment.json"), "utf8"));
      const owners = new Map();
      for (const f of m.files ?? []) owners.set(f.relPath.toLowerCase().replace(/\//g, "\\"), f.source);
      return { method: m.deploymentMethod, owners };
    } catch {
      return { method: undefined, owners: new Map() };
    }
  }

  /** A cache file another mod deployed after the season's snapshot (a deploy during the run) is
   * that mod's file, not a new cell: Vortex's deployment manifest says so. */
  foreign(c) {
    const { owners } = this.deploymentOwners(c);
    const ours = new Set([...ALL.map((s) => s.modId), LOD.modId]);
    return (nameLower) => {
      const src = owners.get(`grass\\${nameLower}`);
      return !!src && !ours.has(src);
    };
  }

  isOurs(folder) { return exists(path.join(folder, MARKER)); }

  ensureMod(c, spec) {
    const folder = path.join(c.staging, spec.modId);
    if (exists(folder) && !this.isOurs(folder)) {
      throw new Error(`A mod folder named '${spec.modId}' exists but was not made by this tool; rename it first`);
    }
    fs.mkdirSync(folder, { recursive: true });
    fs.writeFileSync(path.join(folder, MARKER), JSON.stringify({ createdBy: "NGIO Grass Cache (Vortex extension)" }));
    if (!c.mods[spec.modId]) {
      this.api.store.dispatch(actions.addMod(c.gameId, {
        id: spec.modId, state: "installed", type: "", installationPath: spec.modId,
        attributes: { name: spec.modName, logicalFileName: spec.modName, installTime: new Date(), source: "other",
          notes: "Made by NGIO Grass Cache. Safe to remove; regenerate it any time." },
      }));
    }
    return folder;
  }

  setEnabled(c, id, on) { this.api.store.dispatch(actions.setModEnabled(c.profileId, id, on)); }

  /** The run belongs to one profile; a switch in Vortex mid-run must stop it, never retarget it. */
  checkProfile(c) {
    if (this.profileId && c.profileId !== this.profileId) {
      throw new Error("Vortex's active profile or game changed during the run. Switch back and use Resume");
    }
  }

  deploy(c) {
    this.checkProfile(c);
    return new Promise((resolve, reject) => {
      let done = false;
      const finish = (err) => {
        if (done) return;
        done = true;
        clearTimeout(timer);
        this.api.events.removeListener("did-deploy", onDid);
        if (err) reject(err); else resolve();
      };
      const onDid = (profileId) => { if (profileId === c.profileId) finish(); };
      const timer = setTimeout(() => finish(new Error("Deployment did not finish within 30 minutes")), 30 * 60 * 1000);
      this.api.events.on("did-deploy", onDid);
      // Vortex's handler is (callback, profileId, ...): the callback comes FIRST.
      this.api.events.emit("deploy-mods", (err) => finish(err || undefined), c.profileId);
    });
  }

  // ---- preflight --------------------------------------------------------------------
  async preflight(seasonal) {
    const c = this.ctx();
    const out = [];
    const add = (level, text, fixLabel, fix) => out.push({ level, text, fixLabel, fix });
    if (!GAMES.includes(c.gameId)) {
      add("error", "Switch Vortex to Skyrim Special Edition (or VR) first.");
      return out;
    }
    if (c.gameId === "skyrimvr") add("warn", "Skyrim VR: the tool starts sksevr_loader.exe. VR runs have not been tested yet.");
    if (!c.gamePath || !c.staging || !c.profileId) {
      add("error", "Vortex has no game folder, staging folder or active profile for this game.");
      return out;
    }
    const plugins = path.join(c.data, "SKSE", "Plugins");
    const has = (...names) => names.some((n) => exists(path.join(plugins, n)));
    add(exists(c.loader) ? "ok" : "error",
      exists(c.loader) ? "Script extender found." : `${path.basename(c.loader)} is not in the game folder. Install SKSE first.`);
    add(has("NGIO-NG.dll", "GrassControl.dll") ? "ok" : "error",
      has("NGIO-NG.dll", "GrassControl.dll") ? "No Grass In Objects found." : "No Grass In Objects is not deployed (no NGIO-NG.dll or GrassControl.dll).");
    if (!exists(path.join(c.data, NGIO_INI))) add("error", "GrassControl.ini is not deployed. Reinstall No Grass In Objects and deploy.");
    if (seasonal) {
      if (!has("po3_SeasonsOfSkyrim.dll")) {
        add("error", "Seasons of Skyrim is not deployed (no po3_SeasonsOfSkyrim.dll), so every season would get the same grass. Install it, or choose No seasons.");
      } else if (!exists(path.join(c.data, SEASONS_INI))) {
        add("error", "po3_SeasonsOfSkyrim.ini is not deployed.");
      } else add("ok", "Seasons of Skyrim found.");
      if (!has("GrassCacheHelperNG.dll")) add("warn", "Grass Cache Helper NG is not deployed. You need it in game to load seasonal caches.");
    }

    const { method, owners } = this.deploymentOwners(c);
    if (method && method !== "hardlink_activator") {
      add("warn", `Vortex deploys this game with "${method}", so each season switch needs a short redeploy. Hardlink deployment avoids that.`);
    }
    const grassDir = path.join(c.data, "Grass");
    const plain = cgid.list(grassDir).filter(cgid.isPlain);
    if (plain.length) {
      const ours = new Set([...ALL.map((s) => s.modId), LOD.modId]);
      const fromMods = new Set();
      let loose = 0;
      for (const n of plain) {
        const src = owners.get(`grass\\${n.toLowerCase()}`);
        if (src && !ours.has(src)) fromMods.add(src); else if (!src) loose += 1;
      }
      const names = [...fromMods].map((id) => c.mods[id]?.attributes?.name ?? id);
      if (fromMods.size || loose) {
        const where = [...names, ...(loose ? [`${loose} files not from any Vortex mod`] : [])].join(", ");
        const text = `${plain.length} grass cache files are already in Data/Grass (from ${where}). NGIO skips every cell that already has one, so those cells would keep their old grass.`;
        if (fromMods.size) {
          add("warn", text, "Disable those mods and deploy", async () => {
            for (const id of fromMods) this.setEnabled(c, id, false);
            await this.deploy(this.ctx());
          });
        } else add("warn", `${text} Move them out of the game folder by hand.`);
      }
    }
    if (c.trigger && exists(c.trigger)) {
      add("warn", `${TRIGGER} is in the game folder, so NGIO will start generating grass on the next launch of the game. Start here uses it; to play first, move it out.`,
        "Move it out", async () => this.park(c));
    }
    if (c.gameExe && (await procs.findGame(c.gameExe)).length) add("error", "Skyrim is running. Close it before starting.");
    const pf = await procs.pagefileBytes();
    if (pf !== null) {
      if (pf < 10 * GiB) add("error", `Pagefile is ${Math.round(pf / GiB)} GB. The precache can use more memory than you have RAM; set a pagefile of 20 GB or more (System Properties > Advanced > Performance).`);
      else if (pf < 20 * GiB) add("warn", `Pagefile is ${Math.round(pf / GiB)} GB. 20 GB or more is safer for large load orders.`);
    }
    return out;
  }

  // ---- the run ----------------------------------------------------------------------
  async start(plan, resume = false) {
    const c = this.ctx();
    this.plan = plan;
    this.results = plan.seasons.map((season) => ({ season, state: "waiting", cells: 0, restarts: 0, files: 0, note: "" }));
    this.index = -1;
    this.running = true;
    this.finished = false;
    this.resume = resume;
    this.profileId = c.profileId;
    this.wasEnabled = new Set(ALL.map((s) => s.modId).filter((id) => c.mods[id] && c.enabled(id)));
    this.writeState();
    this.emit();
    try {
      await this.prepareSettingsMod();
      await this.nextSeason();
      this.timer = setInterval(() => { void this.tick(); }, 5000);
    } catch (e) {
      await this.abort(e.message);
      throw e;
    }
  }

  async prepareSettingsMod() {
    let c = this.ctx();
    const folder = this.ensureMod(c, RUN_SETTINGS);
    const { owners } = this.deploymentOwners(c);
    const write = (rel, edit) => {
      const src = path.join(c.data, rel);
      if (!exists(src)) return false;
      const ini = IniText.fromBuffer(fs.readFileSync(src));
      edit(ini);
      const dst = path.join(folder, rel);
      fs.mkdirSync(path.dirname(dst), { recursive: true });
      fs.writeFileSync(dst, ini.toBuffer());
      return true;
    };
    // NGIO's own precache recipe: use the cache, and only load from it.
    write(NGIO_INI, (ini) => { ini.set("GrassConfig", "Use-grass-cache", "true"); ini.set("GrassConfig", "Only-load-from-cache", "true"); });
    write(SEASONS_INI, () => {});
    // Win over whichever mods deploy these files now.
    for (const rel of [NGIO_INI, SEASONS_INI]) {
      const owner = owners.get(rel.toLowerCase());
      if (owner && owner !== RUN_SETTINGS.modId) {
        this.api.store.dispatch(actions.addModRule(c.gameId, RUN_SETTINGS.modId, { type: "after", reference: { id: owner } }));
      }
    }
    this.setEnabled(c, RUN_SETTINGS.modId, true);
    this.log("Deploying the run settings (your GrassControl.ini with use-grass-cache and only-load-from-cache set to true). Your own mods are not changed.");
    this.busy = true;
    try { await this.deploy(c); } finally { this.busy = false; }
    c = this.ctx();
    const live = IniText.fromBuffer(fs.readFileSync(path.join(c.data, NGIO_INI)));
    if (String(live.get("GrassConfig", "Only-load-from-cache")).toLowerCase() !== "true"
      || String(live.get("GrassConfig", "Use-grass-cache")).toLowerCase() !== "true") {
      throw new Error("After deploying, the game's GrassControl.ini still has the old values. Check Vortex's conflicts for GrassControl.ini.");
    }
  }

  async setSeason(season) {
    const c = this.ctx();
    const staged = path.join(c.staging, RUN_SETTINGS.modId, SEASONS_INI);
    if (!exists(staged)) return;
    const ini = IniText.fromBuffer(fs.readFileSync(staged));
    ini.set("Settings", "Season Type", String(season.typeNumber));
    fs.writeFileSync(staged, ini.toBuffer());      // in place: a hardlinked deployment sees it at once
    const live = () => IniText.fromBuffer(fs.readFileSync(path.join(c.data, SEASONS_INI))).get("Settings", "Season Type");
    if (live() !== String(season.typeNumber)) {
      this.busy = true;
      try { await this.deploy(c); } finally { this.busy = false; }
      if (live() !== String(season.typeNumber)) throw new Error("The game's po3_SeasonsOfSkyrim.ini did not take the season after a deploy.");
    }
  }

  async nextSeason() {
    this.watch = null;                  // nothing may tick against the previous season
    this.index += 1;
    if (this.index >= this.results.length) return this.finish();
    const c = this.ctx();
    const r = this.results[this.index];
    const resuming = this.resume && this.unpark(c);
    this.resume = false;
    this.resumedInto = resuming;        // per season: a resumed season keeps the files it already has
    if (!resuming) {
      if (exists(this.parked())) fs.unlinkSync(this.parked());
      fs.writeFileSync(c.trigger, "");
    }
    await this.setSeason(r.season);
    // Snapshot Data/Grass: only names that appear after this point are this season's cells.
    this.before = new Set(cgid.list(path.join(c.data, "Grass")).map((n) => n.toLowerCase()));
    r.state = "starting";
    this.watch = new SeasonWatch(this.plan.config);
    this.watch.start(Date.now() / 1000);
    this.launchAt = Date.now() + 1000;
    this.writeState();
    this.log(`${r.season.name}: ${resuming ? "resuming" : "starting"}.`);
  }

  launch() {
    const c = this.ctx();
    const r = this.results[this.index];
    this.api.runExecutable(c.loader, [], {
      cwd: c.gamePath, suggestDeploy: false, detach: true, shell: false,
      onSpawned: (pid) => {
        if (typeof pid !== "number" || pid <= 0) return;      // spawn failed; the error follows
        this.log(`${r.season.name}: game launched.`);
        if (typeof actions.setToolRunning === "function") {
          // Vortex's process monitor then blocks a deploy or purge under the running game.
          this.api.store.dispatch(actions.setToolRunning(c.loader, Date.now(), true));
        }
      },
    }).catch((e) => this.log(`${r.season.name}: the game did not start (${e.message}).`));
  }

  async tick() {
    if (!this.running || !this.watch || this.busy) return;
    this.busy = true;
    try {
      await this.step();
    } catch (e) {
      await this.abort(e.message);
    } finally {
      this.busy = false;
      this.emit();
    }
  }

  async step() {
    const c = this.ctx();
    this.checkProfile(c);
    const r = this.results[this.index];
    if (this.launchAt) {
      if (Date.now() < this.launchAt) return;
      this.launchAt = 0;
      this.launch();
      return;
    }
    const trig = exists(c.trigger);
    let size = 0;
    if (trig) {
      const buf = fs.readFileSync(c.trigger);
      size = buf.length;
      r.cells = buf.toString("utf8").split(/\r?\n/).filter((l) => l.trim()).length;
    }
    const pids = await procs.findGame(c.gameExe);
    this.lastPids = pids;
    const before = this.watch.restarts;
    const action = this.watch.tick({ now: Date.now() / 1000, triggerExists: trig, triggerSize: size, gameAlive: pids.length > 0 });
    r.restarts = this.watch.restarts;
    r.state = this.watch.state;
    if (this.watch.restarts !== before) this.log(`${r.season.name}: ${this.watch.reason}. Restart ${this.watch.restarts} of ${this.plan.config.maxRestarts}.`);
    if (action === Action.KILL) pids.forEach(procs.terminate);
    else if (action === Action.LAUNCH) this.launchAt = Date.now() + 2000;
    else if (action === Action.FINISHED) await this.seasonDone(r);
    else if (action === Action.FAILED) {
      r.note = this.watch.reason;
      this.log(`${r.season.name}: failed, ${this.watch.reason}. Its progress is kept, so Resume continues it.`);
      await this.stopRun(false);
    }
  }

  async seasonDone(r) {
    if (r !== this.results[this.index] || !this.watch) throw new Error("a season finished that was not running");
    const c = this.ctx();
    this.stopToolRunning(c);
    const folder = this.ensureMod(c, r.season);
    const grass = path.join(folder, "Grass");
    if (!this.resumedInto) fs.rmSync(grass, { recursive: true, force: true });
    r.files = cgid.moveNew(path.join(c.data, "Grass"), this.before, grass, r.season.suffix, this.foreign(c));
    r.state = "done";
    this.log(`${r.season.name}: done, ${r.files} cache files moved into '${r.season.modName}'.`);
    this.writeState();
    await this.nextSeason();
  }

  async finish() {
    const c = this.ctx();
    const plan = this.plan;
    if (plan.lodFrom && plan.lodFrom !== NO_SEASONS && !this.results.some((x) => x.season === plan.lodFrom)) {
      this.log(`No DynDOLOD LOD copy: ${plan.lodFrom.name} was not generated in this run.`);
    } else if (plan.lodFrom && plan.lodFrom !== NO_SEASONS) {
      try {
        const lod = this.ensureMod(c, LOD);
        const dst = path.join(lod, "Grass");
        fs.rmSync(dst, { recursive: true, force: true });
        const n = cgid.copyWithoutSuffix(path.join(c.staging, plan.lodFrom.modId, "Grass"), plan.lodFrom.suffix, dst);
        this.setEnabled(c, LOD.modId, false);
        this.log(`DynDOLOD LOD copy: ${n} files from ${plan.lodFrom.name}, in '${LOD.modName}' (left disabled; enable it only while running TexGen/DynDOLOD).`);
      } catch (e) {
        this.log(`The DynDOLOD LOD copy failed (${e.message}); the season caches are unaffected.`);
      }
    }
    for (const id of new Set([...this.wasEnabled, ...this.results.map((x) => x.season.modId)])) this.setEnabled(c, id, true);
    await this.cleanup(true);
    this.running = false;
    this.finished = true;
    this.log("All done. The cache mods are enabled and deployed; keep Grass Cache Helper NG enabled to load seasonal grass.");
  }

  // ---- stopping ---------------------------------------------------------------------
  stopToolRunning(c) {
    if (typeof actions.setToolStopped === "function") this.api.store.dispatch(actions.setToolStopped(c.loader));
  }

  park(c) {
    if (!c.trigger || !exists(c.trigger)) return;
    fs.mkdirSync(this.dataDir(), { recursive: true });
    fs.copyFileSync(c.trigger, this.parked());
    fs.unlinkSync(c.trigger);
    this.log(`${TRIGGER} moved out of the game folder; Resume puts it back.`);
  }

  unpark(c) {
    if (exists(this.parked()) && !exists(c.trigger)) {
      fs.copyFileSync(this.parked(), c.trigger);
      fs.unlinkSync(this.parked());
    }
    return exists(c.trigger);
  }

  async killGame(c) {
    for (let i = 0; i < 10; i++) {
      const pids = await procs.findGame(c.gameExe);
      if (!pids.length) return;
      pids.forEach(procs.terminate);
      await new Promise((r) => setTimeout(r, 500));
    }
  }

  async stopRun(byUser) {
    const c = this.ctx();
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
    this.watch = null;
    await this.killGame(c);
    this.stopToolRunning(c);
    // Cells made so far this season are real files in Data/Grass; collect them now, or a later
    // Resume would count them as someone else's (they would be in its "before" snapshot).
    const r = this.results[this.index];
    if (r && r.state !== "done") {
      try {
        const grass = path.join(this.ensureMod(c, r.season), "Grass");
        const n = cgid.moveNew(path.join(c.data, "Grass"), this.before, grass, r.season.suffix, this.foreign(c));
        if (n) this.log(`${r.season.name}: ${n} cache files made so far kept in '${r.season.modName}'.`);
      } catch (e) {
        this.log(`Could not collect this season's files so far (${e.message}).`);
      }
    }
    try { this.park(c); } catch (e) { this.log(`Could not move ${TRIGGER} out of the game folder (${e.message}). Delete it before playing.`); }
    this.running = false;
    if (byUser) this.log("Stopped. The current season resumes from where it was on the next run.");
    await this.cleanup(false);
  }

  /** Vortex is closing: no time for async work. Kill the last known game PIDs, keep this
   * season's cells, and move the trigger out of the game folder. */
  emergencyStop() {
    const c = this.ctx();
    (this.lastPids || []).forEach(procs.terminate);
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
    this.watch = null;
    this.running = false;
    const r = this.results[this.index];
    try {
      if (r && r.state !== "done") {
        cgid.moveNew(path.join(c.data, "Grass"), this.before, path.join(this.ensureMod(c, r.season), "Grass"), r.season.suffix, this.foreign(c));
      }
    } catch { /* best effort while closing */ }
    try { this.park(c); } catch { /* best effort while closing */ }
  }

  async abort(why) {
    this.log(`The run stopped: ${why}. Progress is kept; Resume continues it.`);
    try { await this.stopRun(false); } catch (e) { this.log(`Cleanup after the error failed too: ${e.message}`); }
  }

  async cleanup(success) {
    const c = this.ctx();
    if (c.mods[RUN_SETTINGS.modId]) {
      this.setEnabled(c, RUN_SETTINGS.modId, false);
      this.busy = true;
      try { await this.deploy(c); } catch (e) { this.log(`Deploy after the run failed (${e.message}); deploy once by hand.`); } finally { this.busy = false; }
      const folder = path.join(c.staging, RUN_SETTINGS.modId);
      this.api.store.dispatch(actions.removeMod(c.gameId, RUN_SETTINGS.modId));
      if (this.isOurs(folder)) fs.rmSync(folder, { recursive: true, force: true });
    } else if (success) {
      this.busy = true;
      try { await this.deploy(c); } finally { this.busy = false; }
    }
    if (success) { try { fs.unlinkSync(this.stateFile()); } catch { /* already gone */ } }
    this.emit();
  }

  // ---- resume across Vortex restarts -------------------------------------------------
  writeState() {
    if (!this.plan) return;
    fs.mkdirSync(this.dataDir(), { recursive: true });
    fs.writeFileSync(this.stateFile(), JSON.stringify({
      seasons: this.results.filter((r) => r.state !== "done").map((r) => r.season.key),
      lodFrom: this.plan.lodFrom?.key ?? null,
    }));
  }

  unfinished() {
    try {
      const d = JSON.parse(fs.readFileSync(this.stateFile(), "utf8"));
      const seasons = (d.seasons ?? []).map((k) => BY_KEY[k]).filter(Boolean);
      return seasons.length ? { seasons, lodFrom: BY_KEY[d.lodFrom] ?? null } : null;
    } catch {
      return null;
    }
  }
}

module.exports = { Runner, FOUR, NO_SEASONS, State };
