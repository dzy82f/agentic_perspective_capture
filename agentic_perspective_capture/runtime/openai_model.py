from __future__ import annotations

from .config import RuntimeConfig
from .model import RuntimeModel


class OpenAIRuntimeModel(RuntimeModel):
    """OpenAI implementation of the runtime model interface."""

    def __init__(self, config: RuntimeConfig) -> None:
        if not config.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        from openai import OpenAI

        self._client = OpenAI(api_key=config.api_key)
        self._model_name = config.model_name

    def complete(self, prompt: str) -> str:
        # Do not pass temperature. Some GPT-5 models reject unsupported parameters.
        response = self._client.responses.create(
            model=self._model_name,
            input=prompt,
        )
        return response.output_text.strip()
