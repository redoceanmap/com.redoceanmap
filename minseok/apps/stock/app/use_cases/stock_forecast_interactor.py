from __future__ import annotations

import asyncio
import logging
from dataclasses import replace
from datetime import UTC, datetime

from stock.app.dtos.stock_forecast_dto import (
    BandInfo,
    ForecastQuery,
    ProbabilityInfo,
    StockForecastView,
)
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.ports.input.stock_forecast_use_case import StockForecastUseCase
from stock.app.ports.output.forecast_history_port import ForecastHistoryPort
from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.services import forecast_narrator
from stock.domain.services.backtester import Backtester
from stock.domain.services.forecast_narrator import QUANTILE_MIN_SAMPLES
from stock.domain.services.indicator_calculator import IndicatorCalculator
from stock.domain.services.outlook_predictor import OutlookPredictor
from stock.app.ports.output.market_data_port import MarketDataPort
from stock.domain.value_objects.backtest_report import MIN_SIGNAL_SAMPLES, wilson_bounds
from stock.domain.value_objects.market_values import Symbol
from stock.domain.value_objects.sentiment_score import SentimentScore

logger = logging.getLogger(__name__)

# 워크포워드가 평가일당 지표를 재계산해 종목당 수 초 걸린다 —
# (티커, horizon)별 최신 봉 기준 1건만 캐시한다(봉은 일 1회 적재라 ts가 바뀌면 자연 무효).
_CACHE: dict[tuple[str, int], tuple[str, StockForecastView]] = {}
# 라이브 모드 전용 — 벤더 2y 다운로드 자체를 막아야 하므로 봉 ts가 아니라 UTC 날짜로
# 신선도를 판단한다(같은 날 재요청이면 다운로드 없이 반환).
_LIVE_CACHE: dict[tuple[str, int], tuple[str, StockForecastView]] = {}


class StockForecastInteractor(StockForecastUseCase):
    """확률·예측 밴드 대장 — 저장 일봉을 백테스트 분포로 바꿔 현재 신호에 조건부 매칭한다."""

    def __init__(
        self,
        history: ForecastHistoryPort,
        market_data: MarketDataPort | None = None,
    ) -> None:
        self._history = history
        self._market_data = market_data
        self._calculator = IndicatorCalculator()
        self._predictor = OutlookPredictor()
        self._backtester = Backtester(self._calculator, self._predictor)

    async def forecast(self, query: ForecastQuery) -> StockForecastView:
        symbol = query.symbol.strip().upper()
        live = False
        # 캐시 검사는 마지막 봉 1행만 읽어서 — 히트면 수년치 일봉 풀로드를 건너뛴다
        latest = await self._history.find_latest_daily_bar(symbol)
        if latest is None and self._market_data is not None:
            # 미수집 종목 — 다운로드 전에 일 단위 라이브 캐시부터(2y 벤더 호출 자체를 막는다)
            today = datetime.now(UTC).date().isoformat()
            live_cached = _LIVE_CACHE.get((symbol, query.horizon))
            if live_cached is not None and live_cached[0] == today:
                return live_cached[1]
            # 시세 벤더 라이브 이력으로 동일 계산(2y ≈ 500봉, 저장 안 함)
            live_bars = await self._market_data.daily_bars(Symbol(code=symbol))
            latest = live_bars[-1] if live_bars else None
            live = True
        if latest is None:
            raise MarketDataUnavailableError(
                f"수집된 일봉이 없습니다(수집 대상 아님): {query.symbol}"
            )

        cache_key = (latest.ticker, query.horizon)
        last_ts = latest.ts.isoformat()
        cached = _CACHE.get(cache_key)
        if cached is not None and cached[0] == last_ts:
            view = cached[1]
            # 캐시 키는 확정 티커 — 같은 종목을 다른 표기(005930 ↔ 005930.KS)로 물어도
            # 응답 symbol은 이번 요청 표기를 따른다
            return view if view.symbol == symbol else replace(view, symbol=symbol)

        bars = live_bars if live else await self._history.find_all_daily_bars(symbol)
        if not bars:
            raise MarketDataUnavailableError(
                f"수집된 일봉이 없습니다(수집 대상 아님): {query.symbol}"
            )

        closes = [b.close for b in bars]
        lows = [b.low for b in bars]
        highs = [b.high for b in bars]
        volumes = [float(b.volume) for b in bars]
        config = AnalysisConfig.default()

        # 워크포워드는 평가일당 지표 재계산(O(n²)) — 이벤트 루프를 막지 않게 스레드로 분리
        def _compute():
            ind = self._calculator.compute(closes, lows, highs, volumes)
            return ind, self._backtester.distribution(
                closes, lows, highs, volumes, horizon=query.horizon, config=config
            )

        try:
            indicators, dist = await asyncio.to_thread(_compute)
        except ValueError as e:  # 봉 부족 — 지표·백테스트 최소 구간 미달
            raise MarketDataUnavailableError(str(e))
        current = self._predictor.predict(indicators, SentimentScore(value=0.0), config)

        direction = current.direction.value
        stats = dist.by_direction[direction]

        probability = None
        ready = False
        if stats.sample_size > 0:
            ci_low, ci_high = wilson_bounds(stats.hits, stats.sample_size)
            # 방향별 유의성: UP은 상승 비율이 기준선보다 뚜렷이 높아야, DOWN은 뚜렷이 낮아야
            # (backtest_report의 up/down_probability_ready와 같은 취지). NEUTRAL은 방향 주장이 아니다.
            if direction == "UP":
                significant = ci_low > dist.baseline_up_rate
            elif direction == "DOWN":
                significant = ci_high < dist.baseline_up_rate
            else:
                significant = False
            ready = stats.sample_size >= MIN_SIGNAL_SAMPLES and significant
            probability = ProbabilityInfo(
                up_rate=stats.hits / stats.sample_size,
                sample_size=stats.sample_size,
                hits=stats.hits,
                ci_low=ci_low,
                ci_high=ci_high,
                baseline_up_rate=dist.baseline_up_rate,
                ready=ready,
            )

        if stats.sample_size >= QUANTILE_MIN_SAMPLES and stats.median is not None:
            band = BandInfo(
                source="quantile", q25_pct=stats.q25, median_pct=stats.median, q75_pct=stats.q75
            )
        else:
            # 폴백: 변동성(ATR) 기반 대칭 예상 범위 — ±ATR%·√horizon
            move = indicators.atr_pct * (query.horizon ** 0.5)
            band = BandInfo(source="atr", q25_pct=-move, median_pct=0.0, q75_pct=move)

        view = StockForecastView(
            symbol=symbol,
            resolved_ticker=bars[0].ticker,
            as_of=bars[-1].ts,
            base_price=closes[-1],
            horizon_days=query.horizon,
            signal_direction=direction,
            probability=probability,
            band=band,
            insights=forecast_narrator.narrate(
                direction, stats, dist.baseline_up_rate, query.horizon, ready
            ),
            live=live,
        )
        if live:
            _LIVE_CACHE[(symbol, query.horizon)] = (
                datetime.now(UTC).date().isoformat(), view,
            )
        _CACHE[cache_key] = (last_ts, view)
        logger.info(
            "[stock-forecast] %s(%s) %s n=%d evaluated=%d",
            symbol, bars[0].ticker, direction, stats.sample_size, dist.evaluated,
        )
        return view
