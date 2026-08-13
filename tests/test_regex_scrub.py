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


def test_separator_formatted_long_number_is_caught() -> None:
    # Account/reference-shaped numbers formatted with dashes previously slipped through,
    # since the old pattern only matched unbroken runs of 8+ digits.
    text = "Your account reference number was 4485-9931-2207 if we need to look anything up."
    result = scrub_text(text, mode="fast")
    scrubbed = result["scrubbed_text"]
    report = result["report"]

    assert "4485-9931-2207" not in scrubbed
    assert "[LONG_NUMBER_1]" in scrubbed
    assert report["counts_by_label"]["LONG_NUMBER"] == 1


def test_plain_phone_number_still_labeled_as_phone_not_long_number() -> None:
    # The new LONG_NUMBER pattern also matches a 10-digit phone number by digit count alone.
    # PHONE must still win the label for a plain phone number, not get relabeled generic.
    text = "Call 415-555-1212 anytime."
    result = scrub_text(text, mode="fast")
    report = result["report"]

    assert report["counts_by_label"].get("PHONE") == 1
    assert "LONG_NUMBER" not in report["counts_by_label"]
