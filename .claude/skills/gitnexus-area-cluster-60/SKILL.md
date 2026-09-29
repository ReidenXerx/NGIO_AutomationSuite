---
name: gitnexus-area-cluster-60
description: "Skill for the Cluster_60 area of NGIO_AutomationSuite. 14 symbols across 1 files."
---

# Cluster_60

14 symbols | 1 files | Cohesion: 79%

## When to Use

- Working with code in `src/`
- Understanding how validate_system, validate_all work
- Modifying cluster_60-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/system_validator.py` | validate_system, _check_dependencies, _check_disk_space, _check_mod_manager, _check_ngio_mod (+9) |

## Entry Points

Start here when exploring this area:

- **`validate_system`** (Function) — `src/utils/system_validator.py:498`
- **`validate_all`** (Method) — `src/utils/system_validator.py:48`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `validate_system` | Function | `src/utils/system_validator.py` | 498 |
| `validate_all` | Method | `src/utils/system_validator.py` | 48 |
| `_check_dependencies` | Method | `src/utils/system_validator.py` | 366 |
| `_check_disk_space` | Method | `src/utils/system_validator.py` | 192 |
| `_check_mod_manager` | Method | `src/utils/system_validator.py` | 414 |
| `_check_ngio_mod` | Method | `src/utils/system_validator.py` | 165 |
| `_check_optional_features` | Method | `src/utils/system_validator.py` | 441 |
| `_check_pagefile_settings` | Method | `src/utils/system_validator.py` | 273 |
| `_check_python_version` | Method | `src/utils/system_validator.py` | 344 |
| `_check_skse_installation` | Method | `src/utils/system_validator.py` | 139 |
| `_check_skyrim_executable` | Method | `src/utils/system_validator.py` | 113 |
| `_check_skyrim_installation` | Method | `src/utils/system_validator.py` | 81 |
| `_check_system_memory` | Method | `src/utils/system_validator.py` | 231 |
| `_check_write_permissions` | Method | `src/utils/system_validator.py` | 313 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Validate_system → _check_ngio_mod` | intra_community | 3 |
| `Validate_system → _check_skse_installation` | intra_community | 3 |
| `Validate_system → _check_skyrim_executable` | intra_community | 3 |
| `Validate_system → _check_skyrim_installation` | intra_community | 3 |
| `Validate_system → Error` | cross_community | 3 |
| `Validate_system → Info` | cross_community | 3 |

## How to Explore

1. `context({name: "validate_system"})` — see callers and callees
2. `query({search_query: "cluster_60"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
