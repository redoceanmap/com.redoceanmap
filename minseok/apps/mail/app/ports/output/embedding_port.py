from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """텍스트 → 임베딩 벡터 아웃바운드 포트. 구현(Ollama bge-m3 등)은 어댑터가 제공."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...
