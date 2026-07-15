from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.market_news_dto import MarketNewsHit


class MarketNewsSearchPort(ABC):
    """상권 뉴스 의미 검색 추상 — chat(소비)과 market(구현: bge-m3+pgvector)을 잇는다.

    계약은 자연어 질의 → MarketNewsHit(임베딩은 구현 스포크의 세부).
    검색 불가(임베딩 미가용)면 빈 리스트(열화 동작).
    """

    @abstractmethod
    async def search(self, query: str, limit: int = 4) -> list[MarketNewsHit]:
        """자연어 질의로 상권 뉴스 코퍼스를 의미 검색한다."""
        ...
