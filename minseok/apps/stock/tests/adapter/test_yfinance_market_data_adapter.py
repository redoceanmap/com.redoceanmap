import pytest

from stock.adapter.outbound.yfinance_market_data_adapter import (
    YFinanceMarketDataAdapter,
    yahoo_candidates,
)
from stock.domain.value_objects.market_values import Symbol


def test_한국_6자리_코드는_코스피_코스닥_순으로_시도():
    assert yahoo_candidates("005930") == ["005930.KS", "005930.KQ"]


def test_미국_티커는_대문자_그대로():
    assert yahoo_candidates("aapl") == ["AAPL"]


@pytest.mark.network
async def test_삼성전자_라이브_조회():
    adapter = YFinanceMarketDataAdapter()
    symbol = Symbol(code="005930")
    price = await adapter.latest_price(symbol)
    indicators = await adapter.indicators(symbol)
    assert price.value > 0
    assert 0.0 <= indicators.rsi <= 100.0
    assert indicators.support < indicators.resistance


@pytest.mark.network
async def test_AAPL_라이브_조회_및_뉴스():
    adapter = YFinanceMarketDataAdapter()
    symbol = Symbol(code="AAPL")
    indicators = await adapter.indicators(symbol)
    headlines = await adapter.recent_headlines(symbol)
    assert indicators.ma20 > 0
    assert isinstance(headlines, list)
