from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RegexRule:
    label: str
    pattern: re.Pattern[str]


REGEX_RULES: list[RegexRule] = [
    RegexRule(
        label="EMAIL",
        pattern=re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ),
    RegexRule(
        label="PHONE",
        pattern=re.compile(
            r"(?<!\w)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\w)"
        ),
    ),
    RegexRule(
        label="URL",
        pattern=re.compile(r"\b(?:https?://|www\.)\S+\b"),
    ),
    RegexRule(
        label="ADDRESS",
        pattern=re.compile(
            r"\b\d{1,6}\s+[A-Za-z0-9.'-]+(?:\s+[A-Za-z0-9.'-]+){0,5}\s+"
            r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b",
            re.IGNORECASE,
        ),
    ),
    RegexRule(
        label="LONG_NUMBER",
        # Catches account/reference/ID-shaped numbers of 8+ total digits, whether or not
        # they're separator-formatted (dashes, dots, spaces), not just unbroken digit runs.
        pattern=re.compile(r"\b\d(?:[-.\s]?\d){7,}\b"),
    ),
]
