from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.forecast_snapshot_use_case import ForecastSnapshotIngestUseCase
from hub.app.ports.output.forecast_snapshot_port import ForecastSnapshotPort
from hub.app.use_cases.forecast_snapshot_interactor import ForecastSnapshotInteractor


def get_forecast_snapshot_port() -> ForecastSnapshotPort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_forecast_snapshot_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_forecast_snapshot_use_case(
    snapshots: ForecastSnapshotPort = Depends(get_forecast_snapshot_port),
) -> ForecastSnapshotIngestUseCase:
    return ForecastSnapshotInteractor(snapshots=snapshots)
