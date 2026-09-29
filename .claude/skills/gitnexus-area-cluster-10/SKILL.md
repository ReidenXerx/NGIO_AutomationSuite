---
name: gitnexus-area-cluster-10
description: "Skill for the Cluster_10 area of NGIO_AutomationSuite. 11 symbols across 3 files."
---

# Cluster_10

11 symbols | 3 files | Cohesion: 53%

## When to Use

- Working with code in `src/`
- Understanding how check_for_previous_session, create_automation_config_from_cache, handle_grass_generation work
- Modifying cluster_10-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/state_manager.py` | check_for_interruption, clear_state, has_saved_state, load_state, mark_interrupted |
| `ngio_automation_runner.py` | _apply_cli_overrides, check_for_previous_session, create_automation_config_from_cache, handle_grass_generation |
| `src/utils/config_cache.py` | get_paths, get_preferences |

## Entry Points

Start here when exploring this area:

- **`check_for_previous_session`** (Function) — `ngio_automation_runner.py:598`
- **`create_automation_config_from_cache`** (Function) — `ngio_automation_runner.py:542`
- **`handle_grass_generation`** (Function) — `ngio_automation_runner.py:234`
- **`get_paths`** (Method) — `src/utils/config_cache.py:517`
- **`get_preferences`** (Method) — `src/utils/config_cache.py:521`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `check_for_previous_session` | Function | `ngio_automation_runner.py` | 598 |
| `create_automation_config_from_cache` | Function | `ngio_automation_runner.py` | 542 |
| `handle_grass_generation` | Function | `ngio_automation_runner.py` | 234 |
| `get_paths` | Method | `src/utils/config_cache.py` | 517 |
| `get_preferences` | Method | `src/utils/config_cache.py` | 521 |
| `check_for_interruption` | Method | `src/utils/state_manager.py` | 199 |
| `clear_state` | Method | `src/utils/state_manager.py` | 177 |
| `has_saved_state` | Method | `src/utils/state_manager.py` | 168 |
| `load_state` | Method | `src/utils/state_manager.py` | 121 |
| `mark_interrupted` | Method | `src/utils/state_manager.py` | 228 |
| `_apply_cli_overrides` | Function | `ngio_automation_runner.py` | 141 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_full_automation → Warning` | cross_community | 4 |
| `Run_full_automation → Info` | cross_community | 4 |
| `Run_full_automation → Debug` | cross_community | 4 |
| `Handle_grass_generation → Is_complete` | cross_community | 3 |
| `Handle_grass_generation → Validate_paths` | cross_community | 3 |
| `Check_for_previous_session → Warning` | cross_community | 3 |
| `Check_for_previous_session → Info` | cross_community | 3 |
| `Check_for_previous_session → Debug` | cross_community | 3 |
| `Handle_grass_generation → Info` | cross_community | 3 |
| `Mark_interrupted → Warning` | cross_community | 3 |

## How to Explore

1. `context({name: "check_for_previous_session"})` — see callers and callees
2. `query({search_query: "cluster_10"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
