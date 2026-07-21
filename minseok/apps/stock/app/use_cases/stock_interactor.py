from __future__ import annotations

import logging

from stock.app.dtos.stock_analysis_dto import StockAnalysis
from stock.app.ports.input.stock_use_case import StockUseCase
from stock.app.ports.output.demand_record_port import DemandRecordPort
from stock.app.ports.output.market_data_port import MarketDataPort
from stock.app.ports.output.news_repository import NewsRepositoryPort
from stock.app.ports.output.sentiment_port import SentimentPort
from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.entities.outlook import Direction
from stock.domain.services.outlook_predictor import OutlookPredictor
from stock.domain.services.stock_narrator import narrate
from stock.domain.value_objects.market_values import Symbol
from stock.domain.value_objects.sentiment_score import SentimentScore

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
        demand: DemandRecordPort | None = None,
    ) -> None:
        self._market_data = market_data
        self._sentiment = sentiment
        self._predictor = predictor
        self._config = config
        self._news = news
        self._demand = demand

    async def analyze(self, symbol: Symbol, name: str | None = None) -> StockAnalysis:
        price = await self._market_data.latest_price(symbol)
        # 시세 확인을 통과한(실존) 심볼만 수요 기록 — 워치리스트 수요 편입의 재료.
        # 기록 실패는 분석에 영향 없음(베스트 에포트).
        if self._demand is not None:
            try:
                await self._demand.record(symbol.code)
            except Exception:
                logger.warning("[stock] 수요 기록 실패: %s", symbol.code, exc_info=True)
        indicators = await self._market_data.indicators(symbol)
        headlines = await self._merge_headlines(symbol, name)

        sentiment = await self._sentiment.analyze(headlines)                    # LLM(EXAONE)
        outlook = self._predictor.predict(indicators, sentiment, self._config)  # 순수
        contributions = self._predictor.breakdown(indicators, sentiment, self._config)
        score = self._predictor.score(contributions)
        # 참고 신호: 백테스트 검증(인샘플+홀드아웃) 통과 조합 — 채점 조건(감성 중립) 그대로 재현
        reference = self._predictor.predict(
            indicators, SentimentScore(value=0.0), AnalysisConfig.rsi_bb_reference()
        )
        reference_up = reference.direction is Direction.UP
        insights = narrate(outlook, score, contributions, indicators, self._config, reference_up)

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
            atr_pct=indicators.atr_pct,
            bb_percent_b=indicators.bb_percent_b,
            volume_ratio=indicators.volume_ratio,
            obv_slope=indicators.obv_slope,
            momentum_12_1=indicators.momentum_12_1,
            reference_up_signal=reference_up,
            headlines=headlines,
            score=score,
            up_threshold=self._config.up_threshold,
            down_threshold=self._config.down_threshold,
            neutral_reason=outlook.neutral_reason,
            signals=contributions,
            insights=insights,
        )

    async def _merge_headlines(self, symbol: Symbol, name: str | None) -> list[str]:
        """수집 뉴스(DB, n8n 적재) 우선 + 시세 벤더 뉴스 보조(중복 제거, 최대 8건)."""
        collected: list[str] = []
        if self._news:
            collected = await self._news.recent_titles(name or symbol.code, ticker=symbol.code)
        vendor = await self._market_data.recent_headlines(symbol)
        return (collected + [h for h in vendor if h not in collected])[:8]
