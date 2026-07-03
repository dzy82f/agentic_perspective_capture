from __future__ import annotations

import json
import re
from pathlib import Path

from agentic_perspective_capture.runtime.model import RuntimeModel

from .loader import load_personas
from .models import PerspectivePack, PersonaPerspective, REQUIRED_SECTIONS, utc_now_iso
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


def parse_markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current
        if current is not None:
            sections[current] = "\n".join(buffer).strip()
        buffer = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        heading = None
        for section in REQUIRED_SECTIONS:
            if line in {f"## {section}", f"### {section}", f"#### {section}", section}:
                heading = section
                break
        if heading:
            flush()
            current = heading
        else:
            if current is not None:
                buffer.append(raw_line)
    flush()

    for section in REQUIRED_SECTIONS:
        sections.setdefault(section, "")
    return sections


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
            sections=parse_markdown_sections(response),
        )
        perspective.validate()
        perspectives.append(perspective)

    return PerspectivePack(
        schema_version="1.0",
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
