from datetime import datetime, timezone

from admin.app.use_cases.data_source_interactor import DataSourceInteractor
from hub.app.dtos.commercial_data_dto import DatasetStat
from hub.app.dtos.price_bar_dto import PriceCoverageItem
from hub.app.dtos.recommendation_directory_dto import RecommendationStats


class _StubCommercial:
    async def get_dataset_stats(self):
        return [DatasetStat(key="store", name="점포 현황", row_count=500, latest_label="20251")]


class _StubRecommendations:
    async def stats(self):
        return RecommendationStats(total=77, today=1, monthly=[], top_categories=[])


class _StubPrices:
    def __init__(self, items):
        self._items = items

    async def coverage(self):
        return self._items

    async def save_many(self, items):
        raise NotImplementedError


def _coverage_item(ticker, bars, last_ts):
    return PriceCoverageItem(
        ticker=ticker,
        timeframe="1d",
        first_ts=datetime(2025, 1, 2, tzinfo=timezone.utc),
        last_ts=last_ts,
        bars=bars,
    )


async def test_데이터소스는_market_현황에_추천과_주가봉_카운트를_덧붙인다():
    latest = datetime(2026, 7, 18, tzinfo=timezone.utc)
    interactor = DataSourceInteractor(
        commercial=_StubCommercial(),
        recommendations=_StubRecommendations(),
        prices=_StubPrices(
            [
                _coverage_item("005930.KS", 300, datetime(2026, 7, 17, tzinfo=timezone.utc)),
                _coverage_item("AAPL", 200, latest),
            ]
        ),
    )
    result = await interactor.list_datasets()
    keys = [d.key for d in result.datasets]
    assert keys == ["store", "recommendations", "price_bars"]
    assert result.datasets[1].row_count == 77
    assert result.datasets[-1].row_count == 500
    assert result.datasets[-1].latest_label == latest.isoformat()


async def test_주가봉이_없으면_빈_카드로_동작한다():
    interactor = DataSourceInteractor(
        commercial=_StubCommercial(),
        recommendations=_StubRecommendations(),
        prices=_StubPrices([]),
    )
    result = await interactor.list_datasets()
    bars = result.datasets[-1]
    assert bars.key == "price_bars"
    assert bars.row_count == 0
    assert bars.latest_label is None
