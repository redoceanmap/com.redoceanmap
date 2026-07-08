from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.analyst_dto import AnalystQuery, AnalystResponse


class AnalystUseCase(ABC):
    """주식 분석 (stock) 유스케이스 — 지표+뉴스 결합 분석 — 백테스트로 검증되는 신호만."""

    @abstractmethod
    async def introduce_myself(self, query: AnalystQuery) -> AnalystResponse:
        """주식 분석 (stock)의 자기소개 메소드."""
        ...
