from __future__ import annotations

import logging

from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.app.ports.input.stock_use_case import StockUseCase
from stock.app.ports.output.market_data_port import MarketDataPort
from stock.app.ports.output.news_repository import NewsRepositoryPort
from stock.app.ports.output.sentiment_port import SentimentPort
from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.services.outlook_predictor import OutlookPredictor
from stock.domain.value_objects.market_values import Symbol

logger = logging.getLogger(__name__)


class StockInteractor(StockUseCase):
    """주식 분석 대장(오케스트레이터).

    시세·지표·뉴스를 모으고, 뉴스 감성만 LLM(SentimentPort→EXAONE)에 위임한 뒤
    결정론적 예측기로 방향 전망을 낸다. 매매 추천은 하지 않고 구조화된 분석만 반환한다.
    최종 사용자 서술은 소비자(chat)가 담당한다(허브 경유, Phase B 예정).
    """

    def __init__(
        self,
        market_data: MarketDataPort,
        sentiment: SentimentPort,
        predictor: OutlookPredictor,
        config: AnalysisConfig,
        news: NewsRepositoryPort | None = None,
    ) -> None:
        self._market_data = market_data
        self._sentiment = sentiment
        self._predictor = predictor
        self._config = config
        self._news = news

    async def analyze(self, symbol: Symbol, name: str | None = None) -> StockAnalysis:
        price = await self._market_data.latest_price(symbol)
        indicators = await self._market_data.indicators(symbol)
        headlines = await self._merge_headlines(symbol, name)

        sentiment = await self._sentiment.analyze(headlines)                    # LLM(EXAONE)
        outlook = self._predictor.predict(indicators, sentiment, self._config)  # 순수

        logger.info(
            "[stock] %s price=%.2f rsi=%.1f sentiment=%.2f → %s(%.2f)",
            symbol.code, price.value, indicators.rsi, sentiment.value,
            outlook.direction.value, outlook.confidence,
        )
        return StockAnalysis(
            symbol=symbol.code,
            price=price.value,
            direction=outlook.direction.value,
            confidence=outlook.confidence,
            sentiment=sentiment.value,
            sentiment_label=sentiment.label,
            rsi=indicators.rsi,
            ma20=indicators.ma20,
            ma50=indicators.ma50,
            support=indicators.support,
            resistance=indicators.resistance,
            headlines=headlines,
        )

    async def _merge_headlines(self, symbol: Symbol, name: str | None) -> list[str]:
        """수집 뉴스(DB, n8n 적재) 우선 + 시세 벤더 뉴스 보조(중복 제거, 최대 8건)."""
        collected: list[str] = []
        if self._news:
            collected = await self._news.recent_titles(name or symbol.code)
        vendor = await self._market_data.recent_headlines(symbol)
        return (collected + [h for h in vendor if h not in collected])[:8]
