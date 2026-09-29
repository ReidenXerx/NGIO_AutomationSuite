---
name: gitnexus-area-tests
description: "Skill for the Tests area of NGIO_AutomationSuite. 28 symbols across 4 files."
---

# Tests

28 symbols | 4 files | Cohesion: 84%

## When to Use

- Working with code in `mo2/`
- Understanding how obs, add_suffix, is_plain work
- Modifying tests-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `mo2/tests/test_core.py` | obs, test_boot_limit_kills_and_relaunches, test_crash_needs_two_dead_checks_then_waits_the_delay, test_finishing_and_closing_in_one_tick_is_not_a_crash, test_game_left_open_after_finishing_is_closed (+14) |
| `mo2/ngio_grass/core/ini.py` | set, to_text, _find, _section_span, get |
| `mo2/ngio_grass/core/cgid.py` | add_suffix, is_plain |
| `mo2/ngio_grass/controller.py` | _existing_cache_checks, _winner |

## Entry Points

Start here when exploring this area:

- **`obs`** (Function) — `mo2/tests/test_core.py:119`
- **`add_suffix`** (Function) — `mo2/ngio_grass/core/cgid.py:21`
- **`is_plain`** (Function) — `mo2/ngio_grass/core/cgid.py:9`
- **`test_boot_limit_kills_and_relaunches`** (Method) — `mo2/tests/test_core.py:137`
- **`test_crash_needs_two_dead_checks_then_waits_the_delay`** (Method) — `mo2/tests/test_core.py:151`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `obs` | Function | `mo2/tests/test_core.py` | 119 |
| `add_suffix` | Function | `mo2/ngio_grass/core/cgid.py` | 21 |
| `is_plain` | Function | `mo2/ngio_grass/core/cgid.py` | 9 |
| `test_boot_limit_kills_and_relaunches` | Method | `mo2/tests/test_core.py` | 137 |
| `test_crash_needs_two_dead_checks_then_waits_the_delay` | Method | `mo2/tests/test_core.py` | 151 |
| `test_finishing_and_closing_in_one_tick_is_not_a_crash` | Method | `mo2/tests/test_core.py` | 161 |
| `test_game_left_open_after_finishing_is_closed` | Method | `mo2/tests/test_core.py` | 167 |
| `test_game_that_never_appears_is_retried` | Method | `mo2/tests/test_core.py` | 186 |
| `test_gives_up_after_max_restarts` | Method | `mo2/tests/test_core.py` | 173 |
| `test_resumed_trigger_size_is_not_progress` | Method | `mo2/tests/test_core.py` | 191 |
| `test_slow_boot_is_not_a_hang` | Method | `mo2/tests/test_core.py` | 130 |
| `test_stall_after_progress` | Method | `mo2/tests/test_core.py` | 144 |
| `test_adds_suffix_only_to_plain_files` | Method | `mo2/tests/test_core.py` | 98 |
| `test_is_plain` | Method | `mo2/tests/test_core.py` | 113 |
| `test_no_seasons_keeps_plain_names` | Method | `mo2/tests/test_core.py` | 104 |
| `set` | Method | `mo2/ngio_grass/core/ini.py` | 76 |
| `to_text` | Method | `mo2/ngio_grass/core/ini.py` | 35 |
| `test_missing_key_goes_before_the_blank_separator` | Method | `mo2/tests/test_core.py` | 61 |
| `test_missing_section_is_appended` | Method | `mo2/tests/test_core.py` | 69 |
| `test_set_changes_only_that_line` | Method | `mo2/tests/test_core.py` | 46 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Start → _section_span` | cross_community | 5 |
| `Start → _winner` | cross_community | 4 |

## How to Explore

1. `context({name: "obs"})` — see callers and callees
2. `query({search_query: "tests"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
