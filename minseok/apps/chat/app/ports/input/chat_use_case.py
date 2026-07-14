from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from chat.app.dtos.chat_dto import AskResponse
from chat.domain.entities.conversation_entity import ConversationSummary, Message


class ChatUseCase(ABC):

    @abstractmethod
    async def ask(
        self, prompt: str, conversation_id: int | None = None, user_id: int | None = None,
    ) -> AskResponse: ...

    @abstractmethod
    def stream_reply(
        self, prompt: str, conversation_id: int | None = None, user_id: int | None = None,
    ) -> AsyncGenerator[dict, None]:
        """대화형 답변을 토큰 단위로 스트리밍한다(멀티턴 메모리 유지).
        이벤트: {"type": "meta", "conversationId": int} → {"type": "delta", "text": str}* → {"type": "done"}"""
        ...

    @abstractmethod
    async def list_conversations(self, user_id: int, limit: int = 30) -> list[ConversationSummary]:
        """사용자의 대화 목록(최신순)."""
        ...

    @abstractmethod
    async def conversation_messages(self, conversation_id: int, user_id: int) -> list[Message]:
        """대화 메시지 전체(payload 포함). 소유자 불일치·미존재는 ConversationNotFoundError."""
        ...
