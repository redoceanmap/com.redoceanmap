"""admin 앱 계약 예외 — 라우터가 HTTP 상태로 구분 매핑한다(chat app.exceptions 선례)."""


class GradeValidationError(ValueError):
    """등급 입력 검증 실패(탭 키·code 형식) — 400."""


class GradeProtectedError(ValueError):
    """보호 등급(admin) 삭제·개명 시도 — 409."""
