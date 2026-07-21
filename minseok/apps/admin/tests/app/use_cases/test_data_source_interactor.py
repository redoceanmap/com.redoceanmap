from admin.app.use_cases.data_source_interactor import DataSourceInteractor
from hub.app.dtos.commercial_data_dto import DatasetStat
from hub.app.dtos.recommendation_directory_dto import RecommendationStats


class _StubCommercial:
    async def get_dataset_stats(self):
        return [DatasetStat(key="store", name="점포 현황", row_count=500, latest_label="20251")]


class _StubRecommendations:
    async def stats(self):
        return RecommendationStats(total=77, today=1, monthly=[], top_categories=[])


async def test_데이터소스는_market_현황에_추천_카운트를_덧붙인다():
    interactor = DataSourceInteractor(
        commercial=_StubCommercial(), recommendations=_StubRecommendations()
    )
    result = await interactor.list_datasets()
    keys = [d.key for d in result.datasets]
    assert keys == ["store", "recommendations"]
    assert result.datasets[-1].row_count == 77
