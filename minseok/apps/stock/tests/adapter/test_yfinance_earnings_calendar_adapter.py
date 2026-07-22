from datetime import date, datetime

import pandas as pd
import pytest

from stock.adapter.outbound import yfinance_earnings_calendar_adapter as mod
from stock.adapter.outbound.yfinance_earnings_calendar_adapter import (
    YFinanceEarningsCalendarAdapter,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    mod._CACHE.clear()
    yield
    mod._CACHE.clear()


class _FakeTicker:
    def __init__(self, df):
        self._df = df

    def get_earnings_dates(self, limit):
        if isinstance(self._df, Exception):
            raise self._df
        return self._df


def _df(dates: list[datetime]) -> pd.DataFrame:
    return pd.DataFrame({"EPS Estimate": [1.0] * len(dates)}, index=pd.DatetimeIndex(dates))


async def test_parses_and_dedupes_dates(monkeypatch):
    df = _df([datetime(2026, 7, 30, 21), datetime(2026, 7, 30, 21), datetime(2026, 4, 29, 21)])
    monkeypatch.setattr(mod.yf, "Ticker", lambda t: _FakeTicker(df))
    dates = await YFinanceEarningsCalendarAdapter().earnings_dates("aapl")
    assert dates == [date(2026, 4, 29), date(2026, 7, 30)]


async def test_daily_cache_prevents_second_fetch(monkeypatch):
    calls = []

    def _ticker(t):
        calls.append(t)
        return _FakeTicker(_df([datetime(2026, 7, 30)]))

    monkeypatch.setattr(mod.yf, "Ticker", _ticker)
    adapter = YFinanceEarningsCalendarAdapter()
    await adapter.earnings_dates("AAPL")
    await adapter.earnings_dates("AAPL")
    assert len(calls) == 1


async def test_vendor_failure_degrades_to_empty_and_caches(monkeypatch):
    calls = []

    def _ticker(t):
        calls.append(t)
        return _FakeTicker(RuntimeError("429"))

    monkeypatch.setattr(mod.yf, "Ticker", _ticker)
    adapter = YFinanceEarningsCalendarAdapter()
    assert await adapter.earnings_dates("AAPL") == []
    assert await adapter.earnings_dates("AAPL") == []  # 그날 재타격 없음
    assert len(calls) == 1


@pytest.mark.network
async def test_live_fetch_returns_dates():
    dates = await YFinanceEarningsCalendarAdapter().earnings_dates("AAPL")
    assert isinstance(dates, list)
