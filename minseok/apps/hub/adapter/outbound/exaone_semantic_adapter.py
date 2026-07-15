from __future__ import annotations

import json
import logging

from core.llm.llm_orchestrator import llm_orchestrator
from hub.app.dtos.semantic_dto import SemanticRoute
from hub.app.ports.output.semantic_llm_port import SemanticLlmPort

logger = logging.getLogger(__name__)

_ROUTING_SYSTEM = """너는 입력된 질문의 의도를 분류하는 라우터다.
반드시 아래 JSON 형식으로만 응답하라. 다른 설명이나 텍스트는 절대 붙이지 마라.

출력 JSON 스키마:
{"destination": "crud" | "rag" | "gemini", "entities": ["질문 속 핵심 단어"]}

[분류 기준]
- "crud": 데이터의 생성·수정·삭제를 명확히 요구할 때 (예: "관심 종목에 삼성전자 추가해줘")
- "rag": 상권·창업·지역 시장 등 내부 데이터 근거가 필요한 질문 (예: "성수동 카페 상권 어때?")
- "gemini": 일상 대화·인사·일반 상식 등 내부 데이터가 필요 없는 질문 (예: "피보나치 수열이 뭐야?")

[예시]
질문: "홍대 앞 요즘 뜨는 업종 알려줘"
답변: {"destination": "rag", "entities": ["홍대", "업종"]}
질문: "내 추천 기록 삭제해줘"
답변: {"destination": "crud", "entities": ["추천 기록", "삭제"]}"""

_GROUNDED_SYSTEM = """너는 제공된 [Context]에만 근거해 사실을 전달하는 비서다.
[Context]에 없는 내용을 추측하거나 외부 지식으로 지어내는 것은 절대 허용되지 않는다.
근거가 부족하면 부족하다고 말하라. 한국어로 간결하게 답하라."""


class ExaoneSemanticAdapter(SemanticLlmPort):
    """오케스트레이터 기본 모델(EXAONE 7.8B)로 분류·근거 답변을 수행하는 어댑터.

    단일 모델 2역은 시스템 프롬프트 교체(동적 프롬프팅)로 구현한다 — QLoRA 없음(PoC).
    LLM 추론 수렴 규칙에 따라 직접 Ollama를 부르지 않고 오케스트레이터를 경유한다.
    """

    async def classify(self, question: str) -> SemanticRoute:
        raw = await llm_orchestrator.orchestrate(
            question, system=_ROUTING_SYSTEM, format="json"
        )
        try:
            decision = json.loads(raw)
            destination = str(decision.get("destination", "")).strip().lower()
            entities = tuple(
                str(entity).strip() for entity in decision.get("entities", []) if str(entity).strip()
            )[:5]
        except (json.JSONDecodeError, AttributeError, TypeError):
            logger.warning("[semantic] 분류 JSON 파싱 실패 → rag 폴백: %r", raw[:120])
            return SemanticRoute(destination="rag", entities=())
        return SemanticRoute(destination=destination, entities=entities)

    async def answer_grounded(self, question: str, context: str) -> str:
        return await llm_orchestrator.orchestrate(
            question, system=f"{_GROUNDED_SYSTEM}\n\n[Context]\n{context}"
        )
