from __future__ import annotations

from mail.app.ports.output.judge_clue_port import JudgeCluePort


class FakeJudgeClueAdapter(JudgeCluePort):
    """실단서(pgvector 유사 메일 검색) 연동 전 임시 가짜 단서. 고정값을 반환한다."""

    async def find_clues(self, query: str, limit: int = 5) -> list[str]:
        return [
            "발신자의 이전 문의 이력 없음",
            "본문에 보고서 요청 키워드 없음",
            "일반 문의로 분류할 근거 충분",
        ][:limit]
