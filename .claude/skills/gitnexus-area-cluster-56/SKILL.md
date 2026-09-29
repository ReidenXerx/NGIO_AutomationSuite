---
name: gitnexus-area-cluster-56
description: "Skill for the Cluster_56 area of NGIO_AutomationSuite. 7 symbols across 1 files."
---

# Cluster_56

7 symbols | 1 files | Cohesion: 46%

## When to Use

- Working with code in `src/`
- Understanding how main, banner, final_report work
- Modifying cluster_56-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/logger.py` | main, banner, final_report, season_start, step (+2) |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `src/utils/logger.py:343`
- **`banner`** (Method) — `src/utils/logger.py:312`
- **`final_report`** (Method) — `src/utils/logger.py:236`
- **`season_start`** (Method) — `src/utils/logger.py:158`
- **`step`** (Method) — `src/utils/logger.py:154`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `main` | Function | `src/utils/logger.py` | 343 |
| `banner` | Method | `src/utils/logger.py` | 312 |
| `final_report` | Method | `src/utils/logger.py` | 236 |
| `season_start` | Method | `src/utils/logger.py` | 158 |
| `step` | Method | `src/utils/logger.py` | 154 |
| `table_header` | Method | `src/utils/logger.py` | 194 |
| `table_row` | Method | `src/utils/logger.py` | 200 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → Info` | cross_community | 3 |
| `Final_report → Info` | cross_community | 3 |

## How to Explore

1. `context({name: "main"})` — see callers and callees
2. `query({search_query: "cluster_56"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
