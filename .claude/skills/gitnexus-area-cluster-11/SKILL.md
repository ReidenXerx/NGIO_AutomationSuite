---
name: gitnexus-area-cluster-11
description: "Skill for the Cluster_11 area of NGIO_AutomationSuite. 66 symbols across 13 files."
---

# Cluster_11

66 symbols | 13 files | Cohesion: 75%

## When to Use

- Working with code in `src/`
- Understanding how check_system_requirements, main, main work
- Modifying cluster_11-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/core/archive_creator.py` | main, _create_lod_metadata_files, _create_lod_mod_structure, _create_lod_zip_archive, _create_mod_structure (+14) |
| `src/core/config_manager.py` | main, _modify_ini_value, _read_config_with_bom_handling, backup_all_configs, configure_ngio_for_cache_use (+5) |
| `src/core/automation_suite.py` | _cleanup_season_files, _create_single_season_archive, _emergency_cleanup, _generate_lod_grass_cache, _generate_lod_grass_cache_from_dir (+4) |
| `src/utils/task_scheduler.py` | create_overnight_task, create_task, create_weekly_task, delete_task, list_tasks |
| `src/core/file_processor.py` | _create_mod_metadata, _execute_operations, create_lod_grass_files, create_mod_folder_structure |
| `src/utils/logger.py` | crash_detected, error, success, warning |
| `src/core/game_manager.py` | _handle_existing_progress, detect_crash, detect_hang |
| `src/core/progress_monitor.py` | _create_crash_result, _detect_process_hang, monitor_generation_process |
| `src/utils/config_cache.py` | _collect_user_preferences, _prompt_for_path, collect_user_paths |
| `src/utils/config_loader.py` | create_config_template, save_template |

## Entry Points

Start here when exploring this area:

- **`check_system_requirements`** (Function) — `ngio_automation_runner.py:177`
- **`main`** (Function) — `src/core/archive_creator.py:1000`
- **`main`** (Function) — `src/core/config_manager.py:625`
- **`create_config_template`** (Function) — `src/utils/config_loader.py:449`
- **`create_all_season_archives`** (Method) — `src/core/archive_creator.py:793`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `check_system_requirements` | Function | `ngio_automation_runner.py` | 177 |
| `main` | Function | `src/core/archive_creator.py` | 1000 |
| `main` | Function | `src/core/config_manager.py` | 625 |
| `create_config_template` | Function | `src/utils/config_loader.py` | 449 |
| `create_all_season_archives` | Method | `src/core/archive_creator.py` | 793 |
| `create_lod_grass_archive` | Method | `src/core/archive_creator.py` | 516 |
| `create_season_archive` | Method | `src/core/archive_creator.py` | 60 |
| `generate_installation_guide` | Method | `src/core/archive_creator.py` | 874 |
| `verify_archive_checksum` | Method | `src/core/archive_creator.py` | 477 |
| `backup_all_configs` | Method | `src/core/config_manager.py` | 193 |
| `configure_ngio_for_cache_use` | Method | `src/core/config_manager.py` | 396 |
| `configure_ngio_for_generation` | Method | `src/core/config_manager.py` | 307 |
| `get_current_season` | Method | `src/core/config_manager.py` | 561 |
| `restore_all_configs` | Method | `src/core/config_manager.py` | 510 |
| `set_season` | Method | `src/core/config_manager.py` | 237 |
| `validate_configurations` | Method | `src/core/config_manager.py` | 440 |
| `create_lod_grass_files` | Method | `src/core/file_processor.py` | 472 |
| `create_mod_folder_structure` | Method | `src/core/file_processor.py` | 285 |
| `detect_crash` | Method | `src/core/game_manager.py` | 447 |
| `detect_hang` | Method | `src/core/game_manager.py` | 486 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → Error` | cross_community | 5 |
| `Load_config → Warning` | cross_community | 5 |
| `Cleanup_processes → Error` | cross_community | 5 |
| `Cleanup_processes → Warning` | cross_community | 5 |
| `Monitor_generation_process → Debug` | cross_community | 5 |
| `Handle_configuration → Info` | cross_community | 4 |
| `Main → Error` | intra_community | 4 |
| `Main → Warning` | cross_community | 4 |
| `Load_config → Error` | cross_community | 4 |
| `Main → Debug` | cross_community | 4 |

## How to Explore

1. `context({name: "check_system_requirements"})` — see callers and callees
2. `query({search_query: "cluster_11"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
