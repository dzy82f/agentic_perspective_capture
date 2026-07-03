from __future__ import annotations

import argparse
from pathlib import Path

from .perspective_capture.capture import run_capture
from .runtime.config import load_config
from .runtime.logging import configure_logging
from .runtime.openai_model import OpenAIRuntimeModel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a Perspective Pack from a question and persona library.")
    parser.add_argument("question", help="The question to capture perspectives on")
    parser.add_argument("--personas", default="personas", help="Persona directory path")
    parser.add_argument("--outputs", default="outputs", help="Output directory path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    config = load_config()
    model = OpenAIRuntimeModel(config)
    pack, output_dir = run_capture(
        question=args.question,
        persona_dir=Path(args.personas),
        outputs_dir=Path(args.outputs),
        model=model,
    )
    print("Perspective Capture completed successfully.")
    print(f"Question ID : {pack.question_id}")
    print(f"JSON        : {output_dir / 'perspective_pack.json'}")
    print(f"Markdown    : {output_dir / 'perspective_pack.md'}")
    return 0
