from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.stock_forecast_dto import ForecastQuery, StockForecastView


class StockForecastUseCase(ABC):
    """저장 일봉 워크포워드 백테스트로 상승 확률·예측 밴드를 계산 — 프론트 차트·확률 카드용."""

    @abstractmethod
    async def forecast(self, query: ForecastQuery) -> StockForecastView:
        """미보유 심볼·봉 부족은 MarketDataUnavailableError(HTTP 변환은 라우터 몫)."""
        ...
