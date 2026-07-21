from datetime import UTC, datetime, timedelta

import pytest

from stock.app.dtos.stock_forecast_dto import ForecastQuery
from stock.app.exceptions import MarketDataUnavailableError
from stock.app.use_cases import stock_forecast_interactor
from stock.app.use_cases.stock_forecast_interactor import StockForecastInteractor
from stock.domain.entities.outlook import Direction, Outlook
from stock.domain.entities.price_bar import PriceBar
from stock.domain.value_objects.forecast_distribution import (
    DirectionStats,
    ForecastDistribution,
)


def _bars(n: int, ticker: str = "TEST.KS") -> list[PriceBar]:
    """일 1% 단조 상승 합성봉 — 지표가 결정론적으로 나온다(전 평가일 NEUTRAL·전일 상승)."""
    start = datetime(2024, 1, 1, tzinfo=UTC)
    out = []
    price = 100.0
    for i in range(n):
        price *= 1.01
        out.append(PriceBar(
            ticker=ticker, timeframe="1d", ts=start + timedelta(days=i),
            open=price * 0.995, high=price * 1.005, low=price * 0.99,
            close=price, volume=1000,
        ))
    return out


class _StubPort:
    def __init__(self, bars):
        self.bars = bars
        self.full_loads = 0

    async def find_latest_daily_bar(self, symbol):
        return self.bars[-1] if self.bars else None

    async def find_all_daily_bars(self, symbol):
        self.full_loads += 1
        return self.bars


@pytest.fixture(autouse=True)
def _clear_cache():
    stock_forecast_interactor._CACHE.clear()
    stock_forecast_interactor._LIVE_CACHE.clear()
    yield
    stock_forecast_interactor._CACHE.clear()
    stock_forecast_interactor._LIVE_CACHE.clear()


async def test_미보유_심볼이면_예외():
    with pytest.raises(MarketDataUnavailableError):
        await StockForecastInteractor(history=_StubPort([])).forecast(
            ForecastQuery(symbol="NOPE")
        )


async def test_봉이_부족하면_예외():
    with pytest.raises(MarketDataUnavailableError):
        await StockForecastInteractor(history=_StubPort(_bars(30))).forecast(
            ForecastQuery(symbol="TEST")
        )


async def test_상승_합성봉의_확률은_결정적이다():
    view = await StockForecastInteractor(history=_StubPort(_bars(120))).forecast(
        ForecastQuery(symbol="test")  # 소문자 입력도 정규화
    )
    assert view.symbol == "TEST"
    assert view.resolved_ticker == "TEST.KS"
    assert view.horizon_days == 5
    # 단조 상승이라 전 평가일이 상승 마감 — 조건부 상승 비율 100%, 기준선도 100%
    p = view.probability
    assert p is not None
    assert p.hits == p.sample_size
    assert p.up_rate == 1.0
    assert p.baseline_up_rate == 1.0
    assert p.ci_low < 1.0 <= p.ci_high  # Wilson 구간은 1.0을 물고 하한은 그보다 작다
    assert any(i.key == "probability" for i in view.insights)
    assert any(i.key == "basis" for i in view.insights)


async def test_표본_30_이상이면_분위수_밴드():
    view = await StockForecastInteractor(history=_StubPort(_bars(120))).forecast(
        ForecastQuery(symbol="TEST")
    )
    assert view.band.source == "quantile"
    # 일 1% × 5거래일 ≈ +5.1% — 분위수 전부 그 근방
    assert 0.045 < view.band.median_pct < 0.055
    assert view.band.q25_pct <= view.band.median_pct <= view.band.q75_pct


async def test_표본_부족이면_ATR_콘_폴백():
    view = await StockForecastInteractor(history=_StubPort(_bars(70))).forecast(
        ForecastQuery(symbol="TEST")
    )
    assert view.band.source == "atr"
    assert view.band.median_pct == 0.0
    assert view.band.q75_pct == -view.band.q25_pct > 0
    assert any(i.key == "band" and "변동성" in i.text for i in view.insights)


async def test_같은_날은_캐시로_재계산하지_않는다():
    port = _StubPort(_bars(120))
    interactor = StockForecastInteractor(history=port)
    first = await interactor.forecast(ForecastQuery(symbol="TEST"))
    second = await interactor.forecast(ForecastQuery(symbol="TEST"))
    assert first is second
    assert port.full_loads == 1  # 캐시 히트면 일봉 풀로드도 생략(마지막 봉 1행만 조회)


async def test_DOWN_신호는_상승률이_기준선보다_낮아야_유의하다(monkeypatch):
    interactor = StockForecastInteractor(history=_StubPort(_bars(120)))
    monkeypatch.setattr(
        interactor._predictor, "predict",
        lambda *a, **k: Outlook(direction=Direction.DOWN, confidence=0.5),
    )
    dist = ForecastDistribution(
        horizon_days=5, evaluated=400, baseline_up_rate=0.55,
        by_direction={
            "UP": DirectionStats(0, 0, None, None, None),
            # 상승 35%(70/200) — 기준선 55%보다 뚜렷이 낮은 강한 하락 신호
            "DOWN": DirectionStats(200, 70, -0.02, -0.01, 0.0),
            "NEUTRAL": DirectionStats(200, 110, 0.0, 0.0, 0.0),
        },
    )
    monkeypatch.setattr(interactor._backtester, "distribution", lambda *a, **k: dist)

    view = await interactor.forecast(ForecastQuery(symbol="TEST"))
    assert view.signal_direction == "DOWN"
    assert view.probability.ready is True  # 하락 방향은 '상승률이 낮을수록' 유의
    assert not any(i.key == "sample" for i in view.insights)  # 참고용 경고 없음


async def test_ready_기준은_표본과_신뢰구간_하한():
    view = await StockForecastInteractor(history=_StubPort(_bars(120))).forecast(
        ForecastQuery(symbol="TEST")
    )
    # 표본 64회(<100) → ready False + 참고용 경고 문장
    assert view.probability.ready is False
    assert any(i.key == "sample" and i.tone == "warning" for i in view.insights)


class _StubMarketData:
    def __init__(self, bars):
        self.bars = bars
        self.calls = 0

    async def daily_bars(self, symbol):
        self.calls += 1
        return self.bars


async def test_미수집_종목은_라이브_이력으로_계산한다():
    view = await StockForecastInteractor(
        history=_StubPort([]), market_data=_StubMarketData(_bars(120, ticker="RKLB")),
    ).forecast(ForecastQuery(symbol="RKLB"))
    assert view.live is True
    assert view.resolved_ticker == "RKLB"
    assert view.band is not None


async def test_수집_봉이_있으면_라이브를_쓰지_않는다():
    view = await StockForecastInteractor(
        history=_StubPort(_bars(120)), market_data=_StubMarketData([]),
    ).forecast(ForecastQuery(symbol="TEST"))
    assert view.live is False


async def test_라이브는_같은_날_재요청에_벤더를_다시_부르지_않는다():
    market = _StubMarketData(_bars(120, ticker="RKLB"))
    interactor = StockForecastInteractor(history=_StubPort([]), market_data=market)
    first = await interactor.forecast(ForecastQuery(symbol="RKLB"))
    second = await interactor.forecast(ForecastQuery(symbol="RKLB"))
    assert first is second
    assert market.calls == 1  # 일 단위 라이브 캐시 — 2y 다운로드는 하루 1회
