"use strict";
/** The .cgid files NGIO writes, one per cell, and the seasonal names they are given afterwards. */
const fs = require("fs");
const path = require("path");
const { SEASONAL_SUFFIXES } = require("./seasons");

function isPlain(name) {
  const low = name.toLowerCase();
  return low.endsWith(".cgid") && !SEASONAL_SUFFIXES.some((s) => low.endsWith(`${s.toLowerCase()}.cgid`));
}

function list(dir) {
  try {
    return fs.readdirSync(dir).filter((n) => n.toLowerCase().endsWith(".cgid"));
  } catch {
    return [];
  }
}

/**
 * Move the cache files NGIO created this season (names not present in `before`) from the game's
 * Data/Grass into `dst`, adding the season suffix. Files that were already there belong to other
 * mods (Vortex hardlinks) and are never touched; so are new names `isForeign` says another mod deployed.
 * @param {(nameLower: string) => boolean} [isForeign]
 */
function moveNew(srcDir, before, dst, suffix, isForeign = () => false) {
  fs.mkdirSync(dst, { recursive: true });
  let moved = 0;
  for (const name of list(srcDir)) {
    if (before.has(name.toLowerCase()) || !isPlain(name) || isForeign(name.toLowerCase())) continue;
    const target = suffix ? name.slice(0, -".cgid".length) + suffix + ".cgid" : name;
    const from = path.join(srcDir, name);
    const to = path.join(dst, target);
    try {
      fs.renameSync(from, to);
    } catch (e) {
      if (e.code !== "EXDEV") throw e;          // staging on another drive: copy, then remove
      fs.copyFileSync(from, to);
      fs.unlinkSync(from);
    }
    moved += 1;
  }
  return moved;
}

/** DynDOLOD's grass LOD reads plain names: copy Name<suffix>.cgid to Name.cgid. */
function copyWithoutSuffix(srcDir, suffix, dstDir) {
  fs.mkdirSync(dstDir, { recursive: true });
  const tail = `${suffix}.cgid`.toLowerCase();
  let copied = 0;
  for (const name of list(srcDir)) {
    if (!name.toLowerCase().endsWith(tail)) continue;
    fs.copyFileSync(path.join(srcDir, name), path.join(dstDir, name.slice(0, -tail.length) + ".cgid"));
    copied += 1;
  }
  return copied;
}

module.exports = { isPlain, list, moveNew, copyWithoutSuffix };
