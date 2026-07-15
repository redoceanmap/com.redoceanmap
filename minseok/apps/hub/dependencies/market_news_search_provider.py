from __future__ import annotations

from hub.app.ports.output.market_news_search_port import MarketNewsSearchPort


def get_market_news_search_port() -> MarketNewsSearchPort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(market) 구현을 주입한다."""
    raise NotImplementedError(
        "get_market_news_search_port는 main.py의 dependency_overrides로 market 구현을 주입해야 합니다."
    )
