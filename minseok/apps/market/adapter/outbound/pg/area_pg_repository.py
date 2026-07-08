from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from market.adapter.outbound.mappers.area_mapper import AreaMapper
from market.adapter.outbound.orm.region_orm import RegionOrm
from market.adapter.outbound.orm.trade_area_division_orm import TradeAreaDivisionOrm
from market.adapter.outbound.orm.trade_area_orm import TradeAreaOrm
from market.app.dtos.area_dto import AreaQuery
from market.app.ports.output.area_repository import AreaRepository
from market.domain.entities.area_entity import Area


class AreaPgRepository(AreaRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _joined_stmt(self):
        """trade_area → 구분 + 행정동(→자치구) 조인. (stmt, 자치구alias) 반환."""
        dong = aliased(RegionOrm)  # 행정동(level2)
        gu = aliased(RegionOrm)    # 자치구(level1)
        stmt = (
            select(TradeAreaOrm, TradeAreaDivisionOrm.name, dong.name, gu.code, gu.name)
            .join(TradeAreaDivisionOrm, TradeAreaOrm.division_code == TradeAreaDivisionOrm.code)
            .outerjoin(dong, TradeAreaOrm.region_code == dong.code)
            .outerjoin(gu, dong.parent_code == gu.code)
        )
        return stmt, gu

    async def find_all(self, query: AreaQuery) -> list[Area]:
        stmt, gu = self._joined_stmt()
        if query.district_name:
            stmt = stmt.where(gu.name == query.district_name)
        result = await self._session.execute(stmt)
        return [
            AreaMapper.to_entity(ta, div_name, dong_name, gu_code, gu_name)
            for ta, div_name, dong_name, gu_code, gu_name in result.all()
        ]

    async def find_by_trdar(self, trdar_code: int) -> Area | None:
        stmt, _ = self._joined_stmt()
        stmt = stmt.where(TradeAreaOrm.code == trdar_code)
        row = (await self._session.execute(stmt)).first()
        if row is None:
            return None
        ta, div_name, dong_name, gu_code, gu_name = row
        return AreaMapper.to_entity(ta, div_name, dong_name, gu_code, gu_name)
