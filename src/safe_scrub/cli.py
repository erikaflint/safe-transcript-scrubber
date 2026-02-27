from __future__ import annotations

import argparse
from pathlib import Path

from safe_scrub.io import read_transcript, write_json, write_text
from safe_scrub.scrub.redact import scrub_text
from safe_scrub.synth.generator import generate_batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="safe_scrub")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scrub_parser = subparsers.add_parser("scrub", help="Scrub transcript text")
    scrub_parser.add_argument("input_path", help="Path to input transcript (.txt or .vtt)")
    scrub_parser.add_argument("--out", required=True, dest="output_dir", help="Output directory")
    scrub_parser.add_argument("--mode", choices=["fast", "strong"], default="fast")
    scrub_parser.add_argument(
        "--policy",
        choices=["internal", "public-demo"],
        default="internal",
        help="Risk policy mode",
    )

    synth_parser = subparsers.add_parser("synth", help="Generate demo-safe synthetic transcripts")
    synth_parser.add_argument("--count", type=int, required=True, help="Number of transcripts to create")
    synth_parser.add_argument("--out", required=True, dest="output_dir", help="Output directory")
    synth_parser.add_argument("--format", choices=["txt", "vtt"], required=True, dest="fmt")
    synth_parser.add_argument("--template", choices=["coaching", "stress_reset"], required=True)
    synth_parser.add_argument("--seed", type=int, default=0)
    synth_parser.add_argument("--risk", choices=["low", "medium", "high"], default="low")
    synth_parser.add_argument("--min-turns", type=int, default=80)
    synth_parser.add_argument("--max-turns", type=int, default=160)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scrub":
        input_path = Path(args.input_path)
        output_dir = Path(args.output_dir)
        text = read_transcript(input_path)

        try:
            result = scrub_text(text=text, mode=args.mode, policy=args.policy)
        except RuntimeError as exc:
            if str(exc) == "strong_mode_required_for_public_demo":
                write_json(
                    output_dir / "risk_report.json",
                    {
                        "policy_applied": args.policy,
                        "warnings": ["strong_mode_required_for_public_demo"],
                        "status": "aborted",
                    },
                )
                return 2
            raise

        if args.policy == "public-demo" and result["scrubbed_public_text"] is not None:
            write_text(output_dir / "scrubbed_internal.txt", result["scrubbed_text"])
            write_text(output_dir / "scrubbed_public.txt", result["scrubbed_public_text"])
        else:
            write_text(output_dir / "scrubbed.txt", result["scrubbed_text"])
        write_json(output_dir / "redaction_report.json", result["report"])
        write_json(output_dir / "risk_report.json", result["risk_report"])
    elif args.command == "synth":
        generate_batch(
            count=args.count,
            out_dir=args.output_dir,
            fmt=args.fmt,
            template=args.template,
            seed=args.seed,
            risk=args.risk,
            min_turns=args.min_turns,
            max_turns=args.max_turns,
        )

    return 0
