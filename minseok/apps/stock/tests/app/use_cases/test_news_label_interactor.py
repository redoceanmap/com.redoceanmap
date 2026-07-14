from stock.app.dtos.news_label_dto import UnlabeledNews
from stock.app.use_cases.news_label_interactor import NewsLabelInteractor
from stock.domain.entities.news_label import NewsLabel


class _StubRepo:
    def __init__(self):
        self.saved: list[NewsLabel] = []

    async def save_many(self, labels):
        self.saved.extend(labels)
        return len(labels)

    async def unlabeled(self, labeler, limit):
        return [UnlabeledNews(news_id=7, ticker="NVDA", title="엔비디아 실적 발표")]


async def test_적재는_저장_신규_건수를_반환한다():
    repo = _StubRepo()
    saved = await NewsLabelInteractor(labels=repo).ingest([
        NewsLabel(news_id=7, labeler="exaone-2.4b-awq", sentiment=0.5, event_type="실적", confidence=0.8)
    ])
    assert saved == 1
    assert repo.saved[0].news_id == 7


async def test_미라벨_조회는_저장소_결과를_그대로_반환한다():
    rows = await NewsLabelInteractor(labels=_StubRepo()).unlabeled("exaone-2.4b-awq", 10)
    assert rows[0].news_id == 7
    assert rows[0].ticker == "NVDA"
