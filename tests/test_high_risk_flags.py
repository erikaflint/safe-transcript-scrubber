from safe_scrub.scrub.redact import scrub_text


def test_high_risk_flags_and_level_high() -> None:
    text = "My ex-husband recorded me without consent and started a lawsuit."

    result = scrub_text(text, mode="fast", policy="internal")
    risk_report = result["risk_report"]

    assert risk_report["policy_applied"] == "internal"
    assert risk_report["risk_level"] == "high"
    assert risk_report["recommendation"] == "human_review"

    categories = {flag["category"] for flag in risk_report["flags"]}
    assert "relationship" in categories
    assert "recording_surveillance" in categories
    assert "legal" in categories
