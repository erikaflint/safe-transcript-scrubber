from __future__ import annotations

from typing import Iterable


def format_txt(lines: Iterable[str]) -> str:
    return "\n".join(lines) + "\n"


def _format_timestamp(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.000"


def format_vtt(lines: list[str], cue_seconds: int = 3) -> str:
    chunks = ["WEBVTT", ""]
    start = 0
    for idx, line in enumerate(lines, start=1):
        end = start + cue_seconds
        chunks.append(str(idx))
        chunks.append(f"{_format_timestamp(start)} --> {_format_timestamp(end)}")
        chunks.append(line)
        chunks.append("")
        start = end
    return "\n".join(chunks).rstrip() + "\n"
