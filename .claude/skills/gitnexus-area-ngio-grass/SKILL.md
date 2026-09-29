---
name: gitnexus-area-ngio-grass
description: "Skill for the Ngio_grass area of NGIO_AutomationSuite. 66 symbols across 8 files."
---

# Ngio_grass

66 symbols | 8 files | Cohesion: 78%

## When to Use

- Working with code in `mo2/`
- Understanding how copy_without_suffix, count, terminate work
- Modifying ngio_grass-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `mo2/ngio_grass/controller.py` | _abort, _active, _cleanup, _ensure_mod, _finish (+30) |
| `mo2/ngio_grass/ui.py` | __init__, _apply_fix, _clear_checks, _config, _fill_table (+9) |
| `mo2/ngio_grass/winproc.py` | terminate, memory, _image_path, _norm, find_game (+1) |
| `mo2/ngio_grass/core/watchdog.py` | _restart, start, tick |
| `mo2/ngio_grass/core/cgid.py` | copy_without_suffix, count |
| `mo2/tests/test_core.py` | test_lod_copy_strips_the_suffix, test_bom_and_season_type_round_trip |
| `mo2/ngio_grass/plugin.py` | display, name |
| `mo2/ngio_grass/core/ini.py` | from_bytes, to_bytes |

## Entry Points

Start here when exploring this area:

- **`copy_without_suffix`** (Function) — `mo2/ngio_grass/core/cgid.py:35`
- **`count`** (Function) — `mo2/ngio_grass/core/cgid.py:15`
- **`terminate`** (Function) — `mo2/ngio_grass/winproc.py:102`
- **`memory`** (Function) — `mo2/ngio_grass/winproc.py:112`
- **`find_game`** (Function) — `mo2/ngio_grass/winproc.py:84`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `copy_without_suffix` | Function | `mo2/ngio_grass/core/cgid.py` | 35 |
| `count` | Function | `mo2/ngio_grass/core/cgid.py` | 15 |
| `terminate` | Function | `mo2/ngio_grass/winproc.py` | 102 |
| `memory` | Function | `mo2/ngio_grass/winproc.py` | 112 |
| `find_game` | Function | `mo2/ngio_grass/winproc.py` | 84 |
| `pids_named` | Function | `mo2/ngio_grass/winproc.py` | 65 |
| `mod_path` | Method | `mo2/ngio_grass/controller.py` | 127 |
| `parked` | Method | `mo2/ngio_grass/controller.py` | 100 |
| `start` | Method | `mo2/ngio_grass/controller.py` | 279 |
| `state_file` | Method | `mo2/ngio_grass/controller.py` | 89 |
| `stop` | Method | `mo2/ngio_grass/controller.py` | 489 |
| `trigger` | Method | `mo2/ngio_grass/controller.py` | 86 |
| `unfinished` | Method | `mo2/ngio_grass/controller.py` | 514 |
| `start` | Method | `mo2/ngio_grass/core/watchdog.py` | 69 |
| `tick` | Method | `mo2/ngio_grass/core/watchdog.py` | 87 |
| `test_lod_copy_strips_the_suffix` | Method | `mo2/tests/test_core.py` | 108 |
| `tick` | Method | `mo2/ngio_grass/controller.py` | 383 |
| `display` | Method | `mo2/ngio_grass/plugin.py` | 61 |
| `name` | Method | `mo2/ngio_grass/plugin.py` | 29 |
| `refresh_checks` | Method | `mo2/ngio_grass/ui.py` | 163 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `_tick → Game` | cross_community | 7 |
| `Display → Game` | cross_community | 6 |
| `Start → Mod_path` | cross_community | 5 |
| `Start → _section_span` | cross_community | 5 |
| `_tick → _image_path` | cross_community | 5 |
| `_tick → _norm` | cross_community | 5 |
| `_tick → Pids_named` | cross_community | 5 |
| `_tick → Mod_path` | cross_community | 5 |
| `_next_season → Game` | cross_community | 5 |
| `Start → Game` | cross_community | 5 |

## How to Explore

1. `context({name: "copy_without_suffix"})` — see callers and callees
2. `query({search_query: "ngio_grass"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
