---
name: gitnexus-area-cluster-64
description: "Skill for the Cluster_64 area of NGIO_AutomationSuite. 8 symbols across 1 files."
---

# Cluster_64

8 symbols | 1 files | Cohesion: 88%

## When to Use

- Working with code in `vortex/`
- Understanding how onClick, onClick, onClick work
- Modifying cluster_64-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `vortex/src/page.js` | onClick, onClick, onClick, onChange, onChange (+3) |

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `onClick` | Function | `vortex/src/page.js` | 161 |
| `onClick` | Function | `vortex/src/page.js` | 130 |
| `onClick` | Function | `vortex/src/page.js` | 131 |
| `onChange` | Function | `vortex/src/page.js` | 104 |
| `onChange` | Function | `vortex/src/page.js` | 98 |
| `componentDidMount` | Method | `vortex/src/page.js` | 31 |
| `fix` | Method | `vortex/src/page.js` | 89 |
| `refreshChecks` | Method | `vortex/src/page.js` | 41 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `OnClick → Picked` | cross_community | 4 |
| `OnClick → SafeSetState` | cross_community | 4 |
| `OnClick → Picked` | cross_community | 3 |
| `OnClick → SafeSetState` | cross_community | 3 |
| `OnClick → Picked` | cross_community | 3 |
| `OnClick → SafeSetState` | cross_community | 3 |
| `OnChange → Picked` | cross_community | 3 |
| `OnChange → SafeSetState` | cross_community | 3 |
| `OnChange → Picked` | cross_community | 3 |
| `OnChange → SafeSetState` | cross_community | 3 |

## How to Explore

1. `context({name: "onClick"})` — see callers and callees
2. `query({search_query: "cluster_64"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
