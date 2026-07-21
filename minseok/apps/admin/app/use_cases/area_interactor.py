from __future__ import annotations

from admin.app.dtos.area_dto import AreaListResponse
from admin.app.ports.input.area_use_case import AreaUseCase
from hub.app.ports.output.commercial_data_port import CommercialDataPort


class AreaInteractor(AreaUseCase):
    """어드민 상권 목록 대장 — 허브 CommercialDataPort에 위임한다."""

    def __init__(self, commercial: CommercialDataPort) -> None:
        self._commercial = commercial

    async def list_areas(self) -> AreaListResponse:
        return AreaListResponse(areas=await self._commercial.get_area_overview())
