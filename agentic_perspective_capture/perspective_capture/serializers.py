from __future__ import annotations

import json
from pathlib import Path

from .models import PerspectivePack


def write_json(pack: PerspectivePack, path: Path) -> None:
    path.write_text(json.dumps(pack.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(pack: PerspectivePack, path: Path) -> None:
    lines: list[str] = [
        f"# Perspective Pack {pack.question_id}",
        "",
        f"**Question:** {pack.question}",
        "",
        f"**Created:** {pack.created_at}",
        "",
        "## Initial Perspectives",
        "",
    ]
    for perspective in pack.perspectives:
        lines.extend([
            f"### {perspective.persona}",
            "",
            perspective.initial_perspective.strip(),
            "",
        ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
