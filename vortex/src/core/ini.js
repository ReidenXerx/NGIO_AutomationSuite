"use strict";
/**
 * Line-level INI editing that keeps everything it does not touch. Same rules as the MO2
 * plugin's core/ini.py (and the same tests): sections and keys match case-insensitively, a
 * replaced line keeps the file's own spelling of the key, and the BOM and line endings survive.
 * NGIO reads [GrassConfig] with hyphenated keys; 1.6.0 wrote a [Settings] section it never reads.
 */

const SECTION = /^\s*\[([^\]]+)\]\s*$/;
const ENTRY = /^([^;#=[][^=]*?)\s*=\s?(.*)$/;
const BOM = "﻿";

class IniText {
  constructor(text) {
    this.bom = text.startsWith(BOM);
    if (this.bom) text = text.slice(1);
    this.newline = text.includes("\r\n") ? "\r\n" : "\n";
    this.trailingNewline = /\r?\n$/.test(text);
    this.lines = text.length ? text.split(/\r?\n/) : [];
    if (this.trailingNewline) this.lines.pop();
  }

  static fromBuffer(buf) {
    const text = buf.toString("utf8");
    // A stray U+FFFD means the file was not UTF-8; read it as Windows-1252 instead.
    return new IniText(text.includes("�") ? buf.toString("latin1") : text);
  }

  toText() {
    let body = this.lines.join(this.newline);
    if (this.trailingNewline || this.lines.length === 0) body += this.newline;
    return (this.bom ? BOM : "") + body;
  }

  toBuffer() {
    return Buffer.from(this.toText(), "utf8");
  }

  sectionSpan(section) {
    const want = section.trim().toLowerCase();
    let start = -1;
    for (let i = 0; i < this.lines.length; i++) {
      const m = SECTION.exec(this.lines[i]);
      if (!m) continue;
      if (start !== -1) return [start, i];
      if (m[1].trim().toLowerCase() === want) start = i;
    }
    return start === -1 ? null : [start, this.lines.length];
  }

  find(section, key) {
    const span = this.sectionSpan(section);
    if (!span) return -1;
    const want = key.trim().toLowerCase();
    for (let i = span[0] + 1; i < span[1]; i++) {
      const m = ENTRY.exec(this.lines[i]);
      if (m && m[1].trim().toLowerCase() === want) return i;
    }
    return -1;
  }

  get(section, key) {
    const i = this.find(section, key);
    if (i === -1) return null;
    return ENTRY.exec(this.lines[i])[2].trim();
  }

  /** Set a value; returns true when the file changed. */
  set(section, key, value) {
    const i = this.find(section, key);
    if (i !== -1) {
      const m = ENTRY.exec(this.lines[i]);
      if (m[2].trim() === value) return false;
      this.lines[i] = `${m[1].trimEnd()} = ${value}`;
      return true;
    }
    const span = this.sectionSpan(section);
    if (!span) {
      if (this.lines.length && this.lines[this.lines.length - 1].trim()) this.lines.push("");
      this.lines.push(`[${section}]`, `${key} = ${value}`);
      return true;
    }
    let at = span[0] + 1;
    for (let j = span[0] + 1; j < span[1]; j++) if (this.lines[j].trim()) at = j + 1;
    this.lines.splice(at, 0, `${key} = ${value}`);
    return true;
  }
}

module.exports = { IniText };
