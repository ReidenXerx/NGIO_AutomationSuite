---
name: gitnexus-area-cluster-74
description: "Skill for the Cluster_74 area of NGIO_AutomationSuite. 11 symbols across 2 files."
---

# Cluster_74

11 symbols | 2 files | Cohesion: 54%

## When to Use

- Working with code in `src/`
- Understanding how run_full_automation, create_state_from_config, format_state_summary work
- Modifying cluster_74-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/core/automation_suite.py` | _backup_configurations, _get_season_by_name, _resume_from_state, _setup_and_validate, _should_resume_from_state (+2) |
| `src/utils/state_manager.py` | create_state_from_config, format_state_summary, get_resumable_seasons, save_state |

## Entry Points

Start here when exploring this area:

- **`run_full_automation`** (Method) — `src/core/automation_suite.py:125`
- **`create_state_from_config`** (Method) — `src/utils/state_manager.py:269`
- **`format_state_summary`** (Method) — `src/utils/state_manager.py:292`
- **`get_resumable_seasons`** (Method) — `src/utils/state_manager.py:242`
- **`save_state`** (Method) — `src/utils/state_manager.py:82`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `run_full_automation` | Method | `src/core/automation_suite.py` | 125 |
| `create_state_from_config` | Method | `src/utils/state_manager.py` | 269 |
| `format_state_summary` | Method | `src/utils/state_manager.py` | 292 |
| `get_resumable_seasons` | Method | `src/utils/state_manager.py` | 242 |
| `save_state` | Method | `src/utils/state_manager.py` | 82 |
| `_backup_configurations` | Method | `src/core/automation_suite.py` | 276 |
| `_get_season_by_name` | Method | `src/core/automation_suite.py` | 732 |
| `_resume_from_state` | Method | `src/core/automation_suite.py` | 693 |
| `_setup_and_validate` | Method | `src/core/automation_suite.py` | 238 |
| `_should_resume_from_state` | Method | `src/core/automation_suite.py` | 672 |
| `_update_state_after_season` | Method | `src/core/automation_suite.py` | 747 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_full_automation → Warning` | cross_community | 4 |
| `Run_full_automation → Info` | cross_community | 4 |
| `Run_full_automation → Debug` | cross_community | 4 |
| `Mark_interrupted → Error` | cross_community | 3 |

## How to Explore

1. `context({name: "run_full_automation"})` — see callers and callees
2. `query({search_query: "cluster_74"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
