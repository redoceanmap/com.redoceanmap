from __future__ import annotations

from hub.adapter.outbound.gemini_api_adapter import GeminiApiAdapter
from hub.adapter.outbound.log_gemini_record_adapter import LogGeminiRecordAdapter
from hub.app.ports.input.gemini_use_case import GeminiUseCase
from hub.app.use_cases.gemini_interactor import GeminiInteractor


def get_gemini_use_case() -> GeminiUseCase:
    return GeminiInteractor(gemini=GeminiApiAdapter(), record=LogGeminiRecordAdapter())
