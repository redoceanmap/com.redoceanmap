from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.stock_forecast_dto import StockForecastSummary


class StockForecastPort(ABC):
    """주식 확률·예측 요약 조회 계약 — chat(소비)과 stock(구현)을 잇는다.

    분석(StockAnalysisPort)과 별개인 조회 전용. chat이 종목 답변의 "결론 한 줄"에
    페이지와 같은 과거 통계 재료를 쓰도록 준다. 수집 일봉이 없어 산출 불가하면 None(열화).
    """

    @abstractmethod
    async def forecast(self, ticker: str) -> StockForecastSummary | None:
        """해석된 종목 코드의 확률 요약. 산출 불가(미수집·표본 부족)면 None."""
        raise NotImplementedError
