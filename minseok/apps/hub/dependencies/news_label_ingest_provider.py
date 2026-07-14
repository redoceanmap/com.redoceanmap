from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.news_label_ingest_use_case import NewsLabelIngestUseCase
from hub.app.ports.output.news_label_storage_port import NewsLabelStoragePort
from hub.app.use_cases.news_label_ingest_interactor import NewsLabelIngestInteractor


def get_news_label_storage_port() -> NewsLabelStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_news_label_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_news_label_ingest_use_case(
    storage: NewsLabelStoragePort = Depends(get_news_label_storage_port),
) -> NewsLabelIngestUseCase:
    return NewsLabelIngestInteractor(storage=storage)
