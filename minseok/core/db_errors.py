"""DB 예외 분류 — 행 문제와 인프라 장애를 가른다."""
from __future__ import annotations

from sqlalchemy.exc import DBAPIError


def is_infra_failure(error: DBAPIError) -> bool:
    """행 단위로 되짚어도 소용없는 인프라 장애인가.

    PostgreSQL이 거부한 오류에는 SQLSTATE가 붙는다(실측: btree 초과 54000, 길이 초과 22001).
    접속 자체가 실패한 오류(DB 재시작·연결 거부·호스트 이름 해석 실패)에는 SQLSTATE가 없다.
    후자를 행 문제로 오인해 되짚으면 전 행이 같은 이유로 "거부"돼 조용히 유실되므로,
    호출자가 재시도할 수 있게 배치 실패로 올려야 한다.
    """
    return error.connection_invalidated or getattr(error.orig, "sqlstate", None) is None
