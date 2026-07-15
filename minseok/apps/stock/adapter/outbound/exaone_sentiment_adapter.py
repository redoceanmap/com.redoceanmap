from __future__ import annotations

import logging
import re

from core.llm.llm_orchestrator import llm_orchestrator
from stock.app.ports.output.sentiment_port import SentimentPort
from stock.domain.value_objects.sentiment_score import SentimentScore

logger = logging.getLogger(__name__)

_PROMPT = (
    "다음 뉴스 헤드라인들의 시장 감성을 -1.0(매우 부정) ~ 1.0(매우 긍정) 사이의 "
    "소수 하나로만 답하라. 설명 없이 숫자만 출력한다.\n\n헤드라인:\n{headlines}"
)


def _parse_score(raw: str) -> float:
    match = re.search(r"-?\d+(?:\.\d+)?", raw)
    if not match:
        return 0.0
    return max(-1.0, min(1.0, float(match.group())))


class ExaoneSentimentAdapter(SentimentPort):
    """EXAONE(Ollama) 로 뉴스 감성을 점수화한다.

    대장이 LLM 추론이 필요할 때 위임하는 유일한 지점. 단일 모델(7.8B) 정책.
    """

    async def analyze(self, headlines: list[str]) -> SentimentScore:
        if not headlines:
            # 뉴스가 없으면(한국 종목 등) LLM을 부르지 않고 중립으로 둔다.
            return SentimentScore(value=0.0)
        prompt = _PROMPT.format(headlines="\n".join(f"- {h}" for h in headlines))
        raw = await llm_orchestrator.orchestrate(prompt)
        score = _parse_score(raw)
        logger.info("[exaone-sentiment] raw=%r → %.2f", raw.strip()[:40], score)
        return SentimentScore(value=score)
