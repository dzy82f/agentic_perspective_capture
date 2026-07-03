from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_perspective_capture.perspective_capture.capture import (
    allocate_question_id,
    clean_initial_perspective,
    create_perspective_pack,
    run_capture,
    validate_question,
)
from agentic_perspective_capture.perspective_capture.loader import EXPECTED_PERSONA_FILES, load_personas
from agentic_perspective_capture.perspective_capture.serializers import write_json, write_markdown
from agentic_perspective_capture.runtime.model import RuntimeModel


class MockModel(RuntimeModel):
    def complete(self, prompt: str) -> str:
        return "This is my short initial position. I am not answering the question; I am stating how I first see it."


def make_personas(path: Path) -> Path:
    path.mkdir()
    for filename in EXPECTED_PERSONA_FILES:
        (path / filename).write_text(f"# {filename}\nPersona body.", encoding="utf-8")
    return path


def test_persona_loading(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    personas = load_personas(persona_dir)
    assert len(personas) == len(EXPECTED_PERSONA_FILES)


def test_deterministic_persona_order(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    personas = load_personas(persona_dir)
    assert [p.filename for p in personas] == EXPECTED_PERSONA_FILES


def test_empty_question_failure() -> None:
    with pytest.raises(ValueError):
        validate_question("   ")


def test_missing_persona_directory_failure(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_personas(tmp_path / "missing")


def test_perspective_pack_creation(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("What is philosophy?", persona_dir, MockModel(), "Q000001")
    assert pack.question_id == "Q000001"
    assert len(pack.perspectives) == len(EXPECTED_PERSONA_FILES)
    assert pack.perspectives[0].initial_perspective


def test_json_serialisation(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    path = tmp_path / "pack.json"
    write_json(pack, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["question_id"] == "Q000001"
    assert data["schema_version"] == "1.1"
    assert "initial_perspective" in data["perspectives"][0]
    assert "sections" not in data["perspectives"][0]


def test_markdown_serialisation(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    path = tmp_path / "pack.md"
    write_markdown(pack, path)
    text = path.read_text(encoding="utf-8")
    assert "# Perspective Pack Q000001" in text
    assert "## Initial Perspectives" in text
    assert "#### Core framing" not in text


def test_automatic_question_id_creation(tmp_path: Path) -> None:
    outputs = tmp_path / "outputs"
    assert allocate_question_id(outputs) == "Q000001"
    assert allocate_question_id(outputs) == "Q000002"


def test_output_directory_creation(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack, output_dir = run_capture("Question?", persona_dir, tmp_path / "outputs", MockModel())
    assert pack.question_id == "Q000001"
    assert output_dir.exists()
    assert (output_dir / "perspective_pack.json").exists()
    assert (output_dir / "perspective_pack.md").exists()


def test_no_discussion_section(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    assert "discussion" not in pack.to_dict()


def test_no_synthesis_section(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    assert "synthesis" not in pack.to_dict()


def test_no_handoff_data(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    assert "handoff" not in pack.to_dict()


def test_runtime_model_interface_can_be_mocked(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    assert pack.perspectives[0].initial_perspective.startswith("This is my short initial position")


def test_prompt_rejects_fixed_headings(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    personas = load_personas(persona_dir)
    from agentic_perspective_capture.perspective_capture.prompts import build_perspective_prompt
    prompt = build_perspective_prompt("Question?", personas[0])
    assert "Do not use fixed headings" in prompt
    assert "Core framing" not in prompt


def test_clean_initial_perspective_removes_heading_noise() -> None:
    assert clean_initial_perspective("# Perspective\n\nThis is the text.") == "This is the text."
