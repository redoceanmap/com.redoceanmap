from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from chat.app.dtos.chat_dto import AskResponse


class ChatUseCase(ABC):

    @abstractmethod
    async def ask(self, prompt: str, conversation_id: int | None = None) -> AskResponse: ...

    @abstractmethod
    def stream_reply(
        self, prompt: str, conversation_id: int | None = None,
    ) -> AsyncGenerator[dict, None]:
        """대화형 답변을 토큰 단위로 스트리밍한다(멀티턴 메모리 유지).
        이벤트: {"type": "meta", "conversationId": int} → {"type": "delta", "text": str}* → {"type": "done"}"""
        ...
