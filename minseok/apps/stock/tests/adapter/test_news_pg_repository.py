"""save_many의 행 단위 폴백 — 한 행이 거부돼도 배치 전체를 잃지 않는다.

수집 URL 길이 초과(StringDataRightTruncation)로 40건 배치가 통째로 롤백되던 회귀를 고정한다.
"""
import pytest
from sqlalchemy.exc import DataError, OperationalError

from stock.adapter.outbound.pg.news_pg_repository import NewsPgRepository
from stock.domain.entities.news_article import NewsArticle


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


def _article(url: str) -> NewsArticle:
    return NewsArticle(title="제목", source="연합뉴스", url=url, ticker="005930.KS")


async def test_거부된_한_행만_건너뛰고_나머지는_저장된다():
    bad_url = "https://news.google.com/" + "A" * 3000
    articles = [_article(f"https://news.google.com/{i}") for i in range(39)]
    articles.insert(20, _article(bad_url))  # 배치 중간에 섞는다

    session = _FakeSession(reject_url=bad_url)
    saved = await NewsPgRepository(session).save_many(articles)

    assert saved == 39  # 40건 중 39건 생존 — 배치 전멸(0건)이 아니다
    assert session.batch_sizes[0] == 40  # 먼저 일괄 INSERT를 시도하고
    assert session.batch_sizes[1:] == [1] * 40  # 실패 시에만 행 단위로 되짚는다
    assert session.rollbacks == 2  # 배치 1회 + 거부된 행 1회
    assert session.commits == 39


async def test_정상_배치는_일괄_INSERT_한_번으로_끝난다():
    session = _FakeSession()
    saved = await NewsPgRepository(session).save_many(
        [_article(f"https://news.google.com/{i}") for i in range(40)]
    )

    assert saved == 40
    assert session.batch_sizes == [40]  # 행 단위 폴백은 타지 않는다
    assert session.commits == 1
    assert session.rollbacks == 0


async def test_btree_인덱스_초과도_행_단위로_되짚는다():
    """실측 회귀: 고엔트로피 URL 3000자는 DataError가 아니라 OperationalError로 온다.

    (psycopg.errors.ProgramLimitExceeded — index row size N exceeds btree maximum 2704)
    """
    bad_url = "https://news.google.com/" + "Z" * 3000
    articles = [_article("https://news.google.com/ok"), _article(bad_url)]

    session = _FakeSession(
        reject_url=bad_url,
        error=OperationalError("INSERT ...", {}, Exception("index row size 3064 exceeds btree")),
    )
    assert await NewsPgRepository(session).save_many(articles) == 1


async def test_연결_유실은_되짚지_않고_그대로_터뜨린다():
    """행 문제가 아니므로 폴백이 무의미하다 — 40번 재시도하며 시간만 버리면 안 된다."""
    bad_url = "https://news.google.com/dead"
    err = OperationalError("INSERT ...", {}, Exception("server closed the connection"))
    err.connection_invalidated = True

    session = _FakeSession(reject_url=bad_url, error=err)
    with pytest.raises(OperationalError):
        await NewsPgRepository(session).save_many([_article(bad_url)])
    assert session.batch_sizes == [1]  # 폴백 진입 없음


async def test_빈_입력은_세션을_건드리지_않는다():
    session = _FakeSession()
    assert await NewsPgRepository(session).save_many([]) == 0
    assert session.batch_sizes == []
