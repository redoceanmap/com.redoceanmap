from __future__ import annotations

from fastapi import Depends

from hub.adapter.outbound.exaone_semantic_adapter import ExaoneSemanticAdapter
from hub.adapter.outbound.gemini_api_adapter import GeminiApiAdapter
from hub.adapter.outbound.log_semantic_record_adapter import LogSemanticRecordAdapter
from hub.app.ports.input.semantic_use_case import SemanticUseCase
from hub.app.ports.output.market_news_search_port import MarketNewsSearchPort
from hub.app.use_cases.semantic_interactor import SemanticInteractor
from hub.dependencies.market_news_search_provider import get_market_news_search_port


def get_semantic_use_case(
    market_news: MarketNewsSearchPort = Depends(get_market_news_search_port),
) -> SemanticUseCase:
    return SemanticInteractor(
        llm=ExaoneSemanticAdapter(),
        gemini=GeminiApiAdapter(),
        market_news=market_news,
        record=LogSemanticRecordAdapter(),
    )
