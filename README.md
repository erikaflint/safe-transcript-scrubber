# Safe Transcript Scrubber

A privacy-first, local-first CLI tool for scrubbing sensitive data from text transcripts.

## Purpose

`safe-transcript-scrubber` ingests a transcript (`.txt` or `.vtt`) and produces:

- `scrubbed.txt` with detected PII replaced by consistent placeholders
- `redaction_report.json` with summary counts and metadata
- `risk_report.json` with high-risk content flags and score

## Local-first privacy posture

- Processing is done locally on your machine.
- No network calls are required for the default (`fast`) mode.
- `strong` mode can use local spaCy NER if installed.

## What it does not promise

This tool does **not** guarantee perfect anonymization. It is a pragmatic first-pass scrubber and may miss or over-redact content.

## Install

```bash
cd safe-transcript-scrubber
python -m pip install -e .
```

Optional strong-mode support:

```bash
python -m pip install -e .[spacy]
python -m spacy download en_core_web_sm
```

## Usage

Fast mode (regex-only):

```bash
python -m safe_scrub scrub examples/synthetic_transcript_1.txt --out out --mode fast
```

Strong mode (regex + optional spaCy NER):

```bash
python -m safe_scrub scrub examples/synthetic_transcript_1.txt --out out --mode strong
```

Internal policy (default):

```bash
python -m safe_scrub scrub examples/synthetic_transcript_1.txt --out out --mode fast --policy internal
```

Public demo policy (adds optional generalization pass):

```bash
python -m safe_scrub scrub examples/synthetic_transcript_1.txt --out out_demo --mode fast --policy public-demo
```

`public-demo` enforces stronger safety:
- it forces strong-mode processing
- if spaCy/model is unavailable, execution aborts and `risk_report.json` includes
  `strong_mode_required_for_public_demo`

VTT input (timing/cue codes are stripped before scrubbing):

```bash
python -m safe_scrub scrub examples/audio_transcript.vtt --out out_vtt --mode fast
```

If spaCy or the model is unavailable, strong mode gracefully falls back to regex-only and reports `spacy_unavailable` in `redaction_report.json`.

## Output files

- `out/redaction_report.json`
- `out/risk_report.json`
- `out/scrubbed.txt` when `--policy internal`
- `out/scrubbed_internal.txt` when `--policy public-demo`
- `out/scrubbed_public.txt` when `--policy public-demo`

## Generating Demo-Safe Transcripts

Use the built-in synthetic generator to create realistic demo/test transcripts without using any real client data.

```bash
python -m safe_scrub synth --count 3 --out examples/synth --format txt --template coaching --seed 1 --risk medium
```

VTT output:

```bash
python -m safe_scrub synth --count 2 --out examples/synth_vtt --format vtt --template stress_reset --seed 42 --risk low
```

Options:
- `--template coaching|stress_reset`
- `--risk low|medium|high`
- `--min-turns 80 --max-turns 160`
- `--seed` for deterministic output

Risk levels:
- `low`: avoids high-risk keywords entirely
- `medium`: injects a small number of risk phrases to exercise the risk layer
- `high`: injects multiple risk phrases across categories

Generated output includes:
- `synthetic_001.txt` or `synthetic_001.vtt`
- additional numbered files
- `manifest.json` with template, risk, seed, topic, and turn count metadata

## High-risk content layer

The tool flags potentially sensitive high-risk content by keyword/category and computes a simple risk score.

- Categories include: `relationship`, `recording_surveillance`, `legal`, `medical_or_clinical`, `high_specificity_markers`
- `risk_report.json` includes:
  - `risk_score`
  - `risk_level` (`low` | `medium` | `high`)
  - `flags` as `{category, match, count}`
  - `recommendation` (`ok` | `review` | `human_review`)
  - `policy_applied`
  - `generalizations_applied` (empty in `internal`)
- In `public-demo` policy, conservative phrase-level generalizations are applied and written to `scrubbed_public.txt`.

## Tests

```bash
python -m pip install -e .[test]
pytest
```
