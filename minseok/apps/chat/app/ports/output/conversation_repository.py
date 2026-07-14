from abc import ABC, abstractmethod

from chat.domain.entities.conversation_entity import Conversation, ConversationSummary, Message


class ConversationRepository(ABC):
    """대화 영속성 아웃바운드 포트."""

    @abstractmethod
    async def create_conversation(self, user_id: int | None = None) -> Conversation: ...

    @abstractmethod
    async def add_message(
        self, conversation_id: int, role: str, content: str, payload: dict | None = None,
    ) -> Message: ...

    @abstractmethod
    async def get_messages(self, conversation_id: int, limit: int = 20) -> list[Message]: ...

    @abstractmethod
    async def get_conversation(self, conversation_id: int) -> Conversation | None: ...

    @abstractmethod
    async def list_conversations(self, user_id: int, limit: int = 30) -> list[ConversationSummary]:
        """사용자의 대화 목록(최신순). 제목은 첫 user 메시지 앞 40자."""
        ...
