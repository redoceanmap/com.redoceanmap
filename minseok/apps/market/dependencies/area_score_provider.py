from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_market_db
from market.adapter.outbound.pg.area_score_pg_repository import AreaScorePgRepository
from market.app.ports.input.area_score_use_case import AreaScoreUseCase
from market.app.use_cases.area_score_interactor import AreaScoreInteractor


def get_area_score_use_case(db: AsyncSession = Depends(get_market_db)) -> AreaScoreUseCase:
    return AreaScoreInteractor(repo=AreaScorePgRepository(session=db))
