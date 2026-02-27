from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from safe_scrub import __version__
from safe_scrub.scrub.high_risk import analyze_high_risk, apply_generalizations
from safe_scrub.scrub.placeholders import PlaceholderAssigner
from safe_scrub.scrub.regex_rules import REGEX_RULES
from safe_scrub.scrub.speakers import anonymize_speaker_prefixes
from safe_scrub.scrub.spacy_ner import detect_spacy_entities


@dataclass(frozen=True)
class Finding:
    start: int
    end: int
    label: str
    source: str
    text: str

    @property
    def length(self) -> int:
        return self.end - self.start


def _regex_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule in REGEX_RULES:
        for match in rule.pattern.finditer(text):
            findings.append(
                Finding(
                    start=match.start(),
                    end=match.end(),
                    label=rule.label,
                    source="regex",
                    text=match.group(0),
                )
            )
    return findings


def _spacy_findings(text: str) -> tuple[list[Finding], list[str]]:
    entities, warnings = detect_spacy_entities(text)
    findings = [
        Finding(start=e.start, end=e.end, label=e.label, source="spacy", text=e.text)
        for e in entities
    ]
    return findings, warnings


def _resolve_overlaps(findings: list[Finding], text_length: int) -> list[Finding]:
    # Keep longest spans first; then keep only non-overlapping spans.
    sorted_findings = sorted(findings, key=lambda f: (-f.length, f.start, f.end))
    occupied = [False] * text_length
    selected: list[Finding] = []

    for finding in sorted_findings:
        if finding.start < 0 or finding.end > text_length or finding.start >= finding.end:
            continue
        if any(occupied[pos] for pos in range(finding.start, finding.end)):
            continue
        for pos in range(finding.start, finding.end):
            occupied[pos] = True
        selected.append(finding)

    return sorted(selected, key=lambda f: f.start)


def _apply_replacements(text: str, findings: list[Finding]) -> str:
    assigner = PlaceholderAssigner()
    output = text

    placeholder_by_span: dict[tuple[int, int, str], str] = {}
    for finding in sorted(findings, key=lambda f: f.start):
        key = (finding.start, finding.end, finding.label)
        placeholder_by_span[key] = assigner.assign(finding.label, finding.text)

    for finding in sorted(findings, key=lambda f: f.start, reverse=True):
        key = (finding.start, finding.end, finding.label)
        placeholder = placeholder_by_span[key]
        output = output[: finding.start] + placeholder + output[finding.end :]

    return output


def scrub_text(text: str, mode: str, policy: str = "internal") -> dict[str, object]:
    if mode not in {"fast", "strong"}:
        raise ValueError(f"Unsupported mode: {mode}")
    if policy not in {"internal", "public-demo"}:
        raise ValueError(f"Unsupported policy: {policy}")

    effective_mode = mode
    if policy == "public-demo":
        # Public-demo is high-safety mode; always run the strong pipeline.
        effective_mode = "strong"

    speaker_scrubbed_text, speaker_stats = anonymize_speaker_prefixes(text)
    findings = _regex_findings(speaker_scrubbed_text)
    warnings: list[str] = []

    if effective_mode == "strong":
        spacy_findings, spacy_warnings = _spacy_findings(speaker_scrubbed_text)
        findings.extend(spacy_findings)
        warnings.extend(spacy_warnings)
        if policy == "public-demo" and "spacy_unavailable" in spacy_warnings:
            raise RuntimeError("strong_mode_required_for_public_demo")

    resolved = _resolve_overlaps(findings, len(speaker_scrubbed_text))
    scrubbed_text = _apply_replacements(speaker_scrubbed_text, resolved)

    counts_by_label = dict(Counter(f.label for f in resolved))
    counts_by_source = dict(Counter(f.source for f in resolved))

    analysis = analyze_high_risk(scrubbed_text)
    risk_report: dict[str, object] = {
        "risk_score": analysis["risk_score"],
        "risk_level": analysis["risk_level"],
        "total_flags": analysis["total_flags"],
        "counts_by_category": analysis["counts_by_category"],
        "flags": analysis["flags"],
        "recommendation": analysis["recommendation"],
        "policy_applied": policy,
        "generalizations_applied": [],
    }
    public_text: str | None = None
    if policy == "public-demo":
        public_text, applied = apply_generalizations(scrubbed_text, analysis["matches"])
        risk_report["generalizations_applied"] = applied

    report = {
        "version": __version__,
        "mode": effective_mode,
        "policy": policy,
        "total_findings": len(resolved),
        "counts_by_label": counts_by_label,
        "counts_by_source": counts_by_source,
        "speaker_redaction": speaker_stats,
        "warnings": warnings,
    }

    return {
        "scrubbed_text": scrubbed_text,
        "scrubbed_public_text": public_text,
        "report": report,
        "risk_report": risk_report,
    }
