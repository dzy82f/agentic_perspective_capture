from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_perspective_capture.perspective_capture.capture import (
    allocate_question_id,
    create_perspective_pack,
    run_capture,
    validate_question,
)
from agentic_perspective_capture.perspective_capture.loader import EXPECTED_PERSONA_FILES, load_personas
from agentic_perspective_capture.perspective_capture.models import REQUIRED_SECTIONS
from agentic_perspective_capture.perspective_capture.serializers import write_json, write_markdown
from agentic_perspective_capture.runtime.model import RuntimeModel


class MockModel(RuntimeModel):
    def complete(self, prompt: str) -> str:
        return "\n".join(
            [
                f"## {section}\nMock content for {section}."
                for section in REQUIRED_SECTIONS
            ]
        )


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


def test_json_serialisation(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    path = tmp_path / "pack.json"
    write_json(pack, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["question_id"] == "Q000001"
    assert data["schema_version"] == "1.0"


def test_markdown_serialisation(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    path = tmp_path / "pack.md"
    write_markdown(pack, path)
    text = path.read_text(encoding="utf-8")
    assert "# Perspective Pack Q000001" in text
    assert "#### Core framing" in text


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
    data = pack.to_dict()
    assert "discussion" not in data


def test_no_synthesis_section(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    data = pack.to_dict()
    assert "synthesis" not in data


def test_no_handoff_data(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    data = pack.to_dict()
    assert "handoff" not in data


def test_runtime_model_interface_can_be_mocked(tmp_path: Path) -> None:
    persona_dir = make_personas(tmp_path / "personas")
    pack = create_perspective_pack("Question?", persona_dir, MockModel(), "Q000001")
    assert pack.perspectives[0].sections["Core framing"] == "Mock content for Core framing."
