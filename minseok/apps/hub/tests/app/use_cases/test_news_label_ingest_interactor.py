from hub.app.dtos.news_label_dto import NewsLabelItem
from hub.app.use_cases.news_label_ingest_interactor import NewsLabelIngestInteractor


class _StubLabelStorage:
    def __init__(self):
        self.saved: list[NewsLabelItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)

    async def unlabeled(self, labeler, limit):
        return []


def _label(**overrides):
    base = dict(news_id=1, labeler="exaone-2.4b-awq", sentiment=0.7, event_type="실적", confidence=0.9)
    return NewsLabelItem(**{**base, **overrides})


async def test_라벨_적재는_범위_밖_라벨을_거른다():
    storage = _StubLabelStorage()
    saved = await NewsLabelIngestInteractor(storage).ingest([
        _label(),
        _label(news_id=2, sentiment=1.5),     # 감성 범위 밖
        _label(news_id=3, confidence=-0.1),   # 확신도 범위 밖
        _label(news_id=4, labeler=" "),       # 라벨러 없음
    ])
    assert saved == 1
    assert [i.news_id for i in storage.saved] == [1]
