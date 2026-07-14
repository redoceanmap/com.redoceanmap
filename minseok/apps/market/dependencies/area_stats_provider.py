from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from market.adapter.outbound.pg.area_stats_pg_repository import AreaStatsPgRepository
from market.app.ports.input.area_stats_use_case import AreaStatsUseCase
from market.app.use_cases.area_stats_interactor import AreaStatsInteractor


def get_area_stats_use_case(db: AsyncSession = Depends(get_db)) -> AreaStatsUseCase:
    return AreaStatsInteractor(stats=AreaStatsPgRepository(session=db))
