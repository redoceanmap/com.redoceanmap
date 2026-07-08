from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from mail.adapter.outbound.orm.inbound_mail_orm import InboundMailOrm
from mail.app.ports.output.inbound_mail_repository import InboundMailRepositoryPort
from mail.domain.entities.inbound_mail import InboundMail


def _to_entity(orm: InboundMailOrm) -> InboundMail:
    return InboundMail(
        id=orm.id,
        message_id=orm.message_id,
        subject=orm.subject,
        sender=orm.sender,
        recipient=orm.recipient,
        preview=orm.preview,
        received_at=orm.received_at,
    )


class InboundMailPgRepository(InboundMailRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, mail: InboundMail, embedding: list[float] | None = None) -> bool:
        stmt = (
            pg_insert(InboundMailOrm)
            .values(
                message_id=mail.message_id,
                subject=mail.subject,
                sender=mail.sender,
                recipient=mail.recipient,
                preview=mail.preview,
                embedding=embedding,
            )
            .on_conflict_do_nothing(index_elements=["message_id"])
            .returning(InboundMailOrm.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none() is not None

    async def list_recent(self, limit: int = 50) -> list[InboundMail]:
        stmt = select(InboundMailOrm).order_by(InboundMailOrm.id.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return [_to_entity(orm) for orm in result.scalars().all()]

    async def search_similar(self, embedding: list[float], limit: int = 5) -> list[InboundMail]:
        stmt = (
            select(InboundMailOrm)
            .where(InboundMailOrm.embedding.is_not(None))
            .order_by(InboundMailOrm.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(orm) for orm in result.scalars().all()]
