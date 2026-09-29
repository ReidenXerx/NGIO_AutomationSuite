---
name: gitnexus-area-cluster-59
description: "Skill for the Cluster_59 area of NGIO_AutomationSuite. 8 symbols across 1 files."
---

# Cluster_59

8 symbols | 1 files | Cohesion: 74%

## When to Use

- Working with code in `src/`
- Understanding how main, check_mod_installed, create_diagnostic_report work
- Modifying cluster_59-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/skyrim_detector.py` | main, _check_environment_variables, _check_registry, check_mod_installed, create_diagnostic_report (+3) |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `src/utils/skyrim_detector.py:554`
- **`check_mod_installed`** (Method) — `src/utils/skyrim_detector.py:288`
- **`create_diagnostic_report`** (Method) — `src/utils/skyrim_detector.py:483`
- **`detect_skyrim_installations`** (Method) — `src/utils/skyrim_detector.py:89`
- **`get_best_installation`** (Method) — `src/utils/skyrim_detector.py:456`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `src/utils/skyrim_detector.py` | 554 |
| `check_mod_installed` | Method | `src/utils/skyrim_detector.py` | 288 |
| `create_diagnostic_report` | Method | `src/utils/skyrim_detector.py` | 483 |
| `detect_skyrim_installations` | Method | `src/utils/skyrim_detector.py` | 89 |
| `get_best_installation` | Method | `src/utils/skyrim_detector.py` | 456 |
| `get_mod_info` | Method | `src/utils/skyrim_detector.py` | 309 |
| `_check_environment_variables` | Method | `src/utils/skyrim_detector.py` | 171 |
| `_check_registry` | Method | `src/utils/skyrim_detector.py` | 128 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _determine_skyrim_version` | cross_community | 5 |
| `Main → _find_executable` | cross_community | 5 |
| `Main → Debug` | cross_community | 5 |
| `Main → _check_required_files` | cross_community | 4 |
| `Check_mod_installed → _determine_skyrim_version` | cross_community | 4 |
| `Check_mod_installed → _find_executable` | cross_community | 4 |
| `Check_mod_installed → _check_required_files` | cross_community | 4 |
| `Create_diagnostic_report → _determine_skyrim_version` | cross_community | 4 |
| `Create_diagnostic_report → _find_executable` | cross_community | 4 |
| `Create_diagnostic_report → _check_required_files` | cross_community | 4 |

## How to Explore

1. `context({name: "main"})` — see callers and callees
2. `query({search_query: "cluster_59"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
