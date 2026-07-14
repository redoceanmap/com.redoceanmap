from market.app.dtos.area_stats_dto import (
    AreaHeader,
    AreaStatsQuery,
    ChangeSummary,
    FloatingQuarter,
    SalesQuarter,
    ServiceRef,
    StoreQuarter,
)
from market.app.use_cases.area_stats_interactor import AreaStatsInteractor


def _floating(yq, total=1000):
    return FloatingQuarter(
        year_quarter=yq, total=total,
        age_10=10, age_20=20, age_30=30, age_40=40, age_50=50, age_60_plus=60,
        time_00_06=1, time_06_11=2, time_11_14=3, time_14_17=4, time_17_21=5, time_21_24=6,
    )


class _StubRepo:
    def __init__(self, header=None, service=None, sales=None, stores=None,
                 floating=None, change=None):
        self.header = header
        self.service = service
        self.sales = sales or []
        self.stores = stores or []
        self.floating = floating or []
        self.change = change
        self.requested_service: tuple | None = None

    async def find_header(self, trdar_code):
        return self.header

    async def resolve_service(self, trdar_code, service_code):
        self.requested_service = (trdar_code, service_code)
        return self.service

    async def find_sales(self, trdar_code, service_code, quarters):
        return self.sales

    async def find_stores(self, trdar_code, service_code, quarters):
        return self.stores

    async def find_floating(self, trdar_code, quarters):
        return self.floating

    async def find_change(self, trdar_code):
        return self.change


_HEADER = AreaHeader(trdar_code=1000123, trdar_name="성수동 카페거리", district_name="성동구")


async def test_상권이_없으면_None을_반환한다():
    view = await AreaStatsInteractor(stats=_StubRepo()).get_stats(
        AreaStatsQuery(trdar_code=999)
    )
    assert view is None


async def test_팩트들을_분기_축으로_병합한다():
    repo = _StubRepo(
        header=_HEADER,
        service=ServiceRef(code="CS100010", name="커피-음료"),
        sales=[
            SalesQuarter(year_quarter=20243, monthly_sales_amount=100, weekday_sales_amount=70),
            SalesQuarter(year_quarter=20244, monthly_sales_amount=120, weekday_sales_amount=80),
        ],
        stores=[
            StoreQuarter(year_quarter=20244, store_count=42, opening_rate=3.1,
                         closure_rate=2.4, franchise_store_count=12),
        ],
        floating=[_floating(20243), _floating(20244, total=2000)],
        change=ChangeSummary(
            change_indicator_name="상권확장",
            operating_months_avg=96.0,
            region_operating_months_avg=88.0,
        ),
    )
    view = await AreaStatsInteractor(stats=repo).get_stats(AreaStatsQuery(trdar_code=1000123))

    assert [q.year_quarter for q in view.series] == [20243, 20244]
    # 20243: 점포 팩트 없음 → None, 20244: 전 팩트 병합
    assert view.series[0].store_count is None
    assert view.series[1].monthly_sales == 120
    assert view.series[1].store_count == 42
    assert view.series[1].total_floating_pop == 2000
    assert view.latest_floating.year_quarter == 20244
    assert view.change.change_indicator_name == "상권확장"
    assert view.service_code == "CS100010"


async def test_지정한_service_code가_저장소에_전달된다():
    repo = _StubRepo(header=_HEADER, service=ServiceRef(code="CS100001", name="한식음식점"))
    await AreaStatsInteractor(stats=repo).get_stats(
        AreaStatsQuery(trdar_code=1000123, service_code="CS100001")
    )
    assert repo.requested_service == (1000123, "CS100001")


async def test_매출_팩트가_전혀_없으면_유동인구만으로_시계열을_만든다():
    repo = _StubRepo(header=_HEADER, service=None, floating=[_floating(20244)])
    view = await AreaStatsInteractor(stats=repo).get_stats(AreaStatsQuery(trdar_code=1000123))
    assert view.service_code is None
    assert [q.year_quarter for q in view.series] == [20244]
    assert view.series[0].monthly_sales is None
    assert view.series[0].total_floating_pop == 1000


async def test_quarters보다_긴_병합_축은_최근_구간으로_자른다():
    repo = _StubRepo(
        header=_HEADER,
        service=ServiceRef(code="CS100010", name="커피-음료"),
        sales=[
            SalesQuarter(year_quarter=yq, monthly_sales_amount=1, weekday_sales_amount=1)
            for yq in (20241, 20242, 20243)
        ],
        floating=[_floating(20244)],
    )
    view = await AreaStatsInteractor(stats=repo).get_stats(
        AreaStatsQuery(trdar_code=1000123, quarters=2)
    )
    assert [q.year_quarter for q in view.series] == [20243, 20244]
