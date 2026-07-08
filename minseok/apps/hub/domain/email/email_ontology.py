from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailDirective:
    """발신 이메일 작성 온톨로지가 스포크에 내리는 작성 지시(규범).

    허브가 공개하는 전역 온톨로지의 일부이며, 외부 의존 없는 순수 도메인이다.
    (ragwatson star_craft 패턴 — 허브가 앱 공통 상위 개념을 소유한다.)
    """

    tone: str
    structure: tuple[str, ...]
    language: str


# 발신 이메일 작성 온톨로지 — 허브가 규정하는 작성 규범.
OUTBOUND_EMAIL_DIRECTIVE = EmailDirective(
    tone="정중하고 간결한",
    structure=("인사말", "핵심 본문", "맺음말"),
    language="한국어",
)


def render_instruction(content: str, directive: EmailDirective = OUTBOUND_EMAIL_DIRECTIVE) -> str:
    """사용자 내용 + 온톨로지 지시를 스포크가 따를 작성 지침 문자열로 합성한다. 순수 함수."""
    structure = " → ".join(directive.structure)
    return (
        f"{directive.tone} {directive.language} 이메일을 작성해줘. "
        f"구조는 [{structure}] 순서를 따르고, 아래 내용을 담아줘.\n\n{content}"
    )
