from __future__ import annotations

import json
import re
from pathlib import Path

from agentic_perspective_capture.runtime.model import RuntimeModel

from .loader import load_personas
from .models import PerspectivePack, PersonaPerspective, utc_now_iso
from .prompts import build_perspective_prompt
from .serializers import write_json, write_markdown

INDEX_FILE = "index.json"
QUESTION_ID_RE = re.compile(r"^Q\d{6}$")


def validate_question(question: str) -> str:
    clean = question.strip()
    if not clean:
        raise ValueError("Question must not be empty")
    return clean


def allocate_question_id(outputs_dir: Path) -> str:
    outputs_dir.mkdir(parents=True, exist_ok=True)
    index_path = outputs_dir / INDEX_FILE
    if index_path.exists():
        data = json.loads(index_path.read_text(encoding="utf-8"))
        last_question_id = int(data.get("last_question_id", 0))
    else:
        last_question_id = 0
    next_id = last_question_id + 1
    index_path.write_text(json.dumps({"last_question_id": next_id}, indent=2) + "\n", encoding="utf-8")
    return f"Q{next_id:06d}"


def clean_initial_perspective(text: str) -> str:
    """Keep Module 1 output as a short natural position, not a headed report."""
    lines = []
    for raw_line in text.strip().splitlines():
        stripped = raw_line.strip()
        if stripped.lower() in {"initial perspective", "perspective", "short initial position"}:
            continue
        if stripped.startswith("#"):
            continue
        lines.append(raw_line.rstrip())
    return "\n".join(lines).strip()


def create_perspective_pack(
    question: str,
    persona_dir: Path,
    model: RuntimeModel,
    question_id: str,
) -> PerspectivePack:
    clean_question = validate_question(question)
    if not QUESTION_ID_RE.match(question_id):
        raise ValueError(f"Invalid question ID: {question_id}")

    personas = load_personas(persona_dir)
    perspectives: list[PersonaPerspective] = []
    for persona in personas:
        prompt = build_perspective_prompt(clean_question, persona)
        response = model.complete(prompt)
        perspective = PersonaPerspective(
            persona=persona.name,
            source_file=persona.filename,
            initial_perspective=clean_initial_perspective(response),
        )
        perspective.validate()
        perspectives.append(perspective)

    return PerspectivePack(
        schema_version="1.1",
        module="agentic_perspective_capture",
        question_id=question_id,
        question=clean_question,
        created_at=utc_now_iso(),
        perspectives=perspectives,
    )


def run_capture(
    question: str,
    persona_dir: Path,
    outputs_dir: Path,
    model: RuntimeModel,
) -> tuple[PerspectivePack, Path]:
    question_id = allocate_question_id(outputs_dir)
    output_dir = outputs_dir / question_id
    output_dir.mkdir(parents=True, exist_ok=False)
    pack = create_perspective_pack(question, persona_dir, model, question_id)
    write_json(pack, output_dir / "perspective_pack.json")
    write_markdown(pack, output_dir / "perspective_pack.md")
    return pack, output_dir
