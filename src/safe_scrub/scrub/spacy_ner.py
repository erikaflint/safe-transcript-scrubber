from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_ENTITY_LABELS = {"PERSON", "ORG", "GPE", "LOC", "DATE"}


@dataclass(frozen=True)
class SpacyEntity:
    start: int
    end: int
    label: str
    text: str


def detect_spacy_entities(text: str) -> tuple[list[SpacyEntity], list[str]]:
    try:
        import spacy  # type: ignore

        nlp = spacy.load("en_core_web_sm")
    except Exception:
        return [], ["spacy_unavailable"]

    doc = nlp(text)
    entities: list[SpacyEntity] = []
    for ent in doc.ents:
        if ent.label_ in SUPPORTED_ENTITY_LABELS:
            entities.append(
                SpacyEntity(start=ent.start_char, end=ent.end_char, label=ent.label_, text=ent.text)
            )

    return entities, []
