from hub.app.dtos.inbound_mail_dto import InboundMailItem
from hub.app.use_cases.mail_ingest_interactor import MailIngestInteractor


class _StubStorage:
    def __init__(self, result=True):
        self.result = result
        self.received: InboundMailItem | None = None

    async def save(self, item):
        self.received = item
        return self.result


def _item():
    return InboundMailItem(
        message_id="msg-001",
        subject="7월 정산 안내",
        sender="billing@example.com",
        recipient="me@example.com",
        preview="이번 달 정산 내역을 안내드립니다.",
    )


async def test_수신_메일을_저장_포트에_위임한다():
    storage = _StubStorage(result=True)
    saved = await MailIngestInteractor(storage=storage).receive(_item())
    assert saved is True
    assert storage.received.message_id == "msg-001"


async def test_중복_메일이면_False를_반환한다():
    storage = _StubStorage(result=False)
    saved = await MailIngestInteractor(storage=storage).receive(_item())
    assert saved is False
