from admin.app.dtos.recommendation_log_dto import RecommendationLogQuery
from admin.app.use_cases.recommendation_log_interactor import RecommendationLogInteractor
from hub.app.dtos.recommendation_directory_dto import RecommendationStats


class _StubRecommendations:
    def __init__(self):
        self.requested_limit = None

    async def stats(self):
        return RecommendationStats(total=100, today=5, monthly=[], top_categories=[])

    async def list_recent(self, limit):
        self.requested_limit = limit
        return []


async def test_기록_목록은_KPI와_함께_반환한다():
    stub = _StubRecommendations()
    result = await RecommendationLogInteractor(recommendations=stub).list_logs(
        RecommendationLogQuery(limit=50)
    )
    assert result.total == 100
    assert result.today == 5
    assert stub.requested_limit == 50


async def test_limit은_상한으로_보정한다():
    stub = _StubRecommendations()
    await RecommendationLogInteractor(recommendations=stub).list_logs(
        RecommendationLogQuery(limit=99999)
    )
    assert stub.requested_limit == 200
