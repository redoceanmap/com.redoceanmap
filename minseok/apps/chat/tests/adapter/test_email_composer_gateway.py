from chat.adapter.outbound.gateways import email_composer_gateway as gw_module
from chat.adapter.outbound.gateways.email_composer_gateway import EmailComposerN8nGateway


async def test_LLM_결과를_n8n_페이로드로_발송(monkeypatch):
    async def fake_orchestrate(prompt, **kwargs):
        assert "작성 지시" in prompt
        return '{"subject": "테스트 제목", "body": "안녕하세요.\\n본문입니다."}'

    sent: list[dict] = []

    async def fake_send(self, payload):
        sent.append(payload)
        return "n8n 200"

    monkeypatch.setattr(gw_module.llm_orchestrator, "orchestrate", fake_orchestrate)
    monkeypatch.setattr(EmailComposerN8nGateway, "_send", fake_send)

    detail = await EmailComposerN8nGateway().compose_and_send("user@test.com", "지시문")
    assert detail == "n8n 200"
    assert sent[0]["to"] == "user@test.com"
    assert sent[0]["subject"] == "테스트 제목"
    assert "본문입니다" in sent[0]["body"]
