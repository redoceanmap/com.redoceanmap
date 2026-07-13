from __future__ import annotations

from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.entities.outlook import Direction
from stock.domain.services.indicator_calculator import MA_LONG, IndicatorCalculator
from stock.domain.services.outlook_predictor import OutlookPredictor
from stock.domain.value_objects.backtest_report import BacktestReport
from stock.domain.value_objects.sentiment_score import SentimentScore

DEFAULT_HORIZON_DAYS = 5


class Backtester:
    """과거 일봉으로 방향 전망의 적중률을 채점하는 순수 도메인 서비스.

    워크포워드: 각 평가일 t에서 t까지의 데이터로만 지표를 계산해 전망을 내고,
    t+horizon 종가와 비교한다(미래 참조 없음). 과거 뉴스는 수집할 수 없으므로
    감성은 중립(0.0) 고정 — 지표 신호만 평가한다.
    """

    def __init__(
        self,
        calculator: IndicatorCalculator | None = None,
        predictor: OutlookPredictor | None = None,
    ) -> None:
        self._calculator = calculator or IndicatorCalculator()
        self._predictor = predictor or OutlookPredictor()

    def run(
        self,
        closes: list[float],
        lows: list[float],
        highs: list[float],
        volumes: list[float] | None = None,
        *,
        horizon: int = DEFAULT_HORIZON_DAYS,
        config: AnalysisConfig | None = None,
    ) -> BacktestReport:
        return self.sweep(
            closes, lows, highs, volumes,
            horizon=horizon, configs=[config or AnalysisConfig.default()],
        )[0]

    def sweep(
        self,
        closes: list[float],
        lows: list[float],
        highs: list[float],
        volumes: list[float] | None = None,
        *,
        horizon: int = DEFAULT_HORIZON_DAYS,
        configs: list[AnalysisConfig],
    ) -> list[BacktestReport]:
        """여러 config를 한 번에 채점 — 지표는 평가일당 1회만 계산(스윕 비용 절감)."""
        neutral = SentimentScore(value=0.0)
        start = MA_LONG + 1  # 지표 계산 최소 데이터
        end = len(closes) - horizon
        if end <= start:
            raise ValueError(
                f"백테스트에는 최소 {start + horizon + 1}개 봉이 필요합니다 (현재 {len(closes)}개)."
            )

        evaluated = end - start
        indicator_rose_pairs = []
        baseline_up = 0
        for t in range(start, end):
            indicators = self._calculator.compute(
                closes[: t + 1],
                lows[: t + 1],
                highs[: t + 1],
                volumes[: t + 1] if volumes is not None else None,
            )
            rose = closes[t + horizon] > closes[t]
            baseline_up += 1 if rose else 0
            indicator_rose_pairs.append((indicators, rose))

        reports = []
        for config in configs:
            up = down = neutral_count = up_hits = down_hits = 0
            for indicators, rose in indicator_rose_pairs:
                outlook = self._predictor.predict(indicators, neutral, config)
                if outlook.direction is Direction.UP:
                    up += 1
                    up_hits += 1 if rose else 0
                elif outlook.direction is Direction.DOWN:
                    down += 1
                    down_hits += 0 if rose else 1
                else:
                    neutral_count += 1
            reports.append(BacktestReport(
                horizon_days=horizon,
                evaluated=evaluated,
                up_signals=up,
                down_signals=down,
                neutral_signals=neutral_count,
                up_hits=up_hits,
                down_hits=down_hits,
                baseline_up_rate=baseline_up / evaluated,
            ))
        return reports
