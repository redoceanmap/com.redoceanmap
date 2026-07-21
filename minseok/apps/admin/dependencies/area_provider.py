from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.area_use_case import AreaUseCase
from admin.app.use_cases.area_interactor import AreaInteractor
from hub.app.ports.output.commercial_data_port import CommercialDataPort
from hub.dependencies.commercial_data_provider import get_commercial_data_port


def get_area_use_case(
    commercial: CommercialDataPort = Depends(get_commercial_data_port),
) -> AreaUseCase:
    return AreaInteractor(commercial=commercial)
