"""Tests for the MO2 plugin's core: run with `python -m unittest discover -s mo2/tests` from the repo root.

Fixtures copy the real files' shape, measured on the owner's install: NGIO's GrassControl.ini keeps
its keys in [GrassConfig], hyphenated; po3_SeasonsOfSkyrim.ini starts with a UTF-8 BOM.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ngio_grass.core import cgid  # noqa: E402
from ngio_grass.core.ini import IniText  # noqa: E402
from ngio_grass.core.seasons import AUTUMN, NO_SEASONS, WINTER  # noqa: E402
from ngio_grass.core.watchdog import Action, Observation, SeasonWatch, State, WatchConfig  # noqa: E402

GRASS_CONTROL = (
    "[Debug]\r\n"
    "; Set true to write a debug log\r\n"
    "debug-log-enable = false\r\n"
    "\r\n"
    "[RayCastConfig]\r\n"
    "ray-cast-ignore-forms = \r\n"
    "ray-cast-texture-forms = 112D5520:Northern Roads.esp;112D5521:Northern Roads.esp\r\n"
    "\r\n"
    "[GrassConfig]\r\n"
    ";Set true if you want to enable extended grass distance mode.\r\n"
    "use-grass-cache = false\r\n"
    "extend-grass-distance = true\r\n"
    "only-load-from-cache = false\r\n"
    "\r\n"
    "[Settings]\r\n"
    "usegrasscache = True\r\n"
)

SEASONS = "﻿[Settings]\n\n;5 - seasonal\nSeason Type = 4\n\n;January\nMorning Star = 1\n"


class IniTests(unittest.TestCase):
    def test_reads_hyphenated_keys_case_insensitively(self):
        ini = IniText(GRASS_CONTROL)
        self.assertEqual(ini.get("GrassConfig", "Use-grass-cache"), "false")
        self.assertEqual(ini.get("grassconfig", "extend-grass-distance"), "true")
        self.assertIsNone(ini.get("GrassConfig", "usegrasscache"))  # lives in the dead [Settings] block

    def test_set_changes_only_that_line(self):
        ini = IniText(GRASS_CONTROL)
        self.assertTrue(ini.set("GrassConfig", "Use-grass-cache", "true"))
        self.assertTrue(ini.set("GrassConfig", "Only-load-from-cache", "true"))
        out = ini.to_text()
        self.assertIn("use-grass-cache = true\r\n", out)          # the file's own spelling kept
        self.assertIn("only-load-from-cache = true\r\n", out)
        self.assertIn(";Set true if you want to enable extended grass distance mode.\r\n", out)
        self.assertIn("112D5520:Northern Roads.esp;112D5521:Northern Roads.esp", out)
        self.assertEqual(out.replace("use-grass-cache = true", "use-grass-cache = false")
                            .replace("only-load-from-cache = true", "only-load-from-cache = false"), GRASS_CONTROL)

    def test_set_same_value_is_not_a_change(self):
        self.assertFalse(IniText(GRASS_CONTROL).set("GrassConfig", "extend-grass-distance", "true"))

    def test_missing_key_goes_before_the_blank_separator(self):
        ini = IniText(GRASS_CONTROL)
        ini.set("GrassConfig", "max-failures", "2")
        lines = ini.to_text().split("\r\n")
        at = lines.index("max-failures = 2")
        self.assertEqual(lines[at - 1], "only-load-from-cache = false")
        self.assertEqual(lines[at + 1], "")

    def test_missing_section_is_appended(self):
        ini = IniText("[A]\nx = 1\n")
        ini.set("B", "y", "2")
        self.assertEqual(ini.to_text(), "[A]\nx = 1\n\n[B]\ny = 2\n")

    def test_bom_and_season_type_round_trip(self):
        ini = IniText.from_bytes(SEASONS.encode("utf-8"))
        self.assertEqual(ini.get("Settings", "Season Type"), "4")
        ini.set("Settings", "Season Type", "1")
        data = ini.to_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(data.decode("utf-8"), SEASONS.replace("Season Type = 4", "Season Type = 1"))

    def test_value_with_equals_sign(self):
        ini = IniText("[S]\nonly-pregenerate-world-spaces = Tamriel;A=B\n")
        self.assertEqual(ini.get("S", "only-pregenerate-world-spaces"), "Tamriel;A=B")


class CgidTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        for n in ["Tamriel_0_0.cgid", "Tamriel_0_1.cgid", "Old_1_1.WIN.cgid", "notes.txt"]:
            with open(os.path.join(self.dir, n), "w") as f:
                f.write(n)

    def tearDown(self):
        self.tmp.cleanup()

    def test_adds_suffix_only_to_plain_files(self):
        self.assertEqual(cgid.add_suffix(self.dir, AUTUMN.suffix), 2)
        self.assertEqual(sorted(os.listdir(self.dir)),
                         ["Old_1_1.WIN.cgid", "Tamriel_0_0.AUT.cgid", "Tamriel_0_1.AUT.cgid", "notes.txt"])
        self.assertEqual(cgid.add_suffix(self.dir, AUTUMN.suffix), 0)  # a second pass changes nothing

    def test_no_seasons_keeps_plain_names(self):
        self.assertEqual(cgid.add_suffix(self.dir, NO_SEASONS.suffix), 0)
        self.assertIn("Tamriel_0_0.cgid", os.listdir(self.dir))

    def test_lod_copy_strips_the_suffix(self):
        dst = os.path.join(self.dir, "lod")
        self.assertEqual(cgid.copy_without_suffix(self.dir, WINTER.suffix, dst), 1)
        self.assertEqual(os.listdir(dst), ["Old_1_1.cgid"])

    def test_is_plain(self):
        self.assertTrue(cgid.is_plain("A_1_2.cgid"))
        self.assertFalse(cgid.is_plain("A_1_2.SUM.cgid"))
        self.assertFalse(cgid.is_plain("A_1_2.txt"))


def obs(now, exists=True, size=0, alive=True):
    return Observation(now=now, trigger_exists=exists, trigger_size=size, game_alive=alive)


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.cfg = WatchConfig(boot_seconds=300, stall_seconds=120, restart_delay_seconds=10,
                               max_restarts=2, appear_seconds=60, exit_grace_seconds=30)
        self.w = SeasonWatch(self.cfg)
        self.assertEqual(self.w.start(0), Action.LAUNCH)

    def test_slow_boot_is_not_a_hang(self):
        # A 4-minute boot with no progress yet: within boot_seconds, so no restart.
        self.assertEqual(self.w.tick(obs(5, size=0)), Action.WAIT)
        self.assertEqual(self.w.tick(obs(240, size=0)), Action.WAIT)
        self.assertEqual(self.w.state, State.RUNNING)
        self.assertEqual(self.w.restarts, 0)

    def test_boot_limit_kills_and_relaunches(self):
        self.w.tick(obs(5, size=0))
        self.assertEqual(self.w.tick(obs(301, size=0)), Action.KILL)
        self.assertEqual(self.w.state, State.RESTARTING)
        self.assertEqual(self.w.tick(obs(305, alive=False)), Action.WAIT)   # restart delay
        self.assertEqual(self.w.tick(obs(312, alive=False)), Action.LAUNCH)

    def test_stall_after_progress(self):
        self.w.tick(obs(5, size=0))
        self.w.tick(obs(100, size=40))                 # first progress at 100
        self.assertEqual(self.w.tick(obs(210, size=40)), Action.WAIT)
        self.assertEqual(self.w.tick(obs(221, size=40)), Action.KILL)
        self.assertIn("hang", self.w.reason)

    def test_crash_needs_two_dead_checks_then_waits_the_delay(self):
        self.w.tick(obs(5, size=0))
        self.w.tick(obs(50, size=10))
        self.assertEqual(self.w.tick(obs(55, size=10, alive=False)), Action.WAIT)   # one miss is noise
        self.assertEqual(self.w.tick(obs(60, size=10, alive=False)), Action.WAIT)   # crash: restart scheduled
        self.assertEqual(self.w.state, State.RESTARTING)
        self.assertEqual(self.w.tick(obs(65, size=10, alive=False)), Action.WAIT)
        self.assertEqual(self.w.tick(obs(71, size=10, alive=False)), Action.LAUNCH)
        self.assertEqual(self.w.restarts, 1)

    def test_finishing_and_closing_in_one_tick_is_not_a_crash(self):
        self.w.tick(obs(5, size=0))
        self.w.tick(obs(50, size=10))
        self.assertEqual(self.w.tick(obs(55, exists=False, alive=False)), Action.FINISHED)
        self.assertEqual(self.w.restarts, 0)

    def test_game_left_open_after_finishing_is_closed(self):
        self.w.tick(obs(5, size=0))
        self.assertEqual(self.w.tick(obs(50, exists=False, alive=True)), Action.WAIT)
        self.assertEqual(self.w.tick(obs(81, exists=False, alive=True)), Action.KILL)
        self.assertEqual(self.w.tick(obs(86, exists=False, alive=False)), Action.FINISHED)

    def test_gives_up_after_max_restarts(self):
        t = 0
        for _ in range(2):
            self.w.tick(obs(t + 5, size=0))
            self.w.tick(obs(t + 10, alive=False))
            self.w.tick(obs(t + 15, alive=False))
            self.assertEqual(self.w.tick(obs(t + 30, alive=False)), Action.LAUNCH)
            t += 30
        self.w.tick(obs(t + 5, size=0))
        self.w.tick(obs(t + 10, alive=False))
        self.assertEqual(self.w.tick(obs(t + 15, alive=False)), Action.FAILED)
        self.assertEqual(self.w.state, State.FAILED)

    def test_game_that_never_appears_is_retried(self):
        self.assertEqual(self.w.tick(obs(30, alive=False)), Action.WAIT)
        self.assertEqual(self.w.tick(obs(61, alive=False)), Action.WAIT)
        self.assertEqual(self.w.state, State.RESTARTING)

    def test_resumed_trigger_size_is_not_progress(self):
        # Resuming: the trigger already lists cells. Its first size is a baseline, not progress,
        # so the boot limit (not the shorter stall limit) still applies.
        self.w.tick(obs(5, size=5000))
        self.assertEqual(self.w.tick(obs(200, size=5000)), Action.WAIT)
        self.assertIsNone(self.w.last_progress_at)


if __name__ == "__main__":
    unittest.main()
