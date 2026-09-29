---
name: gitnexus-area-cluster-55
description: "Skill for the Cluster_55 area of NGIO_AutomationSuite. 27 symbols across 10 files."
---

# Cluster_55

27 symbols | 10 files | Cohesion: 36%

## When to Use

- Working with code in `src/`
- Understanding how create_custom_profile_interactive, cleanup_output_directory, cleanup_backups work
- Modifying cluster_55-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/logger.py` | __init__, _setup_console_handler, _setup_file_handler, file_operation, info (+5) |
| `src/core/config_manager.py` | __init__, _detect_skyrim_path, _initialize_config_paths, cleanup_backups |
| `src/utils/notifications.py` | _running_under_wine_or_proton, __init__ |
| `src/core/archive_creator.py` | __init__, cleanup_output_directory |
| `src/core/file_processor.py` | __init__, cleanup_temporary_files |
| `src/core/game_manager.py` | __init__, _find_skyrim_executable |
| `src/utils/config_cache.py` | __init__, _auto_detect_config_paths |
| `src/utils/grass_profiles.py` | create_custom_profile_interactive |
| `src/core/progress_monitor.py` | save_console_log |
| `src/utils/task_scheduler.py` | print_setup_guide |

## Entry Points

Start here when exploring this area:

- **`create_custom_profile_interactive`** (Function) — `src/utils/grass_profiles.py:132`
- **`cleanup_output_directory`** (Method) — `src/core/archive_creator.py:837`
- **`cleanup_backups`** (Method) — `src/core/config_manager.py:588`
- **`cleanup_temporary_files`** (Method) — `src/core/file_processor.py:426`
- **`save_console_log`** (Method) — `src/core/progress_monitor.py:496`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `create_custom_profile_interactive` | Function | `src/utils/grass_profiles.py` | 132 |
| `cleanup_output_directory` | Method | `src/core/archive_creator.py` | 837 |
| `cleanup_backups` | Method | `src/core/config_manager.py` | 588 |
| `cleanup_temporary_files` | Method | `src/core/file_processor.py` | 426 |
| `save_console_log` | Method | `src/core/progress_monitor.py` | 496 |
| `file_operation` | Method | `src/utils/logger.py` | 176 |
| `info` | Method | `src/utils/logger.py` | 122 |
| `mod_validation` | Method | `src/utils/logger.py` | 265 |
| `retry_attempt` | Method | `src/utils/logger.py` | 172 |
| `season_complete` | Method | `src/utils/logger.py` | 164 |
| `user_input` | Method | `src/utils/logger.py` | 301 |
| `user_prompt` | Method | `src/utils/logger.py` | 297 |
| `print_setup_guide` | Method | `src/utils/task_scheduler.py` | 326 |
| `_running_under_wine_or_proton` | Function | `src/utils/notifications.py` | 43 |
| `__init__` | Method | `src/core/archive_creator.py` | 42 |
| `__init__` | Method | `src/core/config_manager.py` | 28 |
| `_detect_skyrim_path` | Method | `src/core/config_manager.py` | 69 |
| `_initialize_config_paths` | Method | `src/core/config_manager.py` | 40 |
| `__init__` | Method | `src/core/file_processor.py` | 55 |
| `__init__` | Method | `src/core/game_manager.py` | 38 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Handle_configuration → Info` | cross_community | 4 |
| `Main → Info` | cross_community | 4 |
| `Main → Info` | cross_community | 4 |
| `Load_config → Info` | cross_community | 4 |
| `Main → Info` | cross_community | 4 |
| `Run_full_automation → Info` | cross_community | 4 |
| `Create_mod_folder_structure → Info` | cross_community | 4 |
| `Cleanup_processes → Info` | cross_community | 4 |
| `Check_for_previous_session → Info` | cross_community | 3 |
| `Handle_grass_generation → Info` | cross_community | 3 |

## How to Explore

1. `context({name: "create_custom_profile_interactive"})` — see callers and callees
2. `query({search_query: "cluster_55"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
