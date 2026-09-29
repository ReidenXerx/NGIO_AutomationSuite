---
name: gitnexus-area-cluster-0
description: "Skill for the Cluster_0 area of NGIO_AutomationSuite. 44 symbols across 4 files."
---

# Cluster_0

44 symbols | 4 files | Cohesion: 93%

## When to Use

- Working with code in `vortex/`
- Understanding how IniText, copyWithoutSuffix, isPlain work
- Modifying cluster_0-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `vortex/src/runner.js` | finish, onDid, timer, onSpawned, add (+29) |
| `vortex/src/core/cgid.js` | copyWithoutSuffix, isPlain, list, moveNew |
| `vortex/src/procs.js` | findGame, norm, pagefileBytes, powershell |
| `vortex/src/core/ini.js` | IniText, fromBuffer |

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `IniText` | Class | `vortex/src/core/ini.js` | 12 |
| `copyWithoutSuffix` | Function | `vortex/src/core/cgid.js` | 46 |
| `isPlain` | Function | `vortex/src/core/cgid.js` | 6 |
| `list` | Function | `vortex/src/core/cgid.js` | 11 |
| `moveNew` | Function | `vortex/src/core/cgid.js` | 25 |
| `findGame` | Function | `vortex/src/procs.js` | 18 |
| `norm` | Function | `vortex/src/procs.js` | 15 |
| `pagefileBytes` | Function | `vortex/src/procs.js` | 40 |
| `powershell` | Function | `vortex/src/procs.js` | 8 |
| `finish` | Function | `vortex/src/runner.js` | 152 |
| `onDid` | Function | `vortex/src/runner.js` | 159 |
| `timer` | Function | `vortex/src/runner.js` | 160 |
| `onSpawned` | Function | `vortex/src/runner.js` | 339 |
| `add` | Function | `vortex/src/runner.js` | 171 |
| `has` | Function | `vortex/src/runner.js` | 182 |
| `write` | Function | `vortex/src/runner.js` | 263 |
| `live` | Function | `vortex/src/runner.js` | 302 |
| `exists` | Function | `vortex/src/runner.js` | 34 |
| `fromBuffer` | Method | `vortex/src/core/ini.js` | 22 |
| `checkProfile` | Method | `vortex/src/runner.js` | 142 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Tick → DataDir` | cross_community | 6 |
| `Abort → Exists` | cross_community | 5 |
| `Abort → Norm` | cross_community | 5 |
| `Abort → Powershell` | cross_community | 5 |
| `Tick → Emit` | cross_community | 5 |
| `NextSeason → DataDir` | cross_community | 5 |
| `NextSeason → Exists` | intra_community | 5 |
| `Start → Exists` | cross_community | 5 |
| `NextSeason → List` | intra_community | 4 |
| `Tick → Ctx` | cross_community | 4 |

## How to Explore

1. `context({name: "IniText"})` — see callers and callees
2. `query({search_query: "cluster_0"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
