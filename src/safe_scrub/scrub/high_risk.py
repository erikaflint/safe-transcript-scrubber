from __future__ import annotations

import re
from collections import defaultdict


def _compile_keywords(keywords: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    compiled: list[tuple[str, re.Pattern[str]]] = []
    for keyword in keywords:
        escaped = re.escape(keyword).replace(r"\ ", r"\s+")
        compiled.append((keyword, re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)))
    return compiled


_CATEGORY_POINTS: dict[str, int] = {
    "relationship": 2,
    "recording_surveillance": 3,
    "legal": 3,
    "medical_or_clinical": 2,
    "high_specificity_markers": 2,
}

_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "relationship": [
        "ex-husband",
        "ex-wife",
        "husband",
        "wife",
        "partner",
        "boyfriend",
        "girlfriend",
        "fiance",
        "spouse",
        "roommate",
        "coworker",
        "boss",
        "manager",
        "teacher",
        "neighbor",
        "family",
        "child",
        "parent",
    ],
    "recording_surveillance": [
        "recorded",
        "recording",
        "taped",
        "video",
        "audio",
        "camera",
        "consent",
        "privacy",
        "screenshot",
    ],
    "legal": [
        "court",
        "lawyer",
        "police",
        "restraining order",
        "subpoena",
        "lawsuit",
    ],
    "medical_or_clinical": [
        "diagnosis",
        "clinic",
        "hospital",
        "psychiatrist",
        "therapist",
        "medication",
        "er",
    ],
    "high_specificity_markers": [
        "at my workplace",
        "at my school",
        "in my town",
        "my company",
    ],
}

CATEGORY_KEYWORDS = {category: list(keywords) for category, keywords in _CATEGORY_KEYWORDS.items()}

_COMPILED_CATEGORY_KEYWORDS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    category: _compile_keywords(keywords) for category, keywords in _CATEGORY_KEYWORDS.items()
}

_GENERALIZATION_RULES: list[tuple[str, str]] = [
    ("ex-husband", "former partner"),
    ("ex-wife", "former partner"),
    ("husband", "partner"),
    ("wife", "partner"),
    ("boyfriend", "partner"),
    ("girlfriend", "partner"),
    ("boss", "supervisor"),
    ("manager", "supervisor"),
    ("teacher", "mentor"),
    ("recorded", "shared privately"),
    ("recording", "private moment was shared"),
    ("taped", "shared privately"),
    ("at my workplace", "in a professional setting"),
    ("at my school", "in an educational setting"),
    ("in my town", "in my area"),
    ("my company", "my organization"),
]


def _risk_level(score: int) -> str:
    if score >= 7:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _recommendation(level: str) -> str:
    if level == "high":
        return "human_review"
    if level == "medium":
        return "review"
    return "ok"


def analyze_high_risk(text: str) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for category, patterns in _COMPILED_CATEGORY_KEYWORDS.items():
        for keyword, pattern in patterns:
            for found in pattern.finditer(text):
                candidates.append(
                    {
                        "category": category,
                        "match": keyword,
                        "start": found.start(),
                        "end": found.end(),
                    }
                )

    # Prefer longer phrase matches when spans overlap (e.g., ex-husband over husband).
    candidates.sort(
        key=lambda item: (
            -(int(item["end"]) - int(item["start"])),
            int(item["start"]),
            str(item["match"]),
        )
    )
    occupied = [False] * len(text)
    selected: list[dict[str, object]] = []
    for item in candidates:
        start = int(item["start"])
        end = int(item["end"])
        if any(occupied[idx] for idx in range(start, end)):
            continue
        for idx in range(start, end):
            occupied[idx] = True
        selected.append(item)

    score = 0
    flags: list[dict[str, object]] = []
    matches: list[dict[str, object]] = []
    matched_by_category: defaultdict[str, set[str]] = defaultdict(set)
    count_by_key: defaultdict[tuple[str, str], int] = defaultdict(int)
    for item in selected:
        category = str(item["category"])
        keyword = str(item["match"])
        count_by_key[(category, keyword)] += 1

    for (category, keyword), match_count in sorted(count_by_key.items()):
        matched_by_category[category].add(keyword)
        points = _CATEGORY_POINTS[category]
        score += points
        flags.append({"category": category, "match": keyword, "count": match_count})
        matches.append(
                {
                    "category": category,
                    "match": keyword,
                    "count": match_count,
                    "points": points,
                }
        )

    level = _risk_level(score)
    counts_by_category = {category: len(keywords) for category, keywords in matched_by_category.items()}
    return {
        "risk_score": score,
        "risk_level": level,
        "total_flags": len(flags),
        "counts_by_category": counts_by_category,
        "flags": flags,
        "recommendation": _recommendation(level),
        "matches": matches,
    }


def apply_generalizations(text: str, matches: list[dict[str, object]]) -> tuple[str, list[dict[str, object]]]:
    output = text
    applied: list[dict[str, object]] = []

    allowed_terms = {str(item["match"]).lower() for item in matches}

    for source, replacement in _GENERALIZATION_RULES:
        if source.lower() not in allowed_terms:
            continue
        pattern = re.compile(rf"(?<!\w){re.escape(source).replace(r'\ ', r'\s+')}(?!\w)", re.IGNORECASE)
        found = list(pattern.finditer(output))
        if not found:
            continue
        output = pattern.sub(replacement, output)
        applied.append({"from": source, "to": replacement, "count": len(found)})

    return output, applied
