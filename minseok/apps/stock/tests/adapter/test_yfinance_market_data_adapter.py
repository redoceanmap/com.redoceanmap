import pandas as pd
import pytest

from stock.adapter.outbound import yfinance_market_data_adapter
from stock.adapter.outbound.yfinance_market_data_adapter import (
    YFinanceMarketDataAdapter,
    yahoo_candidates,
)
from stock.domain.value_objects.market_values import Symbol


async def test_야후_NaN_행은_걸러지고_지표가_계산된다(monkeypatch):
    # 야후가 마지막 행을 미완성(NaN)으로 보내는 실사례 재현 — 필터 없으면 RSI가 NaN이 된다
    n = 60
    frame = pd.DataFrame({
        "Open": [100.0 + i * 0.5 for i in range(n)] + [float("nan")],
        "Close": [100.0 + i * 0.5 for i in range(n)] + [float("nan")],
        "Low": [99.0 + i * 0.5 for i in range(n)] + [float("nan")],
        "High": [101.0 + i * 0.5 for i in range(n)] + [float("nan")],
        "Volume": [1000.0] * n + [1000.0],
    })

    class _FakeTicker:
        def __init__(self, ticker):
            pass

        def history(self, period, auto_adjust):
            return frame

    monkeypatch.setattr(yfinance_market_data_adapter.yf, "Ticker", _FakeTicker)
    adapter = YFinanceMarketDataAdapter()
    indicators = await adapter.indicators(Symbol(code="AAPL"))
    assert 0.0 <= indicators.rsi <= 100.0
    price = await adapter.latest_price(Symbol(code="AAPL"))
    assert price.value == frame["Close"].iloc[-2]  # NaN 마지막 행 제외한 최신 종가


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


# ── 전일 종가 선택 규칙 ──
# fast_info["previous_close"]는 실측에서 실제 직전 일봉과 어긋나 쓰지 않는다.
# 현재가가 마지막 일봉과 같은 세션인지로 기준 봉을 가른다.

def test_현재가가_마지막_일봉과_같으면_그_직전_봉이_전일_종가다():
    # 장 마감 상태 — quote가 마지막 종가를 그대로 준다(SNDK 2026-07-22 실사례)
    previous = YFinanceMarketDataAdapter._pick_previous_close(1599.27, [1390.95, 1589.40, 1599.27])
    assert previous == 1589.40


def test_현재가가_장중_틱이면_마지막_일봉이_전일_종가다():
    previous = YFinanceMarketDataAdapter._pick_previous_close(1610.0, [1390.95, 1589.40, 1599.27])
    assert previous == 1599.27


def test_봉이_하나뿐이고_같은_세션이면_전일_종가는_없다():
    assert YFinanceMarketDataAdapter._pick_previous_close(1599.27, [1599.27]) is None


def test_봉이_없으면_전일_종가는_없다():
    assert YFinanceMarketDataAdapter._pick_previous_close(1599.27, []) is None
