from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from market.adapter.outbound.orm.commercial_change_benchmark_orm import (
    CommercialChangeBenchmarkOrm,
)
from market.adapter.outbound.orm.commercial_change_orm import CommercialChangeOrm
from market.adapter.outbound.orm.estimated_sales_orm import EstimatedSalesOrm
from market.adapter.outbound.orm.floating_population_orm import FloatingPopulationOrm
from market.adapter.outbound.orm.region_orm import RegionOrm
from market.adapter.outbound.orm.store_orm import StoreOrm
from market.adapter.outbound.orm.trade_area_orm import TradeAreaOrm
from market.app.dtos.area_score_dto import (
    AreaScoreHeader,
    PersistenceStat,
    StoreHealthStat,
)
from market.app.ports.output.area_score_repository import AreaScoreRepositoryPort
from market.domain.value_objects.area_score_vo import QuarterValue


def _sido_join(stmt, fact_orm):
    """팩트 → trade_area → 행정동 → 자치구 조인 (시도 필터는 gu.parent_code)."""
    dong = aliased(RegionOrm)
    gu = aliased(RegionOrm)
    return (
        stmt.join(TradeAreaOrm, fact_orm.trdar_code == TradeAreaOrm.code)
        .join(dong, TradeAreaOrm.region_code == dong.code)
        .join(gu, dong.parent_code == gu.code)
    ), gu


class AreaScorePgRepository(AreaScoreRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_header(self, trdar_code: int) -> AreaScoreHeader | None:
        dong = aliased(RegionOrm)
        gu = aliased(RegionOrm)
        row = (await self._session.execute(
            select(TradeAreaOrm.code, TradeAreaOrm.name, gu.name, gu.parent_code)
            .outerjoin(dong, TradeAreaOrm.region_code == dong.code)
            .outerjoin(gu, dong.parent_code == gu.code)
            .where(TradeAreaOrm.code == trdar_code)
        )).first()
        if row is None:
            return None
        code, name, gu_name, sido_code = row
        return AreaScoreHeader(
            trdar_code=code, trdar_name=name,
            district_name=gu_name or "", sido_code=sido_code,
        )

    async def find_sales_series(self, trdar_code: int, quarters: int) -> list[QuarterValue]:
        rows = (await self._session.execute(
            select(
                EstimatedSalesOrm.year_quarter,
                func.sum(EstimatedSalesOrm.monthly_sales_amount),
            )
            .where(EstimatedSalesOrm.trdar_code == trdar_code)
            .group_by(EstimatedSalesOrm.year_quarter)
            .order_by(EstimatedSalesOrm.year_quarter.desc())
            .limit(quarters)
        )).all()
        return [QuarterValue(year_quarter=yq, value=float(total)) for yq, total in reversed(rows)]

    async def find_floating_series(self, trdar_code: int, quarters: int) -> list[QuarterValue]:
        rows = (await self._session.execute(
            select(FloatingPopulationOrm.year_quarter, FloatingPopulationOrm.total_floating_pop)
            .where(FloatingPopulationOrm.trdar_code == trdar_code)
            .order_by(FloatingPopulationOrm.year_quarter.desc())
            .limit(quarters)
        )).all()
        return [QuarterValue(year_quarter=yq, value=float(total)) for yq, total in reversed(rows)]

    async def find_city_sales_series(self, sido_code: str, quarters: int) -> list[QuarterValue]:
        stmt, gu = _sido_join(
            select(
                EstimatedSalesOrm.year_quarter,
                func.sum(EstimatedSalesOrm.monthly_sales_amount),
            ),
            EstimatedSalesOrm,
        )
        rows = (await self._session.execute(
            stmt.where(gu.parent_code == sido_code)
            .group_by(EstimatedSalesOrm.year_quarter)
            .order_by(EstimatedSalesOrm.year_quarter.desc())
            .limit(quarters)
        )).all()
        return [QuarterValue(year_quarter=yq, value=float(total)) for yq, total in reversed(rows)]

    async def find_city_floating_series(
        self, sido_code: str, quarters: int
    ) -> list[QuarterValue]:
        stmt, gu = _sido_join(
            select(
                FloatingPopulationOrm.year_quarter,
                func.sum(FloatingPopulationOrm.total_floating_pop),
            ),
            FloatingPopulationOrm,
        )
        rows = (await self._session.execute(
            stmt.where(gu.parent_code == sido_code)
            .group_by(FloatingPopulationOrm.year_quarter)
            .order_by(FloatingPopulationOrm.year_quarter.desc())
            .limit(quarters)
        )).all()
        return [QuarterValue(year_quarter=yq, value=float(total)) for yq, total in reversed(rows)]

    async def find_store_health(self, trdar_code: int) -> StoreHealthStat | None:
        latest_quarter = (await self._session.execute(
            select(func.max(StoreOrm.year_quarter)).where(StoreOrm.trdar_code == trdar_code)
        )).scalar()
        if latest_quarter is None:
            return None
        opening, closure = (await self._session.execute(
            select(func.avg(StoreOrm.opening_rate), func.avg(StoreOrm.closure_rate))
            .where(StoreOrm.trdar_code == trdar_code, StoreOrm.year_quarter == latest_quarter)
        )).one()
        return StoreHealthStat(
            year_quarter=latest_quarter,
            opening_rate=float(opening), closure_rate=float(closure),
        )

    async def find_city_store_health(
        self, sido_code: str, year_quarter: int
    ) -> StoreHealthStat | None:
        stmt, gu = _sido_join(
            select(func.avg(StoreOrm.opening_rate), func.avg(StoreOrm.closure_rate)),
            StoreOrm,
        )
        opening, closure = (await self._session.execute(
            stmt.where(gu.parent_code == sido_code, StoreOrm.year_quarter == year_quarter)
        )).one()
        if opening is None or closure is None:
            return None
        return StoreHealthStat(
            year_quarter=year_quarter,
            opening_rate=float(opening), closure_rate=float(closure),
        )

    async def find_persistence(
        self, trdar_code: int, sido_code: str | None
    ) -> PersistenceStat | None:
        row = (await self._session.execute(
            select(CommercialChangeOrm.year_quarter, CommercialChangeOrm.operating_months_avg)
            .where(CommercialChangeOrm.trdar_code == trdar_code)
            .order_by(CommercialChangeOrm.year_quarter.desc())
            .limit(1)
        )).first()
        if row is None:
            return None
        year_quarter, operating = row
        region_avg = None
        if sido_code:
            region_avg = (await self._session.execute(
                select(CommercialChangeBenchmarkOrm.operating_months_avg).where(
                    CommercialChangeBenchmarkOrm.region_code == sido_code,
                    CommercialChangeBenchmarkOrm.year_quarter == year_quarter,
                )
            )).scalar()
        return PersistenceStat(
            year_quarter=year_quarter,
            operating_months_avg=float(operating),
            region_operating_months_avg=float(region_avg) if region_avg is not None else None,
        )
