from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.commercial_data_dto import AreaOverviewRow


@dataclass(frozen=True)
class AreaListResponse:
    areas: list[AreaOverviewRow]
