---
name: gitnexus-area-cluster-3
description: "Skill for the Cluster_3 area of NGIO_AutomationSuite. 8 symbols across 1 files."
---

# Cluster_3

8 symbols | 1 files | Cohesion: 100%

## When to Use

- Understanding how build_single_exe, calculate_checksum, check_dependencies work
- Modifying cluster_3-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `build_release.py` | build_single_exe, calculate_checksum, check_dependencies, clean_directories, create_final_release_package (+3) |

## Entry Points

Start here when exploring this area:

- **`build_single_exe`** (Function) — `build_release.py:102`
- **`calculate_checksum`** (Function) — `build_release.py:43`
- **`check_dependencies`** (Function) — `build_release.py:69`
- **`clean_directories`** (Function) — `build_release.py:52`
- **`create_final_release_package`** (Function) — `build_release.py:336`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `build_single_exe` | Function | `build_release.py` | 102 |
| `calculate_checksum` | Function | `build_release.py` | 43 |
| `check_dependencies` | Function | `build_release.py` | 69 |
| `clean_directories` | Function | `build_release.py` | 52 |
| `create_final_release_package` | Function | `build_release.py` | 336 |
| `create_portable_package` | Function | `build_release.py` | 141 |
| `create_release_info` | Function | `build_release.py` | 473 |
| `main` | Function | `build_release.py` | 542 |

## How to Explore

1. `context({name: "build_single_exe"})` — see callers and callees
2. `query({search_query: "cluster_3"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
