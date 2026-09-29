---
name: gitnexus-area-cluster-57
description: "Skill for the Cluster_57 area of NGIO_AutomationSuite. 8 symbols across 2 files."
---

# Cluster_57

8 symbols | 2 files | Cohesion: 64%

## When to Use

- Working with code in `src/`
- Understanding how notify_user, notify_completion, notify_error work
- Modifying cluster_57-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `src/utils/notifications.py` | notify_user, _show_toast, notify_completion, notify_error, notify_progress (+2) |
| `src/core/automation_suite.py` | _generate_completion_report |

## Entry Points

Start here when exploring this area:

- **`notify_user`** (Function) — `src/utils/notifications.py:180`
- **`notify_completion`** (Method) — `src/utils/notifications.py:131`
- **`notify_error`** (Method) — `src/utils/notifications.py:140`
- **`notify_progress`** (Method) — `src/utils/notifications.py:147`
- **`play_completion_sound`** (Method) — `src/utils/notifications.py:155`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `notify_user` | Function | `src/utils/notifications.py` | 180 |
| `notify_completion` | Method | `src/utils/notifications.py` | 131 |
| `notify_error` | Method | `src/utils/notifications.py` | 140 |
| `notify_progress` | Method | `src/utils/notifications.py` | 147 |
| `play_completion_sound` | Method | `src/utils/notifications.py` | 155 |
| `play_error_sound` | Method | `src/utils/notifications.py` | 163 |
| `_generate_completion_report` | Method | `src/core/automation_suite.py` | 566 |
| `_show_toast` | Method | `src/utils/notifications.py` | 115 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Notify_user → Debug` | cross_community | 4 |
| `_generate_season_cache → Debug` | cross_community | 4 |
| `Notify_completion → Debug` | cross_community | 3 |

## How to Explore

1. `context({name: "notify_user"})` — see callers and callees
2. `query({search_query: "cluster_57"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
