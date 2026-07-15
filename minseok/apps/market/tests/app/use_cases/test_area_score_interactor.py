from market.app.dtos.area_score_dto import (
    AreaScoreHeader,
    AreaScoreQuery,
    PersistenceStat,
    StoreHealthStat,
)
from market.app.use_cases.area_score_interactor import AreaScoreInteractor
from market.domain.value_objects.area_score_vo import QuarterValue


def _qv(yq, value):
    return QuarterValue(year_quarter=yq, value=value)


class _StubRepo:
    def __init__(self, header=None, sales=None, floating=None, city_sales=None,
                 city_floating=None, store=None, city_store=None, persistence=None):
        self.header = header
        self.sales = sales or []
        self.floating = floating or []
        self.city_sales = city_sales or []
        self.city_floating = city_floating or []
        self.store = store
        self.city_store = city_store
        self.persistence = persistence
        self.city_store_requested: tuple | None = None

    async def find_header(self, trdar_code):
        return self.header

    async def find_sales_series(self, trdar_code, quarters):
        return self.sales

    async def find_floating_series(self, trdar_code, quarters):
        return self.floating

    async def find_city_sales_series(self, sido_code, quarters):
        return self.city_sales

    async def find_city_floating_series(self, sido_code, quarters):
        return self.city_floating

    async def find_store_health(self, trdar_code):
        return self.store

    async def find_city_store_health(self, sido_code, year_quarter):
        self.city_store_requested = (sido_code, year_quarter)
        return self.city_store

    async def find_persistence(self, trdar_code, sido_code):
        return self.persistence


_HEADER = AreaScoreHeader(
    trdar_code=1000123, trdar_name="성수동 카페거리", district_name="성동구", sido_code="11",
)


async def test_상권이_없으면_None을_반환한다():
    view = await AreaScoreInteractor(repo=_StubRepo()).get_score(AreaScoreQuery(trdar_code=999))
    assert view is None


async def test_4개_컴포넌트를_모두_채점한다():
    repo = _StubRepo(
        header=_HEADER,
        sales=[_qv(20253, 100), _qv(20254, 110)],  # QoQ +10%
        floating=[_qv(20253, 1000), _qv(20254, 1050)],  # QoQ +5%
        city_sales=[_qv(20253, 1000), _qv(20254, 1000)],  # QoQ 0%
        city_floating=[_qv(20253, 10000), _qv(20254, 10000)],  # QoQ 0%
        store=StoreHealthStat(year_quarter=20254, opening_rate=4.0, closure_rate=2.0),
        city_store=StoreHealthStat(year_quarter=20254, opening_rate=3.0, closure_rate=3.0),
        persistence=PersistenceStat(
            year_quarter=20254, operating_months_avg=125.0, region_operating_months_avg=100.0,
        ),
    )
    view = await AreaScoreInteractor(repo=repo).get_score(AreaScoreQuery(trdar_code=1000123))

    assert view.score is not None
    by_key = {c.key: c for c in view.score.components}
    assert set(by_key) == {"sales_growth", "floating_growth", "store_health", "persistence"}
    assert by_key["sales_growth"].score == 75.0  # +10%p 차이 / 캡 20 → 50+25
    assert by_key["floating_growth"].score == 62.5
    assert by_key["store_health"].score == 60.0  # 순증 +2 vs 0 / 캡 10 → 50+10
    assert by_key["persistence"].score == 75.0  # 상대비 +25% / 캡 50%
    assert view.score.total == 68.1
    assert view.score.grade == "양호"
    assert repo.city_store_requested == ("11", 20254)


async def test_추이는_매출과_유동인구를_분기_축으로_병합한다():
    repo = _StubRepo(
        header=_HEADER,
        sales=[_qv(20253, 100), _qv(20254, 110)],
        floating=[_qv(20252, 900), _qv(20253, 1000)],
    )
    view = await AreaScoreInteractor(repo=repo).get_score(AreaScoreQuery(trdar_code=1000123))

    assert [p.year_quarter for p in view.trend] == [20252, 20253, 20254]
    assert view.trend[0].monthly_sales is None
    assert view.trend[1].monthly_sales == 100
    assert view.trend[1].floating_qoq == 11.11
    assert view.trend[2].sales_qoq == 10.0
    assert view.trend[2].total_floating_pop is None


async def test_팩트가_전혀_없으면_score가_None인_view를_반환한다():
    view = await AreaScoreInteractor(repo=_StubRepo(header=_HEADER)).get_score(
        AreaScoreQuery(trdar_code=1000123)
    )
    assert view is not None
    assert view.score is None
    assert view.trend == []


async def test_시도_코드가_없으면_벤치마크_비교_컴포넌트를_제외한다():
    repo = _StubRepo(
        header=AreaScoreHeader(
            trdar_code=1, trdar_name="미연결 상권", district_name="", sido_code=None,
        ),
        sales=[_qv(20253, 100), _qv(20254, 110)],
        city_sales=[_qv(20253, 1000), _qv(20254, 1000)],
        store=StoreHealthStat(year_quarter=20254, opening_rate=4.0, closure_rate=2.0),
        persistence=PersistenceStat(
            year_quarter=20254, operating_months_avg=125.0, region_operating_months_avg=None,
        ),
    )
    view = await AreaScoreInteractor(repo=repo).get_score(AreaScoreQuery(trdar_code=1))
    assert view.score is None  # 성장·건강도·지속성 전부 벤치마크 없음 → 컴포넌트 0개
    assert len(view.trend) == 2  # 추이는 벤치마크 없이도 제공
