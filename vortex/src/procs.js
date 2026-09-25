"use strict";
/**
 * Find and stop the game process. Node has no process list, so this asks Windows through CIM.
 * The game is matched by its FULL executable path, so another Skyrim install is never touched.
 */
const { execFile } = require("child_process");
const path = require("path");

function powershell(script, timeoutMs = 15000) {
  return new Promise((resolve, reject) => {
    execFile("powershell.exe", ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
      { windowsHide: true, timeout: timeoutMs }, (err, stdout) => (err ? reject(err) : resolve(String(stdout))));
  });
}

const norm = (p) => path.normalize(p).toLowerCase();

/** PIDs of processes running exactly this executable. */
async function findGame(exePath) {
  const name = path.basename(exePath).replace(/'/g, "''");
  const out = await powershell(
    `Get-CimInstance Win32_Process -Filter "Name='${name}'" | ForEach-Object { "$($_.ProcessId)|$($_.ExecutablePath)" }`);
  const want = norm(exePath);
  return out.split(/\r?\n/).map((l) => l.trim()).filter(Boolean)
    .map((l) => l.split("|"))
    .filter(([, p]) => p && norm(p) === want)
    .map(([pid]) => Number(pid))
    .filter((pid) => pid > 0);
}

function terminate(pid) {
  try {
    process.kill(pid);
    return true;
  } catch {
    return false;
  }
}

/** Pagefile size in bytes (sum of all page files), or null when Windows does not say. */
async function pagefileBytes() {
  try {
    const out = await powershell("(Get-CimInstance Win32_PageFileUsage | Measure-Object AllocatedBaseSize -Sum).Sum");
    const mb = Number(out.trim());
    return Number.isFinite(mb) ? mb * 1024 * 1024 : null;
  } catch {
    return null;
  }
}

/** Does this PID still exist? Signal 0 checks without sending anything, and spawns nothing. */
function isAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (e) {
    return e.code === "EPERM";      // exists, but belongs to someone we may not signal
  }
}

module.exports = { findGame, isAlive, terminate, pagefileBytes };
