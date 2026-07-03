from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

FORBIDDEN_TOP_LEVEL_KEYS = {"discussion", "synthesis", "handoff", "memory_update", "semantic_graph"}


@dataclass(frozen=True)
class Persona:
    name: str
    filename: str
    content: str


@dataclass(frozen=True)
class PersonaPerspective:
    persona: str
    source_file: str
    initial_perspective: str

    def validate(self) -> None:
        if not self.initial_perspective.strip():
            raise ValueError(f"Perspective for {self.persona} is empty")


@dataclass(frozen=True)
class PerspectivePack:
    question_id: str
    question: str
    created_at: str
    schema_version: str
    module: str
    perspectives: list[PersonaPerspective] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "module": self.module,
            "question_id": self.question_id,
            "question": self.question,
            "created_at": self.created_at,
            "perspectives": [
                {
                    "persona": p.persona,
                    "source_file": p.source_file,
                    "initial_perspective": p.initial_perspective,
                }
                for p in self.perspectives
            ],
        }
        if FORBIDDEN_TOP_LEVEL_KEYS.intersection(data):
            raise ValueError("Perspective Pack contains forbidden module data")
        return data


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
