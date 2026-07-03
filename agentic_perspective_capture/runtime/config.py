from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


@dataclass(frozen=True)
class RuntimeConfig:
    model_name: str
    api_key: str | None


def load_config(env_path: Path | None = None) -> RuntimeConfig:
    if load_dotenv is not None:
        load_dotenv(env_path)
    return RuntimeConfig(
        model_name=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
