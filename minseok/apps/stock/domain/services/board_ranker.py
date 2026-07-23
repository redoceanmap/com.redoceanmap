"""신호 보드 정렬 규칙 (순수 도메인).

빈 워크스페이스에 워치리스트를 늘어놓을 때 "무엇을 먼저 보여줄 것인가"를 정한다.
정렬 축은 **신호 세기(|score|)**다 — 방향이 UP이라서가 아니라 신호가 뚜렷해서 위로 온다.
방향 자체에는 우열을 두지 않고 중립만 뒤로 민다. 매수 추천 순위가 아니다.
"""
from __future__ import annotations

_DIRECTION_RANK = {"UP": 0, "DOWN": 0, "NEUTRAL": 1}


def sort_key(direction: str, score: float, ticker: str) -> tuple[int, float, str]:
    """중립 후순위 → |score| 내림차순 → 티커 사전순(동점 안정화)."""
    return (_DIRECTION_RANK.get(direction, 1), -abs(score), ticker)
