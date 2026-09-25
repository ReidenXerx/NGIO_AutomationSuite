"""Line-level INI editing that keeps everything it does not touch.

NGIO and Seasons of Skyrim read plain INI files, and players keep comments, order and hand-tuned
values in them. Python's ConfigParser is the wrong tool here: it drops every comment, lowercases
every key on save, and 1.6.0 used it to write a [Settings] section that NGIO never reads.

So this edits one line at a time. Sections and keys match case-insensitively (NGIO's own page
spells "Use-grass-cache", its generated file spells "use-grass-cache"). A replaced line keeps the
file's own spelling of the key. The BOM and the line endings survive a round trip.
"""
from __future__ import annotations

import re

_SECTION = re.compile(r"^\s*\[(?P<name>[^\]]+)\]\s*$")
_ENTRY = re.compile(r"^(?P<key>[^;#=\[][^=]*?)\s*=\s?(?P<value>.*)$")
_BOM = "﻿"


class IniText:
    def __init__(self, text: str):
        self.bom = text.startswith(_BOM)
        if self.bom:
            text = text[1:]
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.trailing_newline = text.endswith(("\n", "\r\n"))
        self.lines = text.splitlines()

    @classmethod
    def from_bytes(cls, data: bytes) -> "IniText":
        try:
            return cls(data.decode("utf-8"))
        except UnicodeDecodeError:
            return cls(data.decode("cp1252"))

    def to_text(self) -> str:
        body = self.newline.join(self.lines)
        if self.trailing_newline or not self.lines:
            body += self.newline
        return (_BOM if self.bom else "") + body

    def to_bytes(self) -> bytes:
        return self.to_text().encode("utf-8")

    def _section_span(self, section: str) -> tuple[int, int] | None:
        """(header line, end line exclusive) of the first section with this name."""
        want = section.strip().lower()
        start = None
        for i, line in enumerate(self.lines):
            m = _SECTION.match(line)
            if not m:
                continue
            if start is not None:
                return start, i
            if m.group("name").strip().lower() == want:
                start = i
        return (start, len(self.lines)) if start is not None else None

    def _find(self, section: str, key: str) -> int | None:
        span = self._section_span(section)
        if span is None:
            return None
        want = key.strip().lower()
        for i in range(span[0] + 1, span[1]):
            m = _ENTRY.match(self.lines[i])
            if m and m.group("key").strip().lower() == want:
                return i
        return None

    def get(self, section: str, key: str) -> str | None:
        i = self._find(section, key)
        if i is None:
            return None
        m = _ENTRY.match(self.lines[i])
        return m.group("value").strip() if m else None

    def set(self, section: str, key: str, value: str) -> bool:
        """Set a value; returns True when the file changed."""
        i = self._find(section, key)
        if i is not None:
            m = _ENTRY.match(self.lines[i])
            assert m is not None
            if m.group("value").strip() == value:
                return False
            self.lines[i] = f"{m.group('key').rstrip()} = {value}"
            return True
        span = self._section_span(section)
        if span is None:
            if self.lines and self.lines[-1].strip():
                self.lines.append("")
            self.lines += [f"[{section}]", f"{key} = {value}"]
            return True
        # After the section's last non-blank line, so a blank separator stays where it was.
        at = span[0] + 1
        for j in range(span[0] + 1, span[1]):
            if self.lines[j].strip():
                at = j + 1
        self.lines.insert(at, f"{key} = {value}")
        return True
