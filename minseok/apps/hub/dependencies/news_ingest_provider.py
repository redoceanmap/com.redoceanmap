from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.news_ingest_use_case import NewsIngestUseCase
from hub.app.ports.output.news_storage_port import NewsStoragePort
from hub.app.use_cases.news_ingest_interactor import NewsIngestInteractor


def get_news_storage_port() -> NewsStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_news_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_news_ingest_use_case(
    storage: NewsStoragePort = Depends(get_news_storage_port),
) -> NewsIngestUseCase:
    return NewsIngestInteractor(storage=storage)
