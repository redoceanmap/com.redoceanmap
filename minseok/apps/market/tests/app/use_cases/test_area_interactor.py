from market.app.dtos.area_dto import AreaQuery
from market.app.use_cases.area_interactor import AreaInteractor


class _StubRepo:
    def __init__(self, areas=None, area=None):
        self.areas = areas or []
        self.area = area
        self.received_query = None
        self.received_trdar = None

    async def find_all(self, query):
        self.received_query = query
        return self.areas

    async def find_by_trdar(self, trdar_code):
        self.received_trdar = trdar_code
        return self.area


async def test_find_all은_쿼리를_저장소에_그대로_전달한다():
    repo = _StubRepo(areas=[object(), object()])
    query = AreaQuery(district_name="성동구")

    result = await AreaInteractor(repository=repo).find_all(query)

    assert repo.received_query is query
    assert len(result) == 2


async def test_find_by_trdar는_코드를_저장소에_전달한다():
    sentinel = object()
    repo = _StubRepo(area=sentinel)

    result = await AreaInteractor(repository=repo).find_by_trdar(1000123)

    assert repo.received_trdar == 1000123
    assert result is sentinel


async def test_find_by_trdar는_미존재_상권이면_None을_반환한다():
    repo = _StubRepo(area=None)
    assert await AreaInteractor(repository=repo).find_by_trdar(999) is None
