from __future__ import annotations

from core.llm.llm_orchestrator import llm_orchestrator
from market.app.ports.output.embedding_port import EmbeddingPort


class OllamaEmbeddingAdapter(EmbeddingPort):
    """bge-m3(1024차원) 임베딩 — LLM 오케스트레이터로 수렴(stock·mail 앱과 동일 패턴)."""

    async def embed(self, text: str) -> list[float]:
        return await llm_orchestrator.embed(text)

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        return await llm_orchestrator.embed_many(texts)
