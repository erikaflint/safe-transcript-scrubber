from safe_scrub.scrub.redact import scrub_text


def test_overlap_resolution_prefers_longer_span_and_avoids_mangling() -> None:
    text = "Call me at 4155551212 now."
    result = scrub_text(text, mode="fast")
    scrubbed = result["scrubbed_text"]
    report = result["report"]

    assert scrubbed == "Call me at [PHONE_1] now."
    assert report["counts_by_label"].get("PHONE") == 1
    assert report["counts_by_label"].get("LONG_NUMBER", 0) == 0
