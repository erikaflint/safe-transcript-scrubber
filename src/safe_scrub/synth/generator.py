from __future__ import annotations

import random
from pathlib import Path
from safe_scrub.io import write_json, write_text
from safe_scrub.scrub.high_risk import CATEGORY_KEYWORDS
from safe_scrub.synth.formatters import format_txt, format_vtt
from safe_scrub.synth.phrasebanks import (
    CHALLENGES,
    CLOSERS,
    FEELINGS,
    FILLERS,
    GOALS,
    INSIGHTS,
    NEUTRAL_OPENERS,
    RISK_PHRASES,
    SETTLE_LINES,
    TECHNIQUES,
    TOPICS,
    WINS,
)
from safe_scrub.synth.templates import get_template


def _choose(rng: random.Random, items: list[str]) -> str:
    return items[rng.randrange(len(items))]


def _risk_injections(rng: random.Random, risk: str) -> list[str]:
    if risk == "low":
        return []
    categories = list(RISK_PHRASES.keys())
    rng.shuffle(categories)
    num_categories = 2 if risk == "medium" else min(5, 3 + rng.randrange(3))
    chosen = categories[:num_categories]
    injections: list[str] = []
    for category in chosen:
        phrase = _choose(rng, RISK_PHRASES[category])
        keyword_pool = CATEGORY_KEYWORDS[category]
        if not any(keyword in phrase.lower() for keyword in keyword_pool):
            phrase = f"{phrase} and {keyword_pool[0]} kept coming to mind"
        injections.append(phrase)
    return injections


def _greeting_lines(rng: random.Random, template_name: str) -> list[str]:
    style = "Take one easy breath with me." if template_name == "stress_reset" else "We can start small today."
    return [
        f"THERAPIST: {_choose(rng, NEUTRAL_OPENERS)}",
        f"CLIENT: {_choose(rng, FILLERS).capitalize()}, I'm feeling {_choose(rng, FEELINGS)}.",
        f"THERAPIST: {style}",
        f"CLIENT: {_choose(rng, SETTLE_LINES)}",
    ]


def _working_lines(rng: random.Random) -> list[str]:
    return [
        "THERAPIST: Before we get into the hard part, what's working?",
        f"CLIENT: {_choose(rng, WINS)}, and that helped a little.",
        f"THERAPIST: Good. That points toward {_choose(rng, GOALS)}.",
        f"CLIENT: Yeah, {_choose(rng, GOALS)} still feels important.",
    ]


def _challenge_lines(rng: random.Random, injections: list[str]) -> list[str]:
    lines = [
        "THERAPIST: What's the part that still catches you?",
        f"CLIENT: {_choose(rng, CHALLENGES)}.",
        "THERAPIST: When that happens, what do you notice first?",
        f"CLIENT: Usually I feel {_choose(rng, FEELINGS)}, then I try to push through it.",
    ]
    for phrase in injections:
        lines.extend(
            [
                f"CLIENT: {phrase}.",
                "THERAPIST: Okay, let's make room for that without letting it run the whole session.",
            ]
        )
    return lines


def _insight_lines(rng: random.Random) -> list[str]:
    return [
        "THERAPIST: What are you seeing differently now?",
        f"CLIENT: I think {_choose(rng, INSIGHTS)}.",
        "THERAPIST: That sounds more workable than trying to fix everything at once.",
        "CLIENT: Yeah, it feels more honest and a little calmer.",
    ]


def _technique_lines(rng: random.Random, template_name: str) -> list[str]:
    technique = _choose(rng, TECHNIQUES[template_name])
    if template_name == "stress_reset":
        guidance = f"Let's try a {technique} and keep your attention in the body."
    else:
        guidance = f"Let's practice a quick {technique} so the next step feels real."
    return [
        f"THERAPIST: {guidance}",
        "CLIENT: Okay, I'm here.",
        "THERAPIST: Notice one breath in, one breath out, and let the pace soften.",
        "CLIENT: Mm-hm, that already gives me a little more space.",
    ]


def _next_step_lines(rng: random.Random) -> list[str]:
    return [
        "THERAPIST: What's one next step that feels realistic?",
        f"CLIENT: I can aim for {_choose(rng, GOALS)} and keep it simple.",
        "THERAPIST: Good. Keep it measurable and kind.",
        "CLIENT: Yeah, that feels possible.",
    ]


def _closing_lines(rng: random.Random) -> list[str]:
    return [
        f"THERAPIST: {_choose(rng, CLOSERS)}",
        "CLIENT: Thank you, that feels steadier.",
        "THERAPIST: We'll pick up from there next time.",
        "CLIENT: Sounds good.",
    ]


def _filler_exchange(rng: random.Random, template_name: str) -> list[str]:
    therapist_line = (
        "THERAPIST: Stay with the sensation for one beat longer."
        if template_name == "stress_reset"
        else "THERAPIST: What's the smallest true thing you can say about it?"
    )
    client_line = (
        f"CLIENT: {_choose(rng, FILLERS).capitalize()}, it feels {_choose(rng, FEELINGS)} but not impossible."
    )
    return [therapist_line, client_line]


def generate_transcript(
    *,
    template: str,
    risk: str,
    seed: int,
    fmt: str,
    min_turns: int,
    max_turns: int,
) -> tuple[str, dict[str, object]]:
    if fmt not in {"txt", "vtt"}:
        raise ValueError(f"Unsupported format: {fmt}")
    if risk not in {"low", "medium", "high"}:
        raise ValueError(f"Unsupported risk level: {risk}")
    if min_turns > max_turns:
        raise ValueError("min_turns must be <= max_turns")

    spec = get_template(template)
    rng = random.Random(seed)
    topic = _choose(rng, TOPICS)
    target_turns = rng.randint(min_turns, max_turns)
    injections = _risk_injections(rng, risk)

    sections = [
        _greeting_lines(rng, spec.name),
        _working_lines(rng),
        _challenge_lines(rng, injections),
        _insight_lines(rng),
        _technique_lines(rng, spec.name),
        _next_step_lines(rng),
        _closing_lines(rng),
    ]

    lines: list[str] = []
    for section in sections:
        lines.extend(section)

    while len(lines) < target_turns:
        insert_at = max(4, min(len(lines) - 4, len(lines) // 2))
        lines[insert_at:insert_at] = _filler_exchange(rng, spec.name)

    lines = lines[:target_turns]
    rendered = format_txt(lines) if fmt == "txt" else format_vtt(lines)
    metadata = {
        "template": template,
        "risk": risk,
        "seed": seed,
        "topic": topic,
        "turns": len(lines),
    }
    return rendered, metadata


def generate_batch(
    *,
    count: int,
    out_dir: str | Path,
    fmt: str,
    template: str,
    seed: int,
    risk: str,
    min_turns: int,
    max_turns: int,
) -> list[dict[str, object]]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    for index in range(1, count + 1):
        transcript_seed = seed + index - 1
        content, metadata = generate_transcript(
            template=template,
            risk=risk,
            seed=transcript_seed,
            fmt=fmt,
            min_turns=min_turns,
            max_turns=max_turns,
        )
        filename = f"synthetic_{index:03d}.{fmt}"
        write_text(output_dir / filename, content)
        manifest.append({"filename": filename, **metadata})

    write_json(output_dir / "manifest.json", manifest)
    return manifest
