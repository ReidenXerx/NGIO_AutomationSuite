"use strict";
// node --test vortex/test — the same cases as mo2/tests/test_core.py, so both front-ends keep one set of rules.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");

const { IniText } = require("../src/core/ini");
const cgid = require("../src/core/cgid");
const { AUTUMN, WINTER, NO_SEASONS } = require("../src/core/seasons");
const { Action, State, SeasonWatch } = require("../src/core/watchdog");

const GRASS_CONTROL =
  "[Debug]\r\n; Set true to write a debug log\r\ndebug-log-enable = false\r\n\r\n" +
  "[RayCastConfig]\r\nray-cast-ignore-forms = \r\n" +
  "ray-cast-texture-forms = 112D5520:Northern Roads.esp;112D5521:Northern Roads.esp\r\n\r\n" +
  "[GrassConfig]\r\n;Set true if you want to enable extended grass distance mode.\r\n" +
  "use-grass-cache = false\r\nextend-grass-distance = true\r\nonly-load-from-cache = false\r\n\r\n" +
  "[Settings]\r\nusegrasscache = True\r\n";
const SEASONS = "﻿[Settings]\n\n;5 - seasonal\nSeason Type = 4\n\n;January\nMorning Star = 1\n";

test("ini: reads hyphenated keys case-insensitively", () => {
  const ini = new IniText(GRASS_CONTROL);
  assert.equal(ini.get("GrassConfig", "Use-grass-cache"), "false");
  assert.equal(ini.get("grassconfig", "extend-grass-distance"), "true");
  assert.equal(ini.get("GrassConfig", "usegrasscache"), null);
});

test("ini: set changes only that line", () => {
  const ini = new IniText(GRASS_CONTROL);
  assert.ok(ini.set("GrassConfig", "Use-grass-cache", "true"));
  assert.ok(ini.set("GrassConfig", "Only-load-from-cache", "true"));
  const out = ini.toText();
  assert.ok(out.includes("use-grass-cache = true\r\n"));
  assert.equal(
    out.replace("use-grass-cache = true", "use-grass-cache = false").replace("only-load-from-cache = true", "only-load-from-cache = false"),
    GRASS_CONTROL,
  );
});

test("ini: same value is not a change", () => {
  assert.equal(new IniText(GRASS_CONTROL).set("GrassConfig", "extend-grass-distance", "true"), false);
});

test("ini: missing key goes before the blank separator", () => {
  const ini = new IniText(GRASS_CONTROL);
  ini.set("GrassConfig", "max-failures", "2");
  const lines = ini.toText().split("\r\n");
  const at = lines.indexOf("max-failures = 2");
  assert.equal(lines[at - 1], "only-load-from-cache = false");
  assert.equal(lines[at + 1], "");
});

test("ini: missing section is appended", () => {
  const ini = new IniText("[A]\nx = 1\n");
  ini.set("B", "y", "2");
  assert.equal(ini.toText(), "[A]\nx = 1\n\n[B]\ny = 2\n");
});

test("ini: BOM and Season Type round trip", () => {
  const ini = IniText.fromBuffer(Buffer.from(SEASONS, "utf8"));
  assert.equal(ini.get("Settings", "Season Type"), "4");
  ini.set("Settings", "Season Type", "1");
  const buf = ini.toBuffer();
  assert.deepEqual([...buf.subarray(0, 3)], [0xef, 0xbb, 0xbf]);
  assert.equal(buf.toString("utf8"), SEASONS.replace("Season Type = 4", "Season Type = 1"));
});

test("ini: value with an equals sign", () => {
  assert.equal(new IniText("[S]\nonly-pregenerate-world-spaces = Tamriel;A=B\n").get("S", "only-pregenerate-world-spaces"), "Tamriel;A=B");
});

function tmpGrass(names) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ngio-"));
  for (const n of names) fs.writeFileSync(path.join(dir, n), n);
  return dir;
}

test("cgid: moves only the files new this season, with the suffix", () => {
  const src = tmpGrass(["Old_0_0.cgid", "Tamriel_0_0.cgid", "Tamriel_0_1.cgid", "Keep_1_1.WIN.cgid", "notes.txt"]);
  const before = new Set(["old_0_0.cgid", "keep_1_1.win.cgid"]);
  const dst = path.join(src, "out");
  assert.equal(cgid.moveNew(src, before, dst, AUTUMN.suffix), 2);
  assert.deepEqual(fs.readdirSync(dst).sort(), ["Tamriel_0_0.AUT.cgid", "Tamriel_0_1.AUT.cgid"]);
  assert.ok(fs.existsSync(path.join(src, "Old_0_0.cgid")));     // someone else's file stays put
});

test("cgid: a file another mod deployed mid-run is not moved", () => {
  const src = tmpGrass(["Mine_0_0.cgid", "Theirs_0_1.cgid"]);
  const dst = path.join(src, "out");
  assert.equal(cgid.moveNew(src, new Set(), dst, AUTUMN.suffix, (n) => n === "theirs_0_1.cgid"), 1);
  assert.deepEqual(fs.readdirSync(dst), ["Mine_0_0.AUT.cgid"]);
  assert.ok(fs.existsSync(path.join(src, "Theirs_0_1.cgid")));
});

test("cgid: no seasons keeps plain names", () => {
  const src = tmpGrass(["A_0_0.cgid"]);
  const dst = path.join(src, "out");
  assert.equal(cgid.moveNew(src, new Set(), dst, NO_SEASONS.suffix), 1);
  assert.deepEqual(fs.readdirSync(dst), ["A_0_0.cgid"]);
});

test("cgid: LOD copy strips the suffix", () => {
  const src = tmpGrass(["Old_1_1.WIN.cgid", "B_0_0.SUM.cgid"]);
  const dst = path.join(src, "lod");
  assert.equal(cgid.copyWithoutSuffix(src, WINTER.suffix, dst), 1);
  assert.deepEqual(fs.readdirSync(dst), ["Old_1_1.cgid"]);
});

test("cgid: isPlain", () => {
  assert.ok(cgid.isPlain("A_1_2.cgid"));
  assert.ok(!cgid.isPlain("A_1_2.SUM.cgid"));
  assert.ok(!cgid.isPlain("A_1_2.txt"));
});

const CFG = { bootSeconds: 300, stallSeconds: 120, restartDelaySeconds: 10, maxRestarts: 2, appearSeconds: 60, exitGraceSeconds: 30 };
const obs = (now, { exists = true, size = 0, alive = true } = {}) => ({ now, triggerExists: exists, triggerSize: size, gameAlive: alive });
function started() {
  const w = new SeasonWatch(CFG);
  assert.equal(w.start(0), Action.LAUNCH);
  return w;
}

test("watchdog: a slow boot is not a hang", () => {
  const w = started();
  assert.equal(w.tick(obs(5)), Action.WAIT);
  assert.equal(w.tick(obs(240)), Action.WAIT);
  assert.equal(w.state, State.RUNNING);
  assert.equal(w.restarts, 0);
});

test("watchdog: boot limit kills and relaunches", () => {
  const w = started();
  w.tick(obs(5));
  assert.equal(w.tick(obs(301)), Action.KILL);
  assert.equal(w.tick(obs(305, { alive: false })), Action.WAIT);
  assert.equal(w.tick(obs(312, { alive: false })), Action.LAUNCH);
});

test("watchdog: stall after progress", () => {
  const w = started();
  w.tick(obs(5));
  w.tick(obs(100, { size: 40 }));
  assert.equal(w.tick(obs(210, { size: 40 })), Action.WAIT);
  assert.equal(w.tick(obs(221, { size: 40 })), Action.KILL);
  assert.match(w.reason, /hang/);
});

test("watchdog: a crash needs two dead checks, then waits the delay", () => {
  const w = started();
  w.tick(obs(5));
  w.tick(obs(50, { size: 10 }));
  assert.equal(w.tick(obs(55, { size: 10, alive: false })), Action.WAIT);
  assert.equal(w.tick(obs(60, { size: 10, alive: false })), Action.WAIT);
  assert.equal(w.state, State.RESTARTING);
  assert.equal(w.tick(obs(65, { size: 10, alive: false })), Action.WAIT);
  assert.equal(w.tick(obs(71, { size: 10, alive: false })), Action.LAUNCH);
  assert.equal(w.restarts, 1);
});

test("watchdog: finishing and closing in one tick is not a crash", () => {
  const w = started();
  w.tick(obs(5));
  w.tick(obs(50, { size: 10 }));
  assert.equal(w.tick(obs(55, { exists: false, alive: false })), Action.FINISHED);
  assert.equal(w.restarts, 0);
});

test("watchdog: a game left open after finishing is closed", () => {
  const w = started();
  w.tick(obs(5));
  assert.equal(w.tick(obs(50, { exists: false })), Action.WAIT);
  assert.equal(w.tick(obs(81, { exists: false })), Action.KILL);
  assert.equal(w.tick(obs(86, { exists: false, alive: false })), Action.FINISHED);
});

test("watchdog: gives up after max restarts", () => {
  const w = started();
  let t = 0;
  for (let i = 0; i < 2; i++) {
    w.tick(obs(t + 5));
    w.tick(obs(t + 10, { alive: false }));
    w.tick(obs(t + 15, { alive: false }));
    assert.equal(w.tick(obs(t + 30, { alive: false })), Action.LAUNCH);
    t += 30;
  }
  w.tick(obs(t + 5));
  w.tick(obs(t + 10, { alive: false }));
  assert.equal(w.tick(obs(t + 15, { alive: false })), Action.FAILED);
  assert.equal(w.state, State.FAILED);
});

test("watchdog: a game that never appears is retried", () => {
  const w = started();
  assert.equal(w.tick(obs(30, { alive: false })), Action.WAIT);
  assert.equal(w.tick(obs(61, { alive: false })), Action.WAIT);
  assert.equal(w.state, State.RESTARTING);
});

test("watchdog: a resumed trigger's size is not progress", () => {
  const w = started();
  w.tick(obs(5, { size: 5000 }));
  assert.equal(w.tick(obs(200, { size: 5000 })), Action.WAIT);
  assert.equal(w.lastProgressAt, null);
});
