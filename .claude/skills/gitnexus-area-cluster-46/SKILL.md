---
name: gitnexus-area-cluster-46
description: "Skill for the Cluster_46 area of NGIO_AutomationSuite. 7 symbols across 1 files."
---

# Cluster_46

7 symbols | 1 files | Cohesion: 52%

## When to Use

- Working with code in `src/`
- Understanding how main, benchmark_performance, get_statistics work
- Modifying cluster_46-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/core/file_processor.py` | main, _create_rename_operations, _find_cgid_files, _update_stats, benchmark_performance (+2) |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `src/core/file_processor.py:645`
- **`benchmark_performance`** (Method) — `src/core/file_processor.py:573`
- **`get_statistics`** (Method) — `src/core/file_processor.py:458`
- **`process_season_files`** (Method) — `src/core/file_processor.py:73`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `src/core/file_processor.py` | 645 |
| `benchmark_performance` | Method | `src/core/file_processor.py` | 573 |
| `get_statistics` | Method | `src/core/file_processor.py` | 458 |
| `process_season_files` | Method | `src/core/file_processor.py` | 73 |
| `_create_rename_operations` | Method | `src/core/file_processor.py` | 138 |
| `_find_cgid_files` | Method | `src/core/file_processor.py` | 123 |
| `_update_stats` | Method | `src/core/file_processor.py` | 462 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → Error` | cross_community | 5 |
| `Main → Info` | cross_community | 4 |
| `Main → Warning` | cross_community | 4 |

## How to Explore

1. `context({name: "main"})` — see callers and callees
2. `query({search_query: "cluster_46"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
