from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.fundamental_dto import FundamentalInsightItem


class FundamentalReadPort(ABC):
    """펀더멘털 가치·체력 해석 조회 계약 — chat(소비)과 stock(구현)을 잇는다.

    저장(FundamentalStoragePort)과 별개인 조회 전용. chat이 종목 답변에 "이 회사 싼가/튼튼한가"
    한 줄을 붙이도록 규칙 해석(fundamental_narrator) 문장을 준다. 수집분이 없으면 빈 리스트(열화).
    """

    @abstractmethod
    async def latest_insights(self, ticker: str) -> list[FundamentalInsightItem]:
        """해석된 종목 코드의 최신 가치·체력 해석 문장(dart 우선 병합). 없으면 빈 리스트."""
        raise NotImplementedError
