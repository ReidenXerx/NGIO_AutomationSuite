"use strict";
// Build the Vortex extension archive: node vortex/package.js -> vortex/dist/NGIO_Grass_Cache_Vortex_<version>.zip
// Vortex installs it from Extensions > "Install from file"; info.json and index.js sit at the archive root.
// The core tests run first; a red suite builds nothing.
const { execFileSync, spawnSync } = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const here = __dirname;
const tests = spawnSync(process.execPath, ["--test", path.join(here, "test", "core.test.js")], { stdio: "inherit" });
if (tests.status !== 0) process.exit(1);

const { version } = JSON.parse(fs.readFileSync(path.join(here, "info.json"), "utf8"));
const out = path.join(here, "dist", `NGIO_Grass_Cache_Vortex_${version}.zip`);
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.rmSync(out, { force: true });
const files = ["info.json", "index.js", "README.md", "src"];
// PowerShell's Compress-Archive keeps the relative layout when run from this folder.
execFileSync("powershell.exe", ["-NoProfile", "-Command",
  `Compress-Archive -Path ${files.map((f) => `'${f}'`).join(",")} -DestinationPath '${out}'`], { cwd: here, stdio: "inherit" });
console.log(out);
console.log("sha256", crypto.createHash("sha256").update(fs.readFileSync(out)).digest("hex"));
