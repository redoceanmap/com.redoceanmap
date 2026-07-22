from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date


class EarningsCalendarPort(ABC):
    """실적 발표일 조회 아웃바운드 포트 — 어닝 veto(±2일 관망·백테스트 표본 제외)의 재료.

    MarketDataPort와 분리한 이유: 시세 경로(analyze/quote/history)에 어닝 의존이
    새지 않게(ISP), 그리고 capture 조립이 시세 라이브 폴백은 끄되 어닝만 켤 수 있게.
    """

    @abstractmethod
    async def earnings_dates(self, symbol: str) -> list[date]:
        """알려진 실적 발표일(과거+예정, 벤더 제공 범위 내). 실패·미지원 종목은
        빈 리스트 — 호출부는 무-veto로 열화한다(예측 자체를 막지 않는다)."""
        ...
