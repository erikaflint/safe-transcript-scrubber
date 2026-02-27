from safe_scrub.scrub.redact import scrub_text


def test_email_and_phone_replaced_with_placeholders() -> None:
    text = "Email me at jane.doe@example.com or call 415-555-1212."
    result = scrub_text(text, mode="fast")
    scrubbed = result["scrubbed_text"]
    report = result["report"]

    assert "jane.doe@example.com" not in scrubbed
    assert "415-555-1212" not in scrubbed
    assert "[EMAIL_1]" in scrubbed
    assert "[PHONE_1]" in scrubbed

    assert report["counts_by_label"]["EMAIL"] == 1
    assert report["counts_by_label"]["PHONE"] == 1
    assert report["counts_by_source"]["regex"] >= 2
