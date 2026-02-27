from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateSpec:
    name: str
    greeting_style: str
    challenge_style: str
    technique_style: str
    closing_style: str


TEMPLATES = {
    "coaching": TemplateSpec(
        name="coaching",
        greeting_style="practical",
        challenge_style="reflective",
        technique_style="future_oriented",
        closing_style="action",
    ),
    "stress_reset": TemplateSpec(
        name="stress_reset",
        greeting_style="somatic",
        challenge_style="body_first",
        technique_style="grounding",
        closing_style="gentle",
    ),
}


def get_template(name: str) -> TemplateSpec:
    if name not in TEMPLATES:
        raise ValueError(f"Unsupported template: {name}")
    return TEMPLATES[name]
