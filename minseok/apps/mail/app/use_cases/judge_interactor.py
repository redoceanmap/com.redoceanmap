from __future__ import annotations

import logging

from mail.app.dtos.judge_dto import JudgeQuery, JudgeResponse
from mail.app.ports.input.judge_use_case import JudgeUseCase
from mail.app.ports.output.judge_clue_port import JudgeCluePort

logger = logging.getLogger(__name__)


class JudgeInteractor(JudgeUseCase):
    """저지(Judge) 대장 — 현재는 자기소개 스켈레톤.

    향후 역할(watcher_router 설계안의 Case A 처리자): 왓처가 넘긴 일반 메일의 단서를
    JudgeCluePort로 수집·종합해 최종 판단(응답/분류 결론)을 내리는 핵심 추론 담당.
    """

    def __init__(self, clues: JudgeCluePort) -> None:
        self._clues = clues

    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse:
        clues = await self._clues.find_clues(query="자기소개")
        logger.info("[judge/myself] id=%s name=%s clues=%d", query.id, query.name, len(clues))
        return JudgeResponse(
            id=query.id,
            name=query.name,
            introduction=(
                "일반 메일의 최종 판단 담당입니다. 현재는 스켈레톤 단계로, 단서 포트에서 "
                f"유사 사례를 조회해 결론을 도출하는 자리입니다. 현재 확보한 단서는 {len(clues)}건입니다."
            ),
        )
