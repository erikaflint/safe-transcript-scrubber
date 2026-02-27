from safe_scrub.io import _extract_vtt_text
from safe_scrub.scrub.redact import scrub_text


def test_vtt_codes_are_removed_before_scrubbing() -> None:
    vtt = """WEBVTT

1
00:00:01.000 --> 00:00:03.000
Call me at 415-555-1212.

2
00:00:04.000 --> 00:00:06.000 align:start position:0%
Email jane@example.com now.
"""

    plain = _extract_vtt_text(vtt)
    assert "WEBVTT" not in plain
    assert "-->" not in plain
    assert "00:00:01.000" not in plain
    assert plain == "Call me at 415-555-1212.\nEmail jane@example.com now."

    result = scrub_text(plain, mode="fast")
    scrubbed = result["scrubbed_text"]

    assert "415-555-1212" not in scrubbed
    assert "jane@example.com" not in scrubbed
    assert "[PHONE_1]" in scrubbed
    assert "[EMAIL_1]" in scrubbed
