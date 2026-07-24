from __future__ import annotations

from hub.app.dtos.fundamental_dto import FundamentalInsightItem
from hub.app.ports.output.fundamental_read_port import FundamentalReadPort
from stock.app.dtos.stock_history_dto import FundamentalsQuery
from stock.app.ports.input.stock_history_use_case import StockHistoryUseCase


class FundamentalReadGateway(FundamentalReadPort):
    """허브 FundamentalReadPort 구현 — stock 조회 유스케이스가 이미 만든 규칙 해석(insights)을
    허브 계약으로 옮긴다. 문장 생성(fundamental_narrator)은 stock이 소유하고 여기선 매핑만."""

    def __init__(self, use_case: StockHistoryUseCase) -> None:
        self._use_case = use_case

    async def latest_insights(self, ticker: str) -> list[FundamentalInsightItem]:
        view = await self._use_case.fundamentals(FundamentalsQuery(symbol=ticker))
        return [
            FundamentalInsightItem(key=i.key, tone=i.tone, text=i.text)
            for i in view.insights
        ]
