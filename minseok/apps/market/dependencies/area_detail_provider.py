from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_market_db
from market.adapter.outbound.pg.area_detail_pg_repository import AreaDetailPgRepository
from market.app.ports.input.area_detail_use_case import AreaDetailUseCase
from market.app.use_cases.area_detail_interactor import AreaDetailInteractor


def get_area_detail_use_case(db: AsyncSession = Depends(get_market_db)) -> AreaDetailUseCase:
    return AreaDetailInteractor(detail=AreaDetailPgRepository(session=db))
