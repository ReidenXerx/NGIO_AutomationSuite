---
name: gitnexus-area-cluster-12
description: "Skill for the Cluster_12 area of NGIO_AutomationSuite. 10 symbols across 3 files."
---

# Cluster_12

10 symbols | 3 files | Cohesion: 50%

## When to Use

- Working with code in `src/`
- Understanding how handle_configuration, main, parse_arguments work
- Modifying cluster_12-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `ngio_automation_runner.py` | handle_configuration, main, parse_arguments, print_banner, show_help |
| `src/utils/config_cache.py` | main, load_config, reset_config, show_current_config |
| `src/utils/logger.py` | set_console_level |

## Entry Points

Start here when exploring this area:

- **`handle_configuration`** (Function) — `ngio_automation_runner.py:463`
- **`main`** (Function) — `ngio_automation_runner.py:707`
- **`parse_arguments`** (Function) — `ngio_automation_runner.py:68`
- **`print_banner`** (Function) — `ngio_automation_runner.py:151`
- **`show_help`** (Function) — `ngio_automation_runner.py:471`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `handle_configuration` | Function | `ngio_automation_runner.py` | 463 |
| `main` | Function | `ngio_automation_runner.py` | 707 |
| `parse_arguments` | Function | `ngio_automation_runner.py` | 68 |
| `print_banner` | Function | `ngio_automation_runner.py` | 151 |
| `show_help` | Function | `ngio_automation_runner.py` | 471 |
| `main` | Function | `src/utils/config_cache.py` | 585 |
| `load_config` | Method | `src/utils/config_cache.py` | 106 |
| `reset_config` | Method | `src/utils/config_cache.py` | 532 |
| `show_current_config` | Method | `src/utils/config_cache.py` | 550 |
| `set_console_level` | Method | `src/utils/logger.py` | 31 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Handle_configuration → Info` | cross_community | 4 |
| `Main → Info` | cross_community | 4 |
| `Main → Is_complete` | cross_community | 3 |
| `Main → Validate_paths` | cross_community | 3 |
| `Main → Error` | cross_community | 3 |

## How to Explore

1. `context({name: "handle_configuration"})` — see callers and callees
2. `query({search_query: "cluster_12"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
