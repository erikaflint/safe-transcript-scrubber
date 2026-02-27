from __future__ import annotations

import re


_SPEAKER_PREFIX_RE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z .'-]{0,80}):(?P<rest>\s*.*)$")


def anonymize_speaker_prefixes(text: str) -> tuple[str, dict[str, object]]:
    mapping: dict[str, str] = {}
    lines = text.splitlines()
    replaced_lines = 0
    output_lines: list[str] = []

    for line in lines:
        match = _SPEAKER_PREFIX_RE.match(line)
        if not match:
            output_lines.append(line)
            continue

        speaker_name = match.group("name").strip()
        if speaker_name not in mapping:
            mapping[speaker_name] = f"SPEAKER_{len(mapping) + 1}"

        output_lines.append(f"{mapping[speaker_name]}:{match.group('rest')}")
        replaced_lines += 1

    stats = {
        "speaker_lines_redacted": replaced_lines,
        "unique_speakers": len(mapping),
    }
    return "\n".join(output_lines), stats
