"""The .cgid files NGIO writes, one per cell, and the seasonal names they are given afterwards."""
from __future__ import annotations

import os
import shutil

from .seasons import SEASONAL_SUFFIXES


def is_plain(name: str) -> bool:
    """A cache file NGIO wrote itself, not yet given a season."""
    low = name.lower()
    return low.endswith(".cgid") and not any(low.endswith(s.lower() + ".cgid") for s in SEASONAL_SUFFIXES)


def count(grass_dir: str) -> int:
    if not os.path.isdir(grass_dir):
        return 0
    return sum(1 for n in os.listdir(grass_dir) if n.lower().endswith(".cgid"))


def add_suffix(grass_dir: str, suffix: str) -> int:
    """Rename every plain Name.cgid to Name<suffix>.cgid. Returns how many were renamed."""
    if not suffix or not os.path.isdir(grass_dir):
        return 0
    renamed = 0
    for name in os.listdir(grass_dir):
        if not is_plain(name):
            continue
        target = name[: -len(".cgid")] + suffix + ".cgid"
        os.replace(os.path.join(grass_dir, name), os.path.join(grass_dir, target))
        renamed += 1
    return renamed


def copy_without_suffix(src_dir: str, suffix: str, dst_dir: str) -> int:
    """DynDOLOD's grass LOD reads plain names: copy Name<suffix>.cgid to Name.cgid."""
    if not os.path.isdir(src_dir):
        return 0
    os.makedirs(dst_dir, exist_ok=True)
    tail = (suffix + ".cgid").lower()
    copied = 0
    for name in os.listdir(src_dir):
        if name.lower().endswith(tail):
            shutil.copy2(os.path.join(src_dir, name), os.path.join(dst_dir, name[: -len(tail)] + ".cgid"))
            copied += 1
    return copied
