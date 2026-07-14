from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.fundamental_ingest_use_case import FundamentalIngestUseCase
from hub.app.ports.output.fundamental_storage_port import FundamentalStoragePort
from hub.app.use_cases.fundamental_ingest_interactor import FundamentalIngestInteractor


def get_fundamental_storage_port() -> FundamentalStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_fundamental_storage_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_fundamental_ingest_use_case(
    storage: FundamentalStoragePort = Depends(get_fundamental_storage_port),
) -> FundamentalIngestUseCase:
    return FundamentalIngestInteractor(storage=storage)
