from safe_scrub.scrub.redact import scrub_text


def test_speaker_names_redacted_to_speaker_tokens() -> None:
    text = """Erika Flint: Hello there.
Paul Stone: Hi.
Erika Flint: Email me at erika@example.com."""

    result = scrub_text(text, mode="fast", policy="internal")
    scrubbed = result["scrubbed_text"]
    report = result["report"]

    assert "Erika Flint:" not in scrubbed
    assert "Paul Stone:" not in scrubbed
    assert "SPEAKER_1: Hello there." in scrubbed
    assert "SPEAKER_2: Hi." in scrubbed
    assert "SPEAKER_1: Email me at [EMAIL_1]." in scrubbed

    assert report["speaker_redaction"]["speaker_lines_redacted"] == 3
    assert report["speaker_redaction"]["unique_speakers"] == 2
