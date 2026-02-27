from safe_scrub.scrub.high_risk import apply_generalizations
from safe_scrub.scrub.redact import scrub_text


def test_public_demo_generalizes_relationship_and_tracks_applied() -> None:
    text = "My ex-husband recorded me without consent."

    result = scrub_text(text, mode="fast", policy="public-demo")
    public_text = result["scrubbed_public_text"]
    risk_report = result["risk_report"]

    assert public_text is not None
    assert "ex-husband" not in public_text.lower()
    assert "former partner" in public_text.lower()

    applied = risk_report["generalizations_applied"]
    assert any(item["from"] == "ex-husband" for item in applied)


def test_apply_generalizations_direct() -> None:
    text = "My ex-husband said this was recorded."
    matches = [
        {"category": "relationship", "match": "ex-husband", "count": 1, "points": 2},
        {
            "category": "recording_surveillance",
            "match": "recorded",
            "count": 1,
            "points": 3,
        },
    ]

    updated, applied = apply_generalizations(text, matches)

    assert "ex-husband" not in updated.lower()
    assert "former partner" in updated.lower()
    assert any(item["from"] == "ex-husband" and item["count"] >= 1 for item in applied)
