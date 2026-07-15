from hub.app.dtos.gemini_dto import GeminiAnswerQuery, GeminiAnswerResponse, GeminiQuery
from hub.app.use_cases.gemini_interactor import GeminiInteractor


class _StubGemini:
    async def generate(self, prompt):
        return GeminiAnswerResponse(answer=f"답변: {prompt}", model="gemini-test")


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_answer는_포트_답변을_반환하고_기록을_남긴다():
    record = _StubRecord()
    interactor = GeminiInteractor(gemini=_StubGemini(), record=record)
    result = await interactor.answer(GeminiAnswerQuery(prompt="카페 창업 조언"))
    assert result.answer == "답변: 카페 창업 조언"
    assert result.model == "gemini-test"
    assert record.records[0][0] == "answer"


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await GeminiInteractor(gemini=_StubGemini(), record=record).introduce_myself(
        GeminiQuery(id=9, name="제미나이 답변기 (hub/gemini)")
    )
    assert result.id == 9
    assert result.name == "제미나이 답변기 (hub/gemini)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
