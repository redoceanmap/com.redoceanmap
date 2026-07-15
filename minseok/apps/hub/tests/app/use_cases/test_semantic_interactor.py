from datetime import datetime

from hub.app.dtos.gemini_dto import GeminiAnswerResponse
from hub.app.dtos.market_news_dto import MarketNewsHit
from hub.app.dtos.semantic_dto import SemanticAskQuery, SemanticQuery, SemanticRoute
from hub.app.use_cases.semantic_interactor import SemanticInteractor


class _StubLlm:
    def __init__(self, route):
        self._route = route

    async def classify(self, question):
        return self._route

    async def answer_grounded(self, question, context):
        return f"근거 답변({context.count('-')}건 근거)"


class _StubGemini:
    async def generate(self, prompt):
        return GeminiAnswerResponse(answer="제미나이 답변", model="gemini-test")


class _StubNews:
    def __init__(self, hits):
        self._hits = hits

    async def search(self, query, limit=4):
        return self._hits


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


def _interactor(route, hits=()):
    return SemanticInteractor(
        llm=_StubLlm(route),
        gemini=_StubGemini(),
        market_news=_StubNews(list(hits)),
        record=_StubRecord(),
    )


async def test_crud_분기는_실행_없이_감지만_보고한다():
    result = await _interactor(SemanticRoute("crud", ("추천 기록", "삭제"))).ask(
        SemanticAskQuery(prompt="내 추천 기록 삭제해줘")
    )
    assert result.destination == "crud"
    assert "CRUD PoC" in result.answer


async def test_gemini_분기는_외부_API_답변을_반환한다():
    result = await _interactor(SemanticRoute("gemini", ())).ask(
        SemanticAskQuery(prompt="피보나치 수열이 뭐야?")
    )
    assert result.destination == "gemini"
    assert result.answer == "제미나이 답변"


async def test_rag_분기는_뉴스_근거로_답변한다():
    hits = [MarketNewsHit(title="성수 상권 활황", area_tag="성수", published_at=datetime(2026, 7, 1))]
    result = await _interactor(SemanticRoute("rag", ("성수",)), hits).ask(
        SemanticAskQuery(prompt="성수동 상권 어때?")
    )
    assert result.destination == "rag"
    assert "근거 답변" in result.answer


async def test_rag_분기는_근거_없으면_답변을_거부한다():
    result = await _interactor(SemanticRoute("rag", ())).ask(
        SemanticAskQuery(prompt="어디 상권이 좋아?")
    )
    assert "찾지 못해" in result.answer


async def test_미지_분류는_rag로_폴백한다():
    result = await _interactor(SemanticRoute("unknown", ())).ask(
        SemanticAskQuery(prompt="아무 질문")
    )
    assert result.destination == "rag"


async def test_자기소개는_배역_정보를_반환한다():
    interactor = _interactor(SemanticRoute("rag", ()))
    result = await interactor.introduce_myself(
        SemanticQuery(id=10, name="시멘틱 라우터 (hub/semantic)")
    )
    assert result.id == 10
    assert result.introduction
