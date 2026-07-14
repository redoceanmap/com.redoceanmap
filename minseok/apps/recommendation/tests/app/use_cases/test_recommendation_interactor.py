from recommendation.app.dtos.recommendation_dto import RecommendationDraft
from recommendation.app.use_cases.recommendation_interactor import RecommendationInteractor


def _draft():
    return RecommendationDraft(
        trdar_code=1000123,
        trdar_name="성수동 카페거리",
        district_name="성동구",
        category="커피-음료",
        reason="유동인구 증가 추세",
        lat=37.544,
        lng=127.056,
    )


class _StubRepo:
    def __init__(self):
        self.saved: tuple | None = None
        self.requested_limit: int | None = None
        self.requested_conversation: int | None = None

    async def save_many(self, conversation_id, drafts):
        self.saved = (conversation_id, drafts)
        return list(drafts)

    async def list_recent(self, limit=50):
        self.requested_limit = limit
        return []

    async def find_by_conversation(self, conversation_id):
        self.requested_conversation = conversation_id
        return []


async def test_빈_초안이면_저장소를_호출하지_않는다():
    repo = _StubRepo()
    result = await RecommendationInteractor(repository=repo).record(1, [])
    assert result == []
    assert repo.saved is None


async def test_초안들을_대화_id와_함께_저장소에_위임한다():
    repo = _StubRepo()
    drafts = [_draft(), _draft()]
    result = await RecommendationInteractor(repository=repo).record(7, drafts)
    assert repo.saved == (7, drafts)
    assert len(result) == 2


async def test_list_recent는_limit을_저장소에_전달한다():
    repo = _StubRepo()
    await RecommendationInteractor(repository=repo).list_recent(10)
    assert repo.requested_limit == 10


async def test_find_by_conversation은_대화_id를_저장소에_전달한다():
    repo = _StubRepo()
    await RecommendationInteractor(repository=repo).find_by_conversation(42)
    assert repo.requested_conversation == 42
