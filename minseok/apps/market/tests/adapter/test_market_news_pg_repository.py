"""save_many의 행 단위 폴백 — 한 행이 거부돼도 배치 전체를 잃지 않는다.

상권 뉴스도 주식 뉴스와 같은 Google News RSS 수집원을 쓴다(같은 URL 길이 위험).
"""
from sqlalchemy.exc import DataError, OperationalError

from market.adapter.outbound.pg.market_news_pg_repository import MarketNewsPgRepository
from market.domain.entities.market_news_article import MarketNewsArticle


class _FakeResult:
    def __init__(self, count: int) -> None:
        self._count = count

    def scalars(self):
        return self

    def all(self):
        return list(range(self._count))


class _FakeSession:
    """지정한 url이 INSERT에 섞이면 DataError를 던지는 세션 대역."""

    def __init__(self, reject_url: str = "", error=None) -> None:
        self._reject_url = reject_url
        self._error = error or DataError(
            "INSERT ...", {}, Exception("value too long for type character varying")
        )
        self.batch_sizes: list[int] = []
        self.commits = 0
        self.rollbacks = 0

    async def execute(self, stmt):
        # ORM 대상 INSERT의 _multi_values 키는 문자열이 아니라 Column 객체다
        rows = [{col.name: val for col, val in row.items()} for row in stmt._multi_values[0]]
        self.batch_sizes.append(len(rows))
        if self._reject_url and any(r["url"] == self._reject_url for r in rows):
            raise self._error
        return _FakeResult(len(rows))

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


def _article(url: str) -> MarketNewsArticle:
    return MarketNewsArticle(title="제목", source="연합뉴스", url=url, area_tag="성수")


async def test_거부된_한_행만_건너뛰고_나머지는_저장된다():
    bad_url = "https://news.google.com/" + "A" * 3000
    articles = [_article(f"https://news.google.com/{i}") for i in range(19)]
    articles.insert(10, _article(bad_url))

    session = _FakeSession(reject_url=bad_url)
    saved = await MarketNewsPgRepository(session).save_many(articles)

    assert saved == 19  # 20건 중 19건 생존
    assert session.batch_sizes[0] == 20
    assert session.rollbacks == 2  # 배치 1회 + 거부된 행 1회


async def test_정상_배치는_일괄_INSERT_한_번으로_끝난다():
    session = _FakeSession()
    saved = await MarketNewsPgRepository(session).save_many(
        [_article(f"https://news.google.com/{i}") for i in range(20)]
    )

    assert saved == 20
    assert session.batch_sizes == [20]
    assert session.rollbacks == 0


async def test_btree_인덱스_초과도_행_단위로_되짚는다():
    """실측 회귀: 고엔트로피 URL 3000자는 DataError가 아니라 OperationalError로 온다."""
    bad_url = "https://news.google.com/" + "Z" * 3000
    session = _FakeSession(
        reject_url=bad_url,
        error=OperationalError("INSERT ...", {}, Exception("index row size 3064 exceeds btree")),
    )
    saved = await MarketNewsPgRepository(session).save_many(
        [_article("https://news.google.com/ok"), _article(bad_url)]
    )
    assert saved == 1
