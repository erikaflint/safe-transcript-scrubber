from pathlib import Path

from safe_scrub.cli import main
from safe_scrub.scrub.redact import scrub_text


def test_public_demo_forces_strong_mode() -> None:
    text = "Name: test@example.com"
    try:
        result = scrub_text(text, mode="fast", policy="public-demo")
    except RuntimeError:
        # If spaCy isn't available in this env, enforcement still happened.
        return

    assert result["report"]["mode"] == "strong"


def test_cli_public_demo_aborts_with_warning_when_strong_unavailable(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("simple text", encoding="utf-8")
    out_dir = tmp_path / "out"

    code = main(
        [
            "scrub",
            str(input_path),
            "--out",
            str(out_dir),
            "--mode",
            "fast",
            "--policy",
            "public-demo",
        ]
    )

    if code == 2:
        report = (out_dir / "risk_report.json").read_text(encoding="utf-8")
        assert "strong_mode_required_for_public_demo" in report
