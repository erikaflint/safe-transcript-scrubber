import re

from safe_scrub.synth.generator import generate_transcript


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\w)")
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+\b")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
SLASH_DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")


def test_generated_text_has_no_classic_pii_or_exact_dates() -> None:
    text, _ = generate_transcript(
        template="coaching",
        risk="high",
        seed=55,
        fmt="txt",
        min_turns=24,
        max_turns=24,
    )

    assert EMAIL_RE.search(text) is None
    assert PHONE_RE.search(text) is None
    assert URL_RE.search(text) is None
    assert ISO_DATE_RE.search(text) is None
    assert SLASH_DATE_RE.search(text) is None


def test_generated_vtt_contains_expected_structure_without_pii() -> None:
    text, _ = generate_transcript(
        template="stress_reset",
        risk="medium",
        seed=77,
        fmt="vtt",
        min_turns=10,
        max_turns=10,
    )

    assert text.startswith("WEBVTT")
    assert "THERAPIST:" in text
    assert "CLIENT:" in text
    assert EMAIL_RE.search(text) is None
    assert URL_RE.search(text) is None
