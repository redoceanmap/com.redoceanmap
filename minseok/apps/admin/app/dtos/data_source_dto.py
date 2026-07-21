from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.commercial_data_dto import DatasetStat


@dataclass(frozen=True)
class DataSourceListResponse:
    datasets: list[DatasetStat]
