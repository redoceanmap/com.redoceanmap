from __future__ import annotations

from dataclasses import dataclass

from market.utils.coords import tm_to_wgs84


@dataclass(frozen=True, slots=True)
class Coordinate:
    """TM 좌표(엑스/와이)와 WGS84(위경도) 변환을 캡슐화한 값 객체."""

    x: int
    y: int

    @property
    def lat(self) -> float:
        return tm_to_wgs84(self.x, self.y)[0]

    @property
    def lng(self) -> float:
        return tm_to_wgs84(self.x, self.y)[1]
