"""ChatInteractor 테스트 — 스텁 포트 + 모듈 네임스페이스 LLM 교체.

llm_orchestrator는 전역 싱글턴이지만 chat_interactor가 모듈 전역 이름으로 바인딩하므로
monkeypatch로 모듈 네임스페이스의 이름만 갈아끼운다(다른 모듈 무영향, teardown 자동).
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from chat.app.exceptions import ConversationNotFoundError
from chat.app.use_cases.chat_interactor import ChatInteractor
from chat.domain.entities.conversation_entity import Conversation, Message
from hub.app.dtos.commercial_data_dto import AreaInfo, AreaRawStat, AreaSummary, ServiceCode
from hub.app.dtos.news_dto import NewsHit
from hub.app.dtos.stock_analysis_dto import StockAnalysisResult
from hub.app.ports.output.stock_analysis_port import StockAnalysisUnavailable

_NOW = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)

INTENT_STOCK = '{"intent": "stock", "stock_query": "삼성전자"}'
INTENT_STOCK_NO_QUERY = '{"intent": "stock", "stock_query": ""}'
INTENT_MARKET_NEWS = '{"intent": "market_news", "stock_query": ""}'
INTENT_MARKET = '{"intent": "market", "stock_query": ""}'
PHASE1_JSON = '{"service_code": "CS100010", "service_name": "커피-음료", "trdar_codes": [1000001]}'
PHASE2_JSON = '{"text": "상권 요약", "areas": [{"trdar_code": 1000001, "reason": "추천 이유"}]}'


class _StubLLM:
    def __init__(self, responses: list[str]):
        self.calls: list[tuple[str, dict]] = []
        self._responses = list(responses)

    async def orchestrate(self, prompt: str, **kwargs) -> str:
        self.calls.append((prompt, kwargs))
        return self._responses.pop(0)


class _StubConversations:
    def __init__(self, history: list[Message] | None = None,
                 conversation: Conversation | None = None):
        self._history = history or []
        self._conversation = conversation
        self.saved: list[tuple[str, str]] = []
        self.payloads: list[dict | None] = []
        self.created_user_ids: list[int | None] = []
        self._next_id = 100

    async def create_conversation(self, user_id: int | None = None) -> Conversation:
        self._next_id += 1
        self.created_user_ids.append(user_id)
        return Conversation(id=self._next_id, created_at=_NOW, user_id=user_id)

    async def add_message(self, conversation_id: int, role: str, content: str,
                          payload: dict | None = None) -> Message:
        self.saved.append((role, content))
        self.payloads.append(payload)
        return Message(id=len(self.saved), conversation_id=conversation_id,
                       role=role, content=content, created_at=_NOW, payload=payload)

    async def get_messages(self, conversation_id: int, limit: int = 20) -> list[Message]:
        return self._history

    async def get_conversation(self, conversation_id: int) -> Conversation | None:
        return self._conversation

    async def list_conversations(self, user_id: int, limit: int = 30):
        return []


class _StubStocks:
    def __init__(self, result: StockAnalysisResult | None = None, fail: bool = False):
        self.result = result
        self.fail = fail
        self.queries: list[str] = []

    async def analyze(self, query: str) -> StockAnalysisResult:
        self.queries.append(query)
        if self.fail:
            raise StockAnalysisUnavailable("종목을 찾지 못했습니다: X.")
        return self.result


class _StubNewsSearch:
    def __init__(self, hits: list[NewsHit] | None = None):
        self.hits = hits or []
        self.calls: list[tuple[str, str | None, int]] = []

    async def search(self, query: str, ticker: str | None = None, limit: int = 5) -> list[NewsHit]:
        self.calls.append((query, ticker, limit))
        return self.hits


class _StubMarket:
    def __init__(self):
        self.summary_calls = 0

    async def get_area_summary(self) -> AreaSummary:
        self.summary_calls += 1
        area = AreaInfo(trdar_code=1000001, trdar_name="테스트상권", district_name="강남구",
                        adm_dong_name="역삼동", lat=37.5, lng=127.0)
        return AreaSummary(areas=[area], latest_quarter=20254, sales_by_code={1000001: 100_000_000})

    async def get_service_codes(self) -> list[ServiceCode]:
        return [ServiceCode(code="CS100010", name="커피-음료")]

    async def get_area_raw_stats(self, codes, service_code, quarter):
        return {c: _raw_stat() for c in codes}


class _StubRecorder:
    def __init__(self):
        self.recorded: list = []

    async def record(self, conversation_id: int, areas) -> None:
        self.recorded.append((conversation_id, areas))


def _raw_stat() -> AreaRawStat:
    return AreaRawStat(
        has_sales=False, monthly_sales_amount=None, weekday_sales_amount=None,
        has_store=False, store_count=None, closure_rate=None, opening_rate=None,
        franchise_store_count=None,
        has_fp=False, total_floating_pop=None,
        age_10_floating_pop=None, age_20_floating_pop=None, age_30_floating_pop=None,
        age_40_floating_pop=None, age_50_floating_pop=None, age_60_plus_floating_pop=None,
        time_00_06_floating_pop=None, time_06_11_floating_pop=None, time_11_14_floating_pop=None,
        time_14_17_floating_pop=None, time_17_21_floating_pop=None, time_21_24_floating_pop=None,
        has_cc=False, change_indicator_name=None, operating_months_avg=None,
        region_operating_months_avg=None,
    )


def _analysis(**overrides) -> StockAnalysisResult:
    base = dict(
        symbol="005930", price=90000.0, direction="NEUTRAL", confidence=0.1,
        sentiment=0.4, sentiment_label="긍정", rsi=45.0, ma20=88000.0, ma50=85000.0,
        support=80000.0, resistance=95000.0, headlines=["삼성전자 실적 발표"],
        atr_pct=0.025, bb_percent_b=0.15, volume_ratio=1.8, obv_slope=0.5,
        momentum_12_1=0.22, reference_up_signal=True,
    )
    return StockAnalysisResult(**{**base, **overrides})


def _hit(**overrides) -> NewsHit:
    base = dict(title="반도체 업황 회복 조짐", ticker="005930.KS",
                published_at=_NOW, sentiment=0.7, event_type="실적", source="테스트")
    return NewsHit(**{**base, **overrides})


def _build(monkeypatch, llm_responses, *, stocks=None, news=None, conversations=None):
    llm = _StubLLM(llm_responses)
    monkeypatch.setattr("chat.app.use_cases.chat_interactor.llm_orchestrator", llm)
    market, recorder = _StubMarket(), _StubRecorder()
    conversations = conversations or _StubConversations()
    stocks = stocks or _StubStocks(result=_analysis())
    news = news or _StubNewsSearch()
    interactor = ChatInteractor(
        market=market, recorder=recorder, conversations=conversations,
        stocks=stocks, news=news,
    )
    return interactor, llm, dict(market=market, recorder=recorder,
                                 conversations=conversations, stocks=stocks, news=news)


# --- phase0 3분류 라우팅 ---

async def test_stock_의도면_분석_포트를_호출하고_카드를_반환한다(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, [INTENT_STOCK, "주식 서술"])
    result = await interactor.ask("삼성전자 어때?")
    assert stubs["stocks"].queries == ["삼성전자"]
    assert result.stock is not None and result.stock.symbol == "005930"
    assert result.text == "주식 서술"


async def test_market_news_의도면_뉴스_검색을_코퍼스_횡단으로_호출한다(monkeypatch):
    news = _StubNewsSearch(hits=[_hit()])
    interactor, _, _ = _build(monkeypatch, [INTENT_MARKET_NEWS, "업황 서술"], news=news)
    result = await interactor.ask("반도체 업황 어때?")
    assert news.calls == [("반도체 업황 어때?", None, 8)]
    assert result.text == "업황 서술" and result.recommendations == []


async def test_market_의도면_기존_상권_경로가_그대로_동작한다(monkeypatch):  # 무손상 회귀
    interactor, _, stubs = _build(monkeypatch, [INTENT_MARKET, PHASE1_JSON, PHASE2_JSON])
    result = await interactor.ask("성수동 카페 어때?")
    assert stubs["market"].summary_calls == 1
    assert len(result.recommendations) == 1
    assert result.recommendations[0].name == "테스트상권"
    assert len(stubs["recorder"].recorded) == 1


async def test_의도_파싱_실패면_market_폴백(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, ["JSON 아님", PHASE1_JSON, PHASE2_JSON])
    result = await interactor.ask("아무 질문")
    assert stubs["market"].summary_calls == 1
    assert len(result.recommendations) == 1


async def test_stock인데_종목_추출_실패면_market_news_폴백(monkeypatch):
    news = _StubNewsSearch()
    interactor, _, _ = _build(monkeypatch, [INTENT_STOCK_NO_QUERY, "서술"], news=news)
    await interactor.ask("그 회사 어때?")
    assert len(news.calls) == 1  # 상권이 아니라 뉴스 RAG로


# --- 지표 근거 주입 ---

async def test_주식_컨텍스트에_신규_지표_해석과_참고_신호가_들어간다(monkeypatch):
    interactor, llm, _ = _build(monkeypatch, [INTENT_STOCK, "서술"])
    await interactor.ask("삼성전자 어때?")
    stock_prompt = llm.calls[1][0]  # [0]=의도 분류, [1]=7.8B 서술
    assert "%B 0.15" in stock_prompt and "ATR(14)" in stock_prompt
    assert "거래량" in stock_prompt and "12-1 모멘텀 +22.0%" in stock_prompt
    assert "과매도+볼린저 하단" in stock_prompt  # 참고 신호 라인 (True일 때만)


async def test_참고_신호_false면_문구_자체가_없다(monkeypatch):  # 소형 모델 오독 차단
    stocks = _StubStocks(result=_analysis(reference_up_signal=False))
    interactor, llm, _ = _build(monkeypatch, [INTENT_STOCK, "서술"], stocks=stocks)
    await interactor.ask("삼성전자 어때?")
    # 규칙 문구(STOCK_ANSWER_PROMPT)가 아니라 컨텍스트의 신호 라인이 없어야 한다
    assert "과매도+볼린저 하단" not in llm.calls[1][0]


async def test_stock_카드에_신규_6필드가_매핑된다(monkeypatch):
    interactor, _, _ = _build(monkeypatch, [INTENT_STOCK, "서술"])
    result = await interactor.ask("삼성전자 어때?")
    card = result.stock
    assert card.atrPct == 0.025 and card.bbPercentB == 0.15
    assert card.volumeRatio == 1.8 and card.obvSlope == 0.5
    assert card.momentum12To1 == 0.22 and card.referenceUpSignal is True


# --- 뉴스 RAG ---

async def test_주식_답변에_관련_뉴스_섹션이_라벨과_함께_붙는다(monkeypatch):
    news = _StubNewsSearch(hits=[_hit(title="새 소식")])
    interactor, llm, _ = _build(monkeypatch, [INTENT_STOCK, "서술"], news=news)
    await interactor.ask("삼성전자 어때?")
    assert news.calls[0][1] == "005930"  # 해석된 심볼로 범위 제한
    stock_prompt = llm.calls[1][0]
    assert "관련 뉴스(감성 라벨)" in stock_prompt and "호재" in stock_prompt


async def test_뉴스_히트가_없으면_관련_뉴스_섹션이_생략된다(monkeypatch):  # 무손상
    interactor, llm, _ = _build(monkeypatch, [INTENT_STOCK, "서술"])
    await interactor.ask("삼성전자 어때?")
    assert "관련 뉴스(감성 라벨)" not in llm.calls[1][0]


async def test_market_news_히트가_없으면_데이터_부재를_안내한다(monkeypatch):
    interactor, llm, _ = _build(monkeypatch, [INTENT_MARKET_NEWS, "열화 서술"])
    await interactor.ask("업황 어때?")
    assert "수집된 관련 뉴스가 없습니다" in llm.calls[1][0]


async def test_종목_해석_실패면_안내문을_저장하고_반환한다(monkeypatch):
    stocks = _StubStocks(fail=True)
    interactor, _, stubs = _build(monkeypatch, [INTENT_STOCK], stocks=stocks)
    result = await interactor.ask("이상한종목 어때?")
    assert "다시 물어봐" in result.text
    assert stubs["conversations"].saved[-1][0] == "assistant"


# --- phase1 상권 컨텍스트: 질문 지역 우선 ---

def _summary_two_areas() -> AreaSummary:
    seongsu = AreaInfo(trdar_code=1, trdar_name="성수역", district_name="성동구",
                       adm_dong_name="성수1가1동", lat=37.5, lng=127.0)
    noryang = AreaInfo(trdar_code=2, trdar_name="노량진역(노량진)", district_name="동작구",
                       adm_dong_name="노량진1동", lat=37.5, lng=126.9)
    # 매출은 노량진이 압도적 — 언급 매칭 없으면 노량진이 첫 행이어야 한다
    return AreaSummary(areas=[seongsu, noryang], latest_quarter=20254,
                       sales_by_code={1: 10_000_000, 2: 999_000_000})


async def test_행정동_언급_상권이_매출과_무관하게_컨텍스트_최상단_별표(monkeypatch):
    interactor, _, _ = _build(monkeypatch, [])
    context = interactor._build_area_context(_summary_two_areas(), "성수동에 카페 차릴만해?")
    rows = context.splitlines()[1:]
    assert rows[0].startswith("1|성수역") and rows[0].endswith("★")  # 성수1가1동 → 어간 '성수' 매칭
    assert rows[1].startswith("2|") and rows[1].endswith("|")  # 노량진은 표시 없음


async def test_지역_언급_없으면_매출순_유지(monkeypatch):
    interactor, _, _ = _build(monkeypatch, [])
    context = interactor._build_area_context(_summary_two_areas(), "카페 차릴만한 곳 추천해줘")
    rows = context.splitlines()[1:]
    assert rows[0].startswith("2|")  # 매출 상위 노량진 먼저
    assert not any(r.endswith("★") for r in rows)


async def test_자치구_언급도_계속_매칭된다(monkeypatch):  # 기존 동작 보존
    interactor, _, _ = _build(monkeypatch, [])
    context = interactor._build_area_context(_summary_two_areas(), "성동구 쪽 어때?")
    assert context.splitlines()[1].startswith("1|성수역")


async def test_지역_언급_시_LLM이_다른_상권을_골라도_언급_지역으로_보정된다(monkeypatch):
    # phase1(2.4B 스텁)이 노량진(code 2)을 고르지만, 질문은 성수동 — 가드가 성수(code 1)로 교체
    phase1_wrong = '{"service_code": "CS100010", "service_name": "커피-음료", "trdar_codes": [2]}'
    phase2 = '{"text": "요약", "areas": [{"trdar_code": 1, "reason": "이유"}]}'
    interactor, _, stubs = _build(monkeypatch, [INTENT_MARKET, phase1_wrong, phase2])
    stubs["market"].summary = _summary_two_areas()

    async def _fixed_summary():
        return _summary_two_areas()
    stubs["market"].get_area_summary = _fixed_summary

    result = await interactor.ask("성수동에 카페 차릴만해?")
    assert [a.id for a in result.recommendations] == ["1"]  # 성수역만


# --- 멀티턴 시나리오 (E2E 시나리오 3종 — 인터랙터 레벨) ---

async def test_시나리오_주식_업황_상권_연속_질문(monkeypatch):
    conversations = _StubConversations(history=[
        Message(id=1, conversation_id=200, role="user", content="삼성전자 어때?", created_at=_NOW),
        Message(id=2, conversation_id=200, role="assistant", content="주식 서술", created_at=_NOW),
    ])
    news = _StubNewsSearch(hits=[_hit()])
    interactor, llm, stubs = _build(
        monkeypatch,
        [INTENT_MARKET_NEWS, "업황 서술", INTENT_MARKET, PHASE1_JSON, PHASE2_JSON],
        news=news, conversations=conversations,
    )
    r1 = await interactor.ask("그럼 업황은 어때?", conversation_id=200)
    assert "이전 대화" in llm.calls[0][0] and "삼성전자 어때?" in llm.calls[0][0]  # history 전달
    r2 = await interactor.ask("성수동 상권도 알려줘", conversation_id=200)
    assert r1.conversationId == r2.conversationId == 200
    roles = [role for role, _ in stubs["conversations"].saved]
    assert roles == ["user", "assistant", "user", "assistant"]


# --- 대화 히스토리 (payload 저장 + 목록/복원) ---

async def test_새_대화는_user_id를_소유자로_기록한다(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, [INTENT_STOCK, "서술"])
    await interactor.ask("삼성전자 어때?", user_id=7)
    assert stubs["conversations"].created_user_ids == [7]


async def test_주식_답변은_stock_카드를_payload로_저장한다(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, [INTENT_STOCK, "서술"])
    await interactor.ask("삼성전자 어때?")
    assistant_payload = stubs["conversations"].payloads[-1]
    assert assistant_payload is not None
    assert assistant_payload["stock"]["symbol"] == "005930"


async def test_상권_답변은_recommendations를_payload로_저장한다(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, [INTENT_MARKET, PHASE1_JSON, PHASE2_JSON])
    await interactor.ask("성수동 카페 어때?")
    assistant_payload = stubs["conversations"].payloads[-1]
    assert assistant_payload is not None
    assert assistant_payload["recommendations"][0]["name"] == "테스트상권"


async def test_텍스트만인_답변은_payload가_없다(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, [INTENT_MARKET_NEWS, "업황 서술"])
    await interactor.ask("업황 어때?")
    assert stubs["conversations"].payloads[-1] is None


async def test_market_news_답변은_뉴스_카드를_응답과_payload에_동반한다(monkeypatch):
    news = _StubNewsSearch(hits=[_hit()])
    interactor, _, stubs = _build(
        monkeypatch, [INTENT_MARKET_NEWS, "업황 서술"], news=news,
    )
    result = await interactor.ask("반도체 업황 어때?")

    assert len(result.news) == 1
    card = result.news[0]
    assert card.title == "반도체 업황 회복 조짐"
    assert card.ticker == "005930.KS"
    assert card.publishedAt == f"{_NOW:%Y-%m-%d}"
    assert card.sentiment == 0.7 and card.eventType == "실적"

    assistant_payload = stubs["conversations"].payloads[-1]
    assert assistant_payload is not None
    assert assistant_payload["news"][0]["title"] == "반도체 업황 회복 조짐"


async def test_market_news_히트가_없으면_뉴스_카드도_비어있다(monkeypatch):
    interactor, _, stubs = _build(monkeypatch, [INTENT_MARKET_NEWS, "부재 안내"])
    result = await interactor.ask("업황 어때?")
    assert result.news == []
    assert stubs["conversations"].payloads[-1] is None


async def test_남의_대화_메시지는_미존재와_같은_예외를_낸다(monkeypatch):
    conversations = _StubConversations(
        conversation=Conversation(id=200, created_at=_NOW, user_id=1),
    )
    interactor, _, _ = _build(monkeypatch, [], conversations=conversations)
    with pytest.raises(ConversationNotFoundError):
        await interactor.conversation_messages(200, user_id=2)


async def test_소유자는_메시지를_payload_포함으로_받는다(monkeypatch):
    history = [Message(id=1, conversation_id=200, role="assistant", content="답",
                       created_at=_NOW, payload={"stock": {"symbol": "005930"}})]
    conversations = _StubConversations(
        history=history,
        conversation=Conversation(id=200, created_at=_NOW, user_id=1),
    )
    interactor, _, _ = _build(monkeypatch, [], conversations=conversations)
    messages = await interactor.conversation_messages(200, user_id=1)
    assert messages[0].payload == {"stock": {"symbol": "005930"}}


async def test_구버전_익명_대화는_인증_사용자에게_허용된다(monkeypatch):
    conversations = _StubConversations(
        conversation=Conversation(id=200, created_at=_NOW, user_id=None),
    )
    interactor, _, _ = _build(monkeypatch, [], conversations=conversations)
    assert await interactor.conversation_messages(200, user_id=1) == []