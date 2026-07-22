from datetime import UTC, date, datetime, timedelta

from stock.domain.entities.price_bar import PriceBar
from stock.domain.services.regime_calendar import (
    REGIME_BEAR,
    REGIME_BULL,
    REGIME_HIGH_VOL,
    SPY_MA_PERIOD,
    VIX_HIGH,
    RegimeCalendar,
)


def _bars(closes: list[float], ticker: str = "SPY", start: date = date(2020, 1, 1)) -> list[PriceBar]:
    return [
        PriceBar(
            ticker=ticker, timeframe="1d",
            ts=datetime(start.year, start.month, start.day, tzinfo=UTC) + timedelta(days=i),
            open=c, high=c + 1, low=c - 1, close=c, volume=0,
        )
        for i, c in enumerate(closes)
    ]


def _calm_vix(n: int) -> list[PriceBar]:
    return _bars([15.0] * n, ticker="^VIX")


def test_bull_when_above_ma200():
    spy = _bars([100.0] * SPY_MA_PERIOD + [150.0] * 5)  # 마지막 구간 종가가 MA 위
    cal = RegimeCalendar.from_bars(spy, _calm_vix(len(spy)))
    assert cal.regime_at(spy[-1].ts.date()) == REGIME_BULL


def test_bear_when_below_ma200():
    spy = _bars([100.0] * SPY_MA_PERIOD + [50.0] * 5)
    cal = RegimeCalendar.from_bars(spy, _calm_vix(len(spy)))
    assert cal.regime_at(spy[-1].ts.date()) == REGIME_BEAR


def test_high_vol_overrides_bull():
    n = SPY_MA_PERIOD + 5
    spy = _bars([100.0] * SPY_MA_PERIOD + [150.0] * 5)
    vix = _bars([VIX_HIGH + 5.0] * n, ticker="^VIX")
    cal = RegimeCalendar.from_bars(spy, vix)
    assert cal.regime_at(spy[-1].ts.date()) == REGIME_HIGH_VOL


def test_forward_fill_on_non_trading_day():
    spy = _bars([100.0] * SPY_MA_PERIOD + [150.0])
    cal = RegimeCalendar.from_bars(spy, _calm_vix(len(spy)))
    # 마지막 거래일 뒤 3일(주말 등) — 직전 값으로 채운다
    assert cal.regime_at(spy[-1].ts.date() + timedelta(days=3)) == REGIME_BULL


def test_none_before_ma_formed_or_without_data():
    spy = _bars([100.0] * SPY_MA_PERIOD)
    cal = RegimeCalendar.from_bars(spy, _calm_vix(len(spy)))
    # MA200 형성 첫날 이전 날짜 — 판정 불가
    assert cal.regime_at(spy[0].ts.date()) is None
    empty = RegimeCalendar.from_bars([], [])
    assert empty.regime_at(date(2026, 1, 1)) is None


def test_vix_missing_falls_back_to_spy_only():
    spy = _bars([100.0] * SPY_MA_PERIOD + [150.0])
    cal = RegimeCalendar.from_bars(spy, [])
    assert cal.regime_at(spy[-1].ts.date()) == REGIME_BULL
