"""chat 앱 계층 예외. HTTP 상태코드 변환은 인바운드 어댑터(라우터)가 맡는다."""


class ChatError(Exception):
    """chat 유스케이스 공통 예외."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class CommercialDataUnavailableError(ChatError):
    """상권 데이터가 아직 적재되지 않음."""


class InvalidLLMResponseError(ChatError):
    """LLM 응답을 파싱/해석할 수 없음."""


class NoValidAreaError(ChatError):
    """LLM이 고른 상권 중 유효한 것이 없음."""


class ConversationNotFoundError(ChatError):
    """대화가 없거나 요청한 사용자의 소유가 아님 (존재 여부 비노출)."""
