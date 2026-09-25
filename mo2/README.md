# NGIO Grass Cache for Mod Organizer 2 (beta)

Generates the [No Grass In Objects](https://www.nexusmods.com/skyrimspecialedition/mods/42161) grass cache for
every season in one unattended run, from inside MO2. There's no exe and no Python to install: MO2 runs it with its
own Python.

This replaces the standalone exe for MO2 users. A Vortex version comes next.

## What it does

1. **Checks your setup first**: SKSE, NGIO, Seasons of Skyrim, Grass Cache Helper NG, pagefile size, and any grass
   cache that is already visible, since NGIO skips cells that already have a cache file.
2. **Puts the run's settings in a temporary mod**: "NGIO Grass - Run Settings" goes at the top of your mod list.
   It holds copies of your `GrassControl.ini` and `po3_SeasonsOfSkyrim.ini`, with only these changes:
   - `use-grass-cache = true` and `only-load-from-cache = true` (NGIO's own precache recipe).
   - `Season Type` set to the season being generated.
   **Your own INI files are never edited.** The temporary mod is removed when the run ends.
3. **Starts Skyrim through MO2** with `skse64_loader.exe`, so the game sees your whole mod list. Everything NGIO
   writes goes into that season's own mod, e.g. `NGIO Grass Cache - Winter`, not into Overwrite.
4. **Watches the game**:
   - A crash is noticed within about 10 seconds, and the game is relaunched after a pause you set.
   - If no new cell is finished for the time you set, the game counts as hung and is restarted.
   - A slow boot is not a hang: until the first cell, a separate, longer wait applies.
   - NGIO resumes from where it stopped, so a restart continues the season.
5. **Names the files for the season** (`*.WIN.cgid`, `*.SPR.cgid`, `*.SUM.cgid`, `*.AUT.cgid`) and moves on to the
   next season. At the end the season mods are enabled.

Optional: a copy of one season without its suffix, for DynDOLOD grass LOD (`NGIO Grass Cache - DynDOLOD LOD`). It is
left disabled; enable it only while you run TexGen and DynDOLOD.

## Install

1. Close MO2.
2. Extract the archive into MO2's `plugins` folder, so you get `...\Mod Organizer 2\plugins\ngio_grass\__init__.py`.
3. Start MO2 and open **Tools → NGIO Grass Cache**. The tool only shows up for Skyrim Special Edition and VR.

Requires MO2 2.5 or later (it uses the PyQt6 that MO2 2.5 ships).

## Using it

- Pick the seasons (or **No seasons** if you don't use Seasons of Skyrim), fix whatever the checklist marks red,
  and press **Start**. You can close the window and it keeps running; reopen it from the Tools menu.
- **Stop** closes the game and keeps the progress. `PrecacheGrass.txt` is moved out of the game folder, so you
  can play normally in the meantime, and **Resume unfinished run** puts it back and continues.
- The log is shown in the window and saved to MO2's plugin data folder: `plugins\data\ngio_grass\run.log`.

## Good to know

- **Pagefile:** NGIO's precache can use more memory than your RAM. A pagefile of 20 GB or more prevents most
  out-of-memory crashes.
- **Trainwreck:** its crash popup keeps a dead game "open", so the plugin only notices once the hang timer runs out.
- **Root Builder:** NGIO's page says to add `PrecacheGrass.txt` as a Root Builder exclusion.

## Reporting a problem

Attach `run.log` and say which step it stopped at. Screenshots of the checklist help too.
