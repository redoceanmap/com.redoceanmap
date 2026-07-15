from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.market_news_ingest_use_case import MarketNewsIngestUseCase
from hub.app.ports.output.market_news_storage_port import MarketNewsStoragePort
from hub.app.use_cases.market_news_ingest_interactor import MarketNewsIngestInteractor


def get_market_news_storage_port() -> MarketNewsStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(market) 구현을 주입한다."""
    raise NotImplementedError(
        "get_market_news_storage_port는 main.py의 dependency_overrides로 market 구현을 주입해야 합니다."
    )


def get_market_news_ingest_use_case(
    storage: MarketNewsStoragePort = Depends(get_market_news_storage_port),
) -> MarketNewsIngestUseCase:
    return MarketNewsIngestInteractor(storage=storage)
