from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.price_bar_ingest_use_case import PriceBarIngestUseCase
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort
from hub.app.use_cases.price_bar_ingest_interactor import PriceBarIngestInteractor


def get_price_bar_storage_port() -> PriceBarStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_price_bar_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_price_bar_ingest_use_case(
    storage: PriceBarStoragePort = Depends(get_price_bar_storage_port),
) -> PriceBarIngestUseCase:
    return PriceBarIngestInteractor(storage=storage)
