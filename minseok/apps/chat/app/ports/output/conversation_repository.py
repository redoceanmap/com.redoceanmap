from abc import ABC, abstractmethod

from chat.domain.entities.conversation_entity import Conversation, Message


class ConversationRepository(ABC):
    """대화 영속성 아웃바운드 포트."""

    @abstractmethod
    async def create_conversation(self) -> Conversation: ...

    @abstractmethod
    async def add_message(self, conversation_id: int, role: str, content: str) -> Message: ...

    @abstractmethod
    async def get_messages(self, conversation_id: int, limit: int = 20) -> list[Message]: ...
