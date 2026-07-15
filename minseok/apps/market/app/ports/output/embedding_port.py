from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """텍스트 임베딩 아웃바운드 포트(pgvector 저장·검색용). 구현은 어댑터가 제공."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """검색 질의 등 단건 임베딩."""
        ...

    @abstractmethod
    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        """적재 배치 임베딩 — HTTP 1콜로 여러 건 처리."""
        ...
