import json
from pathlib import Path

from safe_scrub.synth.generator import generate_batch, generate_transcript


def test_generate_transcript_is_deterministic_for_same_seed() -> None:
    first_text, first_meta = generate_transcript(
        template="coaching",
        risk="medium",
        seed=123,
        fmt="txt",
        min_turns=20,
        max_turns=20,
    )
    second_text, second_meta = generate_transcript(
        template="coaching",
        risk="medium",
        seed=123,
        fmt="txt",
        min_turns=20,
        max_turns=20,
    )

    assert first_text == second_text
    assert first_meta == second_meta


def test_generate_batch_manifest_and_files_are_deterministic(tmp_path: Path) -> None:
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"

    generate_batch(
        count=2,
        out_dir=out_a,
        fmt="txt",
        template="stress_reset",
        seed=123,
        risk="low",
        min_turns=12,
        max_turns=12,
    )
    generate_batch(
        count=2,
        out_dir=out_b,
        fmt="txt",
        template="stress_reset",
        seed=123,
        risk="low",
        min_turns=12,
        max_turns=12,
    )

    assert (out_a / "synthetic_001.txt").read_text(encoding="utf-8") == (
        out_b / "synthetic_001.txt"
    ).read_text(encoding="utf-8")
    assert json.loads((out_a / "manifest.json").read_text(encoding="utf-8")) == json.loads(
        (out_b / "manifest.json").read_text(encoding="utf-8")
    )
