---
name: gitnexus-area-cluster-48
description: "Skill for the Cluster_48 area of NGIO_AutomationSuite. 8 symbols across 1 files."
---

# Cluster_48

8 symbols | 1 files | Cohesion: 67%

## When to Use

- Working with code in `src/`
- Understanding how load_config, load, validate_and_report work
- Modifying cluster_48-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/config_loader.py` | load_config, _apply_env_overrides, _auto_detect_paths, _detect_skyrim_path, _merge_yaml_config (+3) |

## Entry Points

Start here when exploring this area:

- **`load_config`** (Function) — `src/utils/config_loader.py:433`
- **`load`** (Method) — `src/utils/config_loader.py:161`
- **`validate_and_report`** (Method) — `src/utils/config_loader.py:412`
- **`validate`** (Method) — `src/utils/config_loader.py:79`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `load_config` | Function | `src/utils/config_loader.py` | 433 |
| `load` | Method | `src/utils/config_loader.py` | 161 |
| `validate_and_report` | Method | `src/utils/config_loader.py` | 412 |
| `validate` | Method | `src/utils/config_loader.py` | 79 |
| `_apply_env_overrides` | Method | `src/utils/config_loader.py` | 234 |
| `_auto_detect_paths` | Method | `src/utils/config_loader.py` | 262 |
| `_detect_skyrim_path` | Method | `src/utils/config_loader.py` | 283 |
| `_merge_yaml_config` | Method | `src/utils/config_loader.py` | 226 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Load_config → Debug` | cross_community | 5 |
| `Load_config → Warning` | cross_community | 5 |
| `Load_config → _detect_skyrim_path` | intra_community | 4 |
| `Load_config → Error` | cross_community | 4 |
| `Load_config → Info` | cross_community | 4 |
| `Load_config → Validate` | intra_community | 3 |

## How to Explore

1. `context({name: "load_config"})` — see callers and callees
2. `query({search_query: "cluster_48"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
