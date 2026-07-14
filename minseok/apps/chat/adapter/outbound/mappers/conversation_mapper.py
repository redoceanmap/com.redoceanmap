from chat.adapter.outbound.orm.conversation_orm import ConversationOrm, MessageOrm
from chat.domain.entities.conversation_entity import Conversation, Message


class ConversationMapper:
    """ConversationOrm(영속성) ↔ Conversation(도메인) 변환."""

    @staticmethod
    def to_entity(orm: ConversationOrm) -> Conversation:
        return Conversation(id=orm.id, created_at=orm.created_at, user_id=orm.user_id)


class MessageMapper:
    """MessageOrm(영속성) ↔ Message(도메인) 변환."""

    @staticmethod
    def to_entity(orm: MessageOrm) -> Message:
        return Message(
            id=orm.id,
            conversation_id=orm.conversation_id,
            role=orm.role,
            content=orm.content,
            created_at=orm.created_at,
            payload=orm.payload,
        )
