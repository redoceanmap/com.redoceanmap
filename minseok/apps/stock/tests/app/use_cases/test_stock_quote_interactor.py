import pytest

from stock.adapter.outbound.fake_market_data_adapter import FakeMarketDataAdapter
from stock.app.dtos.stock_quote_dto import QuoteQuery
from stock.app.use_cases import stock_quote_interactor
from stock.app.use_cases.stock_quote_interactor import StockQuoteInteractor
from stock.domain.value_objects.market_values import Price, Quote


class _CountingMarketData(FakeMarketDataAdapter):
    def __init__(self):
        self.calls = 0

    async def quote(self, symbol):
        self.calls += 1
        return Quote(price=Price(value=226.5), previous_close=Price(value=224.0))


@pytest.fixture(autouse=True)
def _clear_cache():
    stock_quote_interactor._CACHE.clear()
    yield
    stock_quote_interactor._CACHE.clear()


async def test_지연_시세_현재가를_반환한다():
    view = await StockQuoteInteractor(market_data=FakeMarketDataAdapter()).quote(
        QuoteQuery(symbol=" aapl ")
    )
    assert view.symbol == "AAPL"  # 정규화
    assert view.price == 226.5
    assert view.delayed is True
    assert view.previous_close == 224.0
    assert view.change_pct == pytest.approx(226.5 / 224.0 - 1)


async def test_전일_종가가_없으면_등락률은_None이다():
    class _NoPrevious(FakeMarketDataAdapter):
        async def quote(self, symbol):
            return Quote(price=Price(value=226.5))

    view = await StockQuoteInteractor(market_data=_NoPrevious()).quote(QuoteQuery(symbol="AAPL"))
    assert view.previous_close is None
    assert view.change_pct is None


async def test_TTL_안에서는_벤더를_다시_부르지_않는다():
    market = _CountingMarketData()
    interactor = StockQuoteInteractor(market_data=market)
    first = await interactor.quote(QuoteQuery(symbol="AAPL"))
    second = await interactor.quote(QuoteQuery(symbol="AAPL"))
    assert first is second  # 공유 캐시 히트
    assert market.calls == 1


async def test_심볼이_다르면_각자_조회한다():
    market = _CountingMarketData()
    interactor = StockQuoteInteractor(market_data=market)
    await interactor.quote(QuoteQuery(symbol="AAPL"))
    await interactor.quote(QuoteQuery(symbol="MSFT"))
    assert market.calls == 2
