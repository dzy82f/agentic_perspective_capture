from __future__ import annotations

from abc import ABC, abstractmethod


class RuntimeModel(ABC):
    """Provider-agnostic model interface owned by the runtime."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Return a text completion for the supplied prompt."""
        raise NotImplementedError
