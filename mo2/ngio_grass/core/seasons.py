"""The four seasons Seasons of Skyrim can be pinned to, and the no-seasons mode.

`type_number` is the value of `Season Type` in po3_SeasonsOfSkyrim.ini (0 disabled, 1 winter,
2 spring, 3 summer, 4 autumn, 5 seasonal). `suffix` is what the seasonal cache loader expects
between the cell name and `.cgid`, e.g. `Tamriel_x_y.WIN.cgid`.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Season:
    key: str
    name: str
    type_number: int
    suffix: str

    @property
    def mod_name(self) -> str:
        return "NGIO Grass Cache" if not self.suffix else f"NGIO Grass Cache - {self.name}"


WINTER = Season("winter", "Winter", 1, ".WIN")
SPRING = Season("spring", "Spring", 2, ".SPR")
SUMMER = Season("summer", "Summer", 3, ".SUM")
AUTUMN = Season("autumn", "Autumn", 4, ".AUT")
NO_SEASONS = Season("none", "No seasons", 0, "")

FOUR = (WINTER, SPRING, SUMMER, AUTUMN)
BY_KEY = {s.key: s for s in (*FOUR, NO_SEASONS)}
SEASONAL_SUFFIXES = tuple(s.suffix for s in FOUR)

RUN_SETTINGS_MOD = "NGIO Grass - Run Settings"
LOD_MOD = "NGIO Grass Cache - DynDOLOD LOD"
