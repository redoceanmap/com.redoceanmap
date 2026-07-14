from hub.app.dtos.news_dto import NewsItem
from hub.app.use_cases.news_ingest_interactor import NewsIngestInteractor


class _StubStorage:
    def __init__(self):
        self.saved: list[NewsItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)


async def test_뉴스_적재는_빈_항목을_거른다():
    storage = _StubStorage()
    saved = await NewsIngestInteractor(storage).ingest([
        NewsItem(title="삼성전자 실적 발표", source="test", url="https://a"),
        NewsItem(title="  ", source="test", url="https://b"),
        NewsItem(title="제목만", source="test", url=""),
    ])
    assert saved == 1
    assert [i.url for i in storage.saved] == ["https://a"]
