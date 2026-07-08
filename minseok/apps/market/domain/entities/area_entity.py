from __future__ import annotations

from dataclasses import dataclass

from market.domain.value_objects.area_vo import Coordinate


@dataclass(frozen=True, slots=True)
class Area:
    """상권 영역 도메인 엔티티 — ORM/프레임워크에 의존하지 않는다."""

    trdar_code: int
    trdar_name: str
    trdar_div_code: str
    trdar_div_name: str
    coordinate: Coordinate
    district_code: int
    district_name: str
    adm_dong_code: int
    adm_dong_name: str
    area_size: int
    region: str

    @property
    def x_coord(self) -> int:
        return self.coordinate.x

    @property
    def y_coord(self) -> int:
        return self.coordinate.y

    @property
    def lat(self) -> float:
        return self.coordinate.lat

    @property
    def lng(self) -> float:
        return self.coordinate.lng
