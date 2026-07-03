from __future__ import annotations

from .models import Persona, REQUIRED_SECTIONS


def build_perspective_prompt(question: str, persona: Persona) -> str:
    section_list = "\n".join(f"## {section}" for section in REQUIRED_SECTIONS)
    return f"""You are producing Module 1: Perspective Capture for Agentic Co-Emergence.

Task:
Capture this persona's independent initial framing of the question.
Do not answer the question directly.
Do not discuss with other personas.
Do not synthesise.
Do not hand off.
Do not update memory.
Do not create a semantic graph.

Question:
{question}

Persona source:
{persona.content}

Return Markdown with exactly these headings and no additional headings:
{section_list}
""".strip()
