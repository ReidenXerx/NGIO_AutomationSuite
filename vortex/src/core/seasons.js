"use strict";
/**
 * `typeNumber` is `Season Type` in po3_SeasonsOfSkyrim.ini (0 disabled, 1-4 pinned, 5 seasonal).
 * `suffix` sits between the cell name and `.cgid` for the seasonal cache loader.
 * `modId` is the folder name of the season's mod in Vortex's staging folder.
 */
const make = (key, name, typeNumber, suffix) => ({
  key,
  name,
  typeNumber,
  suffix,
  modName: suffix ? `NGIO Grass Cache - ${name}` : "NGIO Grass Cache",
  modId: suffix ? `ngio-grass-cache-${key}` : "ngio-grass-cache",
});

const WINTER = make("winter", "Winter", 1, ".WIN");
const SPRING = make("spring", "Spring", 2, ".SPR");
const SUMMER = make("summer", "Summer", 3, ".SUM");
const AUTUMN = make("autumn", "Autumn", 4, ".AUT");
const NO_SEASONS = make("none", "No seasons", 0, "");

const FOUR = [WINTER, SPRING, SUMMER, AUTUMN];
const ALL = [...FOUR, NO_SEASONS];
const BY_KEY = Object.fromEntries(ALL.map((s) => [s.key, s]));
const SEASONAL_SUFFIXES = FOUR.map((s) => s.suffix);

const RUN_SETTINGS = { modId: "ngio-grass-run-settings", modName: "NGIO Grass - Run Settings" };
const LOD = { modId: "ngio-grass-cache-dyndolod-lod", modName: "NGIO Grass Cache - DynDOLOD LOD" };

module.exports = { WINTER, SPRING, SUMMER, AUTUMN, NO_SEASONS, FOUR, ALL, BY_KEY, SEASONAL_SUFFIXES, RUN_SETTINGS, LOD };
