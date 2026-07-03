from __future__ import annotations

from pathlib import Path

from .models import Persona


EXPECTED_PERSONA_FILES = [
    "Ada.md",
    "Aletheia.md",
    "Alison.md",
    "Harry.md",
    "joan.md",
    "lyla.md",
    "Sael.md",
    "Synaia.md",
    "tenzing.md",
]


def load_personas(persona_dir: Path) -> list[Persona]:
    if not persona_dir.exists() or not persona_dir.is_dir():
        raise FileNotFoundError(f"Persona directory not found: {persona_dir}")

    missing = [name for name in EXPECTED_PERSONA_FILES if not (persona_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing persona files: {', '.join(missing)}")

    personas: list[Persona] = []
    for filename in EXPECTED_PERSONA_FILES:
        path = persona_dir / filename
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Persona file is empty: {path}")
        personas.append(Persona(name=path.stem, filename=filename, content=content))
    return personas
