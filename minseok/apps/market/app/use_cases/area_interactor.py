from market.app.dtos.area_dto import AreaQuery
from market.app.ports.input.area_use_case import AreaUseCase
from market.app.ports.output.area_repository import AreaRepository
from market.domain.entities.area_entity import Area


class AreaInteractor(AreaUseCase):

    def __init__(self, repository: AreaRepository) -> None:
        self._repository = repository

    async def find_all(self, query: AreaQuery) -> list[Area]:
        return await self._repository.find_all(query)

    async def find_by_trdar(self, trdar_code: int) -> Area | None:
        return await self._repository.find_by_trdar(trdar_code)
