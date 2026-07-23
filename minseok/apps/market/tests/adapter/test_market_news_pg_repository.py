"""save_many의 행 단위 폴백 — 한 행이 거부돼도 배치 전체를 잃지 않는다.

상권 뉴스도 주식 뉴스와 같은 Google News RSS 수집원을 쓴다(같은 URL 길이 위험).
"""
import pytest
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


def _server_error(exc_type, message: str, sqlstate: str):
    """서버가 거부한 오류 대역 — 실제 psycopg 오류처럼 SQLSTATE를 갖는다.

    접속 실패(SQLSTATE 없음)와 구분하는 기준이므로 대역도 실물과 같아야 한다.
    """
    orig = Exception(message)
    orig.sqlstate = sqlstate
    return exc_type("INSERT ...", {}, orig)


class _FakeSession:
    """지정한 url이 INSERT에 섞이면 DataError를 던지는 세션 대역."""

    def __init__(self, reject_url: str = "", error=None) -> None:
        self._reject_url = reject_url
        self._error = error or _server_error(
            DataError, "value too long for type character varying", "22001"
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
        error=_server_error(OperationalError, "index row size 3064 exceeds btree", "54000"),
    )
    saved = await MarketNewsPgRepository(session).save_many(
        [_article("https://news.google.com/ok"), _article(bad_url)]
    )
    assert saved == 1


async def test_접속_실패는_되짚지_않고_그대로_터뜨린다():
    """실측 회귀(2026-07-22 재배포): DB 재시작 중 접속 실패는 SQLSTATE가 없다.

    행 문제로 오인해 되짚으면 전 행이 같은 이유로 "거부"돼 조용히 유실된다.
    """
    bad_url = "https://news.google.com/dead"
    err = OperationalError(
        "INSERT ...", {}, Exception("connection failed: ... Connection refused"),
    )  # 접속 실패 — orig에 sqlstate 없음, connection_invalidated도 False

    session = _FakeSession(reject_url=bad_url, error=err)
    with pytest.raises(OperationalError):
        await MarketNewsPgRepository(session).save_many([_article(bad_url), _article("https://ok")])
    assert session.batch_sizes == [2]  # 폴백 진입 없음
