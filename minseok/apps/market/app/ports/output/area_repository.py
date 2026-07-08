from abc import ABC, abstractmethod

from market.app.dtos.area_dto import AreaQuery
from market.domain.entities.area_entity import Area


class AreaRepository(ABC):

    @abstractmethod
    async def find_all(self, query: AreaQuery) -> list[Area]: ...

    @abstractmethod
    async def find_by_trdar(self, trdar_code: int) -> Area | None: ...
