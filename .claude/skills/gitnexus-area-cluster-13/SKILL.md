---
name: gitnexus-area-cluster-13
description: "Skill for the Cluster_13 area of NGIO_AutomationSuite. 6 symbols across 2 files."
---

# Cluster_13

6 symbols | 2 files | Cohesion: 37%

## When to Use

- Working with code in `src/`
- Understanding how show_main_menu, configuration_summary, crash_analysis work
- Modifying cluster_13-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/logger.py` | configuration_summary, crash_analysis, performance_stats, separator, system_info |
| `ngio_automation_runner.py` | show_main_menu |

## Entry Points

Start here when exploring this area:

- **`show_main_menu`** (Function) — `ngio_automation_runner.py:204`
- **`configuration_summary`** (Method) — `src/utils/logger.py:225`
- **`crash_analysis`** (Method) — `src/utils/logger.py:290`
- **`performance_stats`** (Method) — `src/utils/logger.py:273`
- **`separator`** (Method) — `src/utils/logger.py:181`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `show_main_menu` | Function | `ngio_automation_runner.py` | 204 |
| `configuration_summary` | Method | `src/utils/logger.py` | 225 |
| `crash_analysis` | Method | `src/utils/logger.py` | 290 |
| `performance_stats` | Method | `src/utils/logger.py` | 273 |
| `separator` | Method | `src/utils/logger.py` | 181 |
| `system_info` | Method | `src/utils/logger.py` | 217 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Handle_configuration → Info` | cross_community | 4 |
| `Main → Info` | cross_community | 4 |
| `Show_main_menu → Info` | cross_community | 3 |
| `_generate_lod_grass_cache → Info` | cross_community | 3 |
| `Configuration_summary → Info` | cross_community | 3 |
| `Crash_analysis → Info` | cross_community | 3 |
| `Final_report → Info` | cross_community | 3 |
| `Performance_stats → Info` | cross_community | 3 |
| `System_info → Info` | cross_community | 3 |

## How to Explore

1. `context({name: "show_main_menu"})` — see callers and callees
2. `query({search_query: "cluster_13"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
