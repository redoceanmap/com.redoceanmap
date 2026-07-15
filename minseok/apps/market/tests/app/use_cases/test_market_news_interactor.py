from market.app.dtos.market_news_search_dto import MarketNewsSearchRow
from market.app.use_cases.market_news_interactor import MarketNewsInteractor
from market.domain.entities.market_news_article import MarketNewsArticle


class _StubRepository:
    def __init__(self, pending: list[tuple[int, str]] | None = None):
        self.pending = pending or []
        self.saved: list[MarketNewsArticle] = []
        self.embeddings: list[tuple[int, list[float]]] = []
        self.search_args: tuple | None = None

    async def save_many(self, articles):
        self.saved.extend(articles)
        return len(articles)

    async def unembedded(self, limit=200):
        return self.pending[:limit]

    async def set_embeddings(self, items):
        self.embeddings.extend(items)
        return len(items)

    async def search_similar(self, embedding, limit=4):
        self.search_args = (embedding, limit)
        return [MarketNewsSearchRow(id=1, title="성수 상권 기사", area_tag="성수",
                                    source="t", published_at=None)]


class _StubEmbeddings:
    def __init__(self, fail: bool = False):
        self.fail = fail

    async def embed(self, text):
        if self.fail:
            raise RuntimeError("Ollama down")
        return [0.1] * 4

    async def embed_many(self, texts):
        if self.fail:
            raise RuntimeError("Ollama down")
        return [[0.1] * 4 for _ in texts]


def _article() -> MarketNewsArticle:
    return MarketNewsArticle(title="제목", source="t", url="https://a", area_tag="성수")


async def test_적재_후_미임베딩분을_배치_임베딩한다():
    repo = _StubRepository(pending=[(1, "제목1"), (2, "제목2")])
    saved = await MarketNewsInteractor(news=repo, embeddings=_StubEmbeddings()).ingest([_article()])
    assert saved == 1
    assert [row_id for row_id, _ in repo.embeddings] == [1, 2]


async def test_임베딩_실패해도_적재는_성공하고_NULL_유지():
    repo = _StubRepository(pending=[(1, "제목1")])
    saved = await MarketNewsInteractor(
        news=repo, embeddings=_StubEmbeddings(fail=True)
    ).ingest([_article()])
    assert saved == 1
    assert repo.embeddings == []


async def test_검색은_질의를_임베딩해_유사도_검색에_넘긴다():
    repo = _StubRepository()
    rows = await MarketNewsInteractor(news=repo, embeddings=_StubEmbeddings()).search(
        "성수동 분위기", limit=4
    )
    assert repo.search_args == ([0.1] * 4, 4)
    assert rows[0].title == "성수 상권 기사"


async def test_질의_임베딩_실패면_빈_결과():
    repo = _StubRepository()
    rows = await MarketNewsInteractor(
        news=repo, embeddings=_StubEmbeddings(fail=True)
    ).search("아무 질의")
    assert rows == []
    assert repo.search_args is None


async def test_임베딩_어댑터가_없으면_검색은_빈_결과():
    rows = await MarketNewsInteractor(news=_StubRepository(), embeddings=None).search("질의")
    assert rows == []
