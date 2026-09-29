---
name: gitnexus-area-cluster-75
description: "Skill for the Cluster_75 area of NGIO_AutomationSuite. 34 symbols across 8 files."
---

# Cluster_75

34 symbols | 8 files | Cohesion: 59%

## When to Use

- Working with code in `src/`
- Understanding how validate_file_integrity, check_precache_file_status, cleanup_processes work
- Modifying cluster_75-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/core/game_manager.py` | _create_precache_trigger, _create_progress_lock, _has_active_generation, _has_existing_grass_cache, _is_process_alive_safe (+11) |
| `src/utils/logger.py` | debug, memory_usage, set_level, timing_end, timing_start |
| `src/core/progress_monitor.py` | _parse_log_file, _read_console_output, _read_ngio_logs, _read_skyrim_logs |
| `src/utils/skyrim_detector.py` | _check_for_conflicts, _get_free_disk_space, _perform_additional_checks |
| `src/core/automation_suite.py` | _is_season_completed, _run_generation_with_monitoring |
| `src/utils/config_loader.py` | _find_config_file, _load_yaml |
| `src/core/file_processor.py` | validate_file_integrity |
| `src/utils/notifications.py` | play_warning_sound |

## Entry Points

Start here when exploring this area:

- **`validate_file_integrity`** (Method) — `src/core/file_processor.py:392`
- **`check_precache_file_status`** (Method) — `src/core/game_manager.py:617`
- **`cleanup_processes`** (Method) — `src/core/game_manager.py:965`
- **`force_terminate`** (Method) — `src/core/game_manager.py:537`
- **`get_process_status`** (Method) — `src/core/game_manager.py:419`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `validate_file_integrity` | Method | `src/core/file_processor.py` | 392 |
| `check_precache_file_status` | Method | `src/core/game_manager.py` | 617 |
| `cleanup_processes` | Method | `src/core/game_manager.py` | 965 |
| `force_terminate` | Method | `src/core/game_manager.py` | 537 |
| `get_process_status` | Method | `src/core/game_manager.py` | 419 |
| `is_process_running` | Method | `src/core/game_manager.py` | 391 |
| `track_startup_duration` | Method | `src/core/game_manager.py` | 111 |
| `wait_for_precache_completion` | Method | `src/core/game_manager.py` | 676 |
| `debug` | Method | `src/utils/logger.py` | 118 |
| `memory_usage` | Method | `src/utils/logger.py` | 286 |
| `set_level` | Method | `src/utils/logger.py` | 326 |
| `timing_end` | Method | `src/utils/logger.py` | 211 |
| `timing_start` | Method | `src/utils/logger.py` | 205 |
| `play_warning_sound` | Method | `src/utils/notifications.py` | 171 |
| `_is_season_completed` | Method | `src/core/automation_suite.py` | 629 |
| `_run_generation_with_monitoring` | Method | `src/core/automation_suite.py` | 354 |
| `_create_precache_trigger` | Method | `src/core/game_manager.py` | 272 |
| `_create_progress_lock` | Method | `src/core/game_manager.py` | 918 |
| `_has_active_generation` | Method | `src/core/game_manager.py` | 937 |
| `_has_existing_grass_cache` | Method | `src/core/game_manager.py` | 941 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Load_config → Debug` | cross_community | 5 |
| `Load_config → Warning` | cross_community | 5 |
| `Cleanup_processes → Error` | cross_community | 5 |
| `Main → Debug` | cross_community | 5 |
| `Cleanup_processes → Warning` | cross_community | 5 |
| `Monitor_generation_process → Debug` | cross_community | 5 |
| `Load_config → Error` | cross_community | 4 |
| `Main → Debug` | cross_community | 4 |
| `Notify_user → Debug` | cross_community | 4 |
| `_generate_season_cache → Debug` | cross_community | 4 |

## How to Explore

1. `context({name: "validate_file_integrity"})` — see callers and callees
2. `query({search_query: "cluster_75"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
