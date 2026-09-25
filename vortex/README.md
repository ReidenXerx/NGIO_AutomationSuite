# NGIO Grass Cache for Vortex (beta)

Generates the [No Grass In Objects](https://www.nexusmods.com/skyrimspecialedition/mods/42161) grass cache for
every season in one unattended run, from a page inside Vortex. There's no exe and no Python to install. The MO2
version lives in `../mo2` and follows the same rules.

## What it does

1. **Checks your setup first**: SKSE, NGIO, Seasons of Skyrim, Grass Cache Helper NG, pagefile size, and any grass
   cache already in `Data/Grass`, since NGIO skips cells that already have a cache file. If another mod provides
   those files, one click disables it and deploys.
2. **Deploys the run's settings as a temporary mod**: "NGIO Grass - Run Settings", with rules so it wins over the
   mods that provide `GrassControl.ini` and `po3_SeasonsOfSkyrim.ini`. It changes only these:
   - `use-grass-cache = true` and `only-load-from-cache = true` (NGIO's own precache recipe).
   - `Season Type` set to the season being generated.
   **Your own mods are never edited.** The temporary mod is removed, and deployed away, when the run ends.
3. **Starts Skyrim with `skse64_loader.exe`** and tells Vortex a tool is running, so Vortex doesn't deploy under
   the live game.
4. **Watches the game**:
   - A crash is noticed within about 10 seconds, and the game is relaunched after a pause you set.
   - If no new cell is finished for the time you set, the game counts as hung and is restarted.
   - A slow boot is not a hang: until the first cell, a separate, longer wait applies.
5. **After each season, moves exactly the cache files that season created** out of `Data/Grass` into that
   season's own mod (`NGIO Grass Cache - Winter`, and so on), renamed for the season. Cache files that were already
   there belong to other mods and are not touched. At the end the season mods are enabled and deployed.

Optional: a copy of one season without its suffix, for DynDOLOD grass LOD. It is left disabled; enable it only
while you run TexGen and DynDOLOD.

## Install

In Vortex: **Extensions → Install From File**, pick the archive, then restart Vortex. A page called
**NGIO Grass Cache** appears when Skyrim Special Edition (or VR) is the active game.

## Using it

- Pick the seasons (or **No seasons**), fix whatever the checklist marks red, and press **Start**.
- **Stop** closes the game and keeps the progress. `PrecacheGrass.txt` is moved out of the game folder, so you
  can play normally in the meantime, and **Resume unfinished run** puts it back and continues. Closing Vortex
  mid-run does the same.
- Each season costs no extra deploys with hardlink deployment. With other deployment methods, each season switch
  takes one short deploy.
- The log is on the page and saved to `%APPDATA%\Vortex\ngio-grass\run.log`.

## Good to know

- **Pagefile:** NGIO's precache can use more memory than your RAM. A pagefile of 20 GB or more prevents most
  out-of-memory crashes.
- **Trainwreck:** its crash popup keeps a dead game "open", so the tool only notices once the hang timer runs out.

## Reporting a problem

Attach `run.log` and say which step it stopped at. Screenshots of the checklist help too.
