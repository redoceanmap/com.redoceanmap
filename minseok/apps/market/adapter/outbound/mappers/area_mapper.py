from market.adapter.outbound.orm.trade_area_orm import TradeAreaOrm
from market.domain.entities.area_entity import Area
from market.domain.value_objects.area_vo import Coordinate

_REGION = "seoul"


class AreaMapper:
    """trade_area(+구분·지역 차원 조인) → Area(도메인) 변환을 담당한다."""

    @staticmethod
    def to_entity(
        ta: TradeAreaOrm,
        division_name: str,
        adm_dong_name: str | None,
        district_code: str | None,
        district_name: str | None,
    ) -> Area:
        return Area(
            trdar_code=ta.code,
            trdar_name=ta.name,
            trdar_div_code=ta.division_code,
            trdar_div_name=division_name,
            coordinate=Coordinate(x=ta.x_coord, y=ta.y_coord),
            district_code=int(district_code) if district_code else 0,
            district_name=district_name or "",
            adm_dong_code=int(ta.region_code) if ta.region_code else 0,
            adm_dong_name=adm_dong_name or "",
            area_size=int(ta.area_size) if ta.area_size is not None else 0,
            region=_REGION,
        )
