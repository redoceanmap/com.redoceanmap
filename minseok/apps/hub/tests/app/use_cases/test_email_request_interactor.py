from hub.app.dtos.email_request_dto import EmailRequestCommand
from hub.app.use_cases.email_request_interactor import EmailRequestInteractor
from hub.domain.email.email_ontology import OUTBOUND_EMAIL_DIRECTIVE, render_instruction


class _StubComposer:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    async def compose_and_send(self, to_email, instruction):
        self.calls.append((to_email, instruction))
        return "n8n 200"


def test_온톨로지_지시는_규범을_담는다():
    instruction = render_instruction("7월 상권 리포트 안내")
    assert OUTBOUND_EMAIL_DIRECTIVE.tone in instruction
    assert "인사말 → 핵심 본문 → 맺음말" in instruction
    assert "7월 상권 리포트 안내" in instruction


async def test_요청은_온톨로지_지시를_합성해_포트에_위임():
    composer = _StubComposer()
    result = await EmailRequestInteractor(composer).request(
        EmailRequestCommand(to_email="user@test.com", content="테스트 내용")
    )
    assert result.status == "sent" and result.detail == "n8n 200"
    to, instruction = composer.calls[0]
    assert to == "user@test.com"
    assert instruction == render_instruction("테스트 내용")
