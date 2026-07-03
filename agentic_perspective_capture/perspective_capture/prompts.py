from __future__ import annotations

from .models import Persona


SYSTEM_INSTRUCTION = """You are producing Module 1: Perspective Capture for Agentic Co-Emergence.

Module 1 has one narrow job: capture this persona's short initial position on the question.

Do not answer the question as an assistant.
Do not produce a report.
Do not use fixed headings.
Do not conduct discussion.
Do not synthesise.
Do not hand off.
Do not update memory.
Do not create a semantic graph.

Stay inside the persona and write naturally.
Capture the first position this persona would bring into a later discussion.
Keep it short: around 100 to 180 words.
Return plain text only."""


def build_perspective_prompt(question: str, persona: Persona) -> str:
    return f"""{SYSTEM_INSTRUCTION}

Persona source:
{persona.content}

Question:
{question}

Write this persona's short initial position only.""".strip()
