from hub.app.dtos.market_news_dto import MarketNewsItem
from hub.app.use_cases.market_news_ingest_interactor import MarketNewsIngestInteractor


class _StubStorage:
    def __init__(self):
        self.saved: list[MarketNewsItem] = []

    async def save_many(self, items):
        self.saved.extend(items)
        return len(items)


async def test_상권_뉴스_적재는_빈_항목을_거른다():
    storage = _StubStorage()
    saved = await MarketNewsIngestInteractor(storage).ingest([
        MarketNewsItem(title="성수 상권 리테일 진화", source="test", url="https://a", area_tag="성수"),
        MarketNewsItem(title="  ", source="test", url="https://b"),
        MarketNewsItem(title="제목만", source="test", url=""),
    ])
    assert saved == 1
    assert [i.url for i in storage.saved] == ["https://a"]
    assert storage.saved[0].area_tag == "성수"
