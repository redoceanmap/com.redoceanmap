from __future__ import annotations

from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.entities.outlook import Direction, Outlook
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.sentiment_score import SentimentScore


class OutlookPredictor:
    """지표 + 뉴스 감성 → 방향 전망. 외부 의존 없는 순수 도메인 서비스.

    결정론적 스코어링만 한다(매매 추천 아님). 종합 점수는 감성·RSI·이동평균 배열을
    가중 합산해 -1.0 ~ 1.0 로 정규화한 뒤 임계값으로 방향을 판정한다.
    """

    def predict(
        self,
        indicators: Indicators,
        sentiment: SentimentScore,
        config: AnalysisConfig,
    ) -> Outlook:
        score = (
            0.5 * sentiment.value
            + 0.3 * self._rsi_signal(indicators.rsi)
            + 0.2 * self._trend_signal(indicators)
        )
        score = max(-1.0, min(1.0, score))
        confidence = min(abs(score), 1.0)
        if score >= config.up_threshold:
            return Outlook(direction=Direction.UP, confidence=confidence)
        if score <= config.down_threshold:
            return Outlook(direction=Direction.DOWN, confidence=confidence)
        return Outlook(direction=Direction.NEUTRAL, confidence=confidence)

    @staticmethod
    def _rsi_signal(rsi: float) -> float:
        # 과매도(30↓)면 반등 기대 +, 과매수(70↑)면 조정 기대 -.
        if rsi <= 30.0:
            return (30.0 - rsi) / 30.0
        if rsi >= 70.0:
            return -(rsi - 70.0) / 30.0
        return 0.0

    @staticmethod
    def _trend_signal(ind: Indicators) -> float:
        # 정배열(ma20 > ma50) 상승 추세 +, 역배열 -.
        if ind.ma50 <= 0:
            return 0.0
        return max(-1.0, min(1.0, (ind.ma20 - ind.ma50) / ind.ma50 * 10.0))
