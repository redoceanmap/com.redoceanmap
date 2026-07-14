from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from chat.adapter.outbound.mappers.conversation_mapper import ConversationMapper, MessageMapper
from chat.adapter.outbound.orm.conversation_orm import ConversationOrm, MessageOrm
from chat.app.ports.output.conversation_repository import ConversationRepository
from chat.domain.entities.conversation_entity import Conversation, ConversationSummary, Message


class ConversationPgRepository(ConversationRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_conversation(self, user_id: int | None = None) -> Conversation:
        orm = ConversationOrm(user_id=user_id)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return ConversationMapper.to_entity(orm)

    async def add_message(
        self, conversation_id: int, role: str, content: str, payload: dict | None = None,
    ) -> Message:
        result = await self._session.execute(
            insert(MessageOrm)
            .values(conversation_id=conversation_id, role=role, content=content, payload=payload)
            .returning(MessageOrm)
        )
        await self._session.commit()
        return MessageMapper.to_entity(result.scalar_one())

    async def get_messages(self, conversation_id: int, limit: int = 20) -> list[Message]:
        result = await self._session.execute(
            select(MessageOrm)
            .where(MessageOrm.conversation_id == conversation_id)
            .order_by(MessageOrm.id)
            .limit(limit)
        )
        return [MessageMapper.to_entity(o) for o in result.scalars().all()]

    async def get_conversation(self, conversation_id: int) -> Conversation | None:
        orm = (await self._session.execute(
            select(ConversationOrm).where(ConversationOrm.id == conversation_id)
        )).scalar_one_or_none()
        return ConversationMapper.to_entity(orm) if orm else None

    async def list_conversations(self, user_id: int, limit: int = 30) -> list[ConversationSummary]:
        first_user_message = (
            select(MessageOrm.content)
            .where(MessageOrm.conversation_id == ConversationOrm.id, MessageOrm.role == "user")
            .order_by(MessageOrm.id)
            .limit(1)
            .scalar_subquery()
        )
        rows = (await self._session.execute(
            select(ConversationOrm, first_user_message)
            .where(ConversationOrm.user_id == user_id)
            .order_by(ConversationOrm.id.desc())
            .limit(limit)
        )).all()
        return [
            ConversationSummary(
                id=orm.id,
                title=(first or "").strip()[:40] or "새 대화",
                created_at=orm.created_at,
            )
            for orm, first in rows
        ]
