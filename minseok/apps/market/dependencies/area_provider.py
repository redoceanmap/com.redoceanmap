from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from market.adapter.outbound.pg.area_pg_repository import AreaPgRepository
from market.app.ports.input.area_use_case import AreaUseCase
from market.app.use_cases.area_interactor import AreaInteractor


def get_area_use_case(db: AsyncSession = Depends(get_db)) -> AreaUseCase:
    return AreaInteractor(repository=AreaPgRepository(session=db))
