from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from chat.adapter.outbound.mappers.conversation_mapper import ConversationMapper, MessageMapper
from chat.adapter.outbound.orm.conversation_orm import ConversationOrm, MessageOrm
from chat.app.ports.output.conversation_repository import ConversationRepository
from chat.domain.entities.conversation_entity import Conversation, Message


class ConversationPgRepository(ConversationRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_conversation(self) -> Conversation:
        orm = ConversationOrm()
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return ConversationMapper.to_entity(orm)

    async def add_message(self, conversation_id: int, role: str, content: str) -> Message:
        result = await self._session.execute(
            insert(MessageOrm)
            .values(conversation_id=conversation_id, role=role, content=content)
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
