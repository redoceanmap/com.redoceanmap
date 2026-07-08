from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from mail.adapter.outbound.ai.ollama_embedding_adapter import OllamaEmbeddingAdapter
from mail.adapter.outbound.pg.inbound_mail_pg_repository import InboundMailPgRepository
from mail.app.ports.input.inbound_mail_use_case import InboundMailUseCase
from mail.app.use_cases.inbound_mail_interactor import InboundMailInteractor


def get_inbound_mail_use_case(db: AsyncSession = Depends(get_db)) -> InboundMailUseCase:
    return InboundMailInteractor(
        repository=InboundMailPgRepository(session=db),
        embeddings=OllamaEmbeddingAdapter(),
    )

