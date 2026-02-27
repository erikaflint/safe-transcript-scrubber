from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


_TIMESTAMP_LINE_RE = re.compile(
    r"^\s*\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}(?:\s+.*)?\s*$"
)


def read_transcript(path: str | Path) -> str:
    source = Path(path)
    raw = source.read_text(encoding="utf-8")
    if source.suffix.lower() != ".vtt":
        return raw
    return _extract_vtt_text(raw)


def _extract_vtt_text(vtt_text: str) -> str:
    lines = vtt_text.splitlines()
    output_lines: list[str] = []
    in_note_block = False

    for line in lines:
        stripped = line.strip()

        if in_note_block:
            if stripped == "":
                in_note_block = False
            continue

        if stripped.startswith("NOTE"):
            in_note_block = True
            continue

        if stripped == "":
            continue
        if stripped == "WEBVTT":
            continue
        if stripped.isdigit():
            continue
        if _TIMESTAMP_LINE_RE.match(line):
            continue

        output_lines.append(stripped)

    return "\n".join(output_lines)


def write_text(path: str | Path, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
