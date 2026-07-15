from __future__ import annotations

from hub.adapter.outbound.gemini_api_adapter import GeminiApiAdapter
from hub.adapter.outbound.log_gemini_record_adapter import LogGeminiRecordAdapter
from hub.app.ports.input.gemini_use_case import GeminiUseCase
from hub.app.ports.output.gemini_answer_port import GeminiAnswerPort
from hub.app.use_cases.gemini_interactor import GeminiInteractor


def get_gemini_answer_port() -> GeminiAnswerPort:
    """허브가 직접 소유·구현하는 포트 — 스포크(chat)는 이 프로바이더로만 의존한다."""
    return GeminiApiAdapter()


def get_gemini_use_case() -> GeminiUseCase:
    return GeminiInteractor(gemini=GeminiApiAdapter(), record=LogGeminiRecordAdapter())
