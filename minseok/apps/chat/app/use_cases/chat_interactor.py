import json
import logging
import re

from chat.app.dtos.chat_dto import AreaRecommendation, AreaStats, AskResponse, StockCard
from chat.app.exceptions import (
    CommercialDataUnavailableError,
    InvalidLLMResponseError,
    NoValidAreaError,
)
from chat.app.dtos.area_stat_dto import AreaStatDto
from chat.app.ports.input.chat_use_case import ChatUseCase
from chat.app.ports.output.conversation_repository import ConversationRepository
from chat.domain.entities.conversation_entity import Message
from core.llm.llm_orchestrator import EXAONE_2_4B, llm_orchestrator
from hub.app.dtos.commercial_data_dto import AreaRawStat, AreaSummary
from hub.app.dtos.recommendation_record_dto import RecommendedArea
from hub.app.dtos.stock_analysis_dto import StockAnalysisResult
from hub.app.ports.output.commercial_data_port import CommercialDataPort
from hub.app.ports.output.recommendation_record_port import RecommendationRecordPort
from hub.app.ports.output.stock_analysis_port import StockAnalysisPort, StockAnalysisUnavailable

logger = logging.getLogger(__name__)

AGE_FIELDS = [
    ("age_10_floating_pop", "10대"),
    ("age_20_floating_pop", "20대"),
    ("age_30_floating_pop", "30대"),
    ("age_40_floating_pop", "40대"),
    ("age_50_floating_pop", "50대"),
    ("age_60_plus_floating_pop", "60대 이상"),
]
TIME_FIELDS = [
    ("time_00_06_floating_pop", "새벽 0~6시"),
    ("time_06_11_floating_pop", "오전 6~11시"),
    ("time_11_14_floating_pop", "오전 11시~오후 2시"),
    ("time_14_17_floating_pop", "오후 2~5시"),
    ("time_17_21_floating_pop", "오후 5~9시"),
    ("time_21_24_floating_pop", "밤 9시~자정"),
]

INTENT_PROMPT = """사용자 질문의 의도를 분류하라.
- "stock": 회사/종목(시세·전망·분석)을 묻는 질문. 회사 이름만 언급해도 stock이다.
- "market": 동네/상권/창업/입지를 묻는 질문.

stock이면 종목을 stock_query에 추출한다. 한국 회사는 **한국어 이름 그대로** 쓰고 절대
티커를 지어내지 않는다. 해외(미국) 회사만 널리 알려진 공식 티커로 정규화한다
(예: 테슬라 → "TSLA", 애플 → "AAPL"). 티커가 확실하지 않으면 이름 그대로 둔다.

예시:
- "삼성전자 주가 어때?" → {"intent": "stock", "stock_query": "삼성전자"}
- "하이닉스 어때?" → {"intent": "stock", "stock_query": "하이닉스"}
- "엔비디아는 어때?" → {"intent": "stock", "stock_query": "NVDA"}
- "카카오 지금 사도 돼?" → {"intent": "stock", "stock_query": "카카오"}
- "성수동은 어때?" → {"intent": "market", "stock_query": ""}
- "홍대에 카페 차릴만해?" → {"intent": "market", "stock_query": ""}

반드시 아래 JSON 형식으로만 응답하라 (마크다운 코드블록 없이):
{"intent": "market", "stock_query": ""}"""

STOCK_ANSWER_PROMPT = """당신은 주식 분석 상담사입니다.
제공된 지표·감성 수치만 근거로 종목의 현재 상황을 한국어 4~6문장으로 설명하세요.

규칙:
- 수치는 제공된 그대로 인용하고, RSI·이동평균·지지선/저항선의 의미를 해석해 서술
- 매수/매도 지시 금지, 상승/하락 확률 단정 금지 — 방향 전망은 참고 신호로만 표현
- 마지막에 투자 판단은 본인 책임이라는 고지 한 문장을 포함"""

PHASE1_PROMPT = """당신은 서울 상권 분석 전문가입니다.
사용자 질문을 보고 다음을 결정하세요:
1. 가장 적합한 service_code (업종 코드)
2. 추천할 상권 trdar_code 3~5개

반드시 아래 JSON 형식으로만 응답하세요 (마크다운 코드블록 없이):
{"service_code": "CS100010", "service_name": "커피-음료", "trdar_codes": [3120103, 3120104, 3110544]}

규칙:
- service_code는 반드시 제공된 목록에서 선택
- trdar_code는 반드시 상권 데이터에 있는 값 사용
- 상권 전체 월매출 규모와 위치(자치구, 행정동)를 기준으로 사용자 질문에 맞는 곳 선택"""

PHASE2_PROMPT = """당신은 서울 창업 컨설턴트입니다.
제공된 각 상권의 공공데이터 수치를 기반으로 창업자에게 유용한 설명을 작성하세요.

반드시 아래 JSON 형식으로만 응답하세요 (마크다운 코드블록 없이):
{
  "text": "전체 추천 요약 (2~3문장, 데이터 근거 포함)",
  "areas": [
    {
      "trdar_code": 1000001,
      "reason": "이 상권을 추천하는 이유 (3~4문장, 반드시 제공된 수치 인용, 창업자 관점)"
    }
  ]
}

규칙:
- text와 reason 모두 자연스러운 한국어로 작성
- reason에서 수치를 인용할 때는 실제 제공된 숫자 그대로 사용
- 창업자가 실질적으로 도움받을 수 있는 인사이트 포함 (경쟁 강도, 수익성, 안정성 등)
- 수치를 단순 나열하지 말고 의미를 해석해서 서술"""

STREAM_SYSTEM_PROMPT = """당신은 서울 상권 분석 상담사입니다.
사용자와 자연스럽게 대화하며 상권 선택·창업 관련 조언을 제공합니다.
이전 대화 맥락을 이어받아 답하고, 확실치 않은 수치는 단정하지 말고 솔직히 안내합니다.
구체적인 상권 추천이 필요하면 사용자가 지역과 업종을 말하도록 유도합니다."""


def _top_field(obj, fields: list[tuple[str, str]]) -> str:
    best = max(fields, key=lambda f: getattr(obj, f[0], 0) or 0)
    return best[1]


def _parse_llm_json(raw: str) -> dict:
    raw = raw.strip()
    # 마크다운 코드펜스 제거
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    text = match.group() if match else raw
    # 후행 콤마 제거(소형 모델 빈발 오류)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


class ChatInteractor(ChatUseCase):

    def __init__(
        self,
        market: CommercialDataPort,
        recorder: RecommendationRecordPort,
        conversations: ConversationRepository,
        stocks: StockAnalysisPort,
    ) -> None:
        self._market = market
        self._recorder = recorder
        self._conversations = conversations
        self._stocks = stocks

    def _history_block(self, history: list[Message]) -> str:
        if not history:
            return ""
        turns = "\n".join(f"{m.role}: {m.content[:200]}" for m in history[-6:])
        return f"이전 대화(맥락 참고용):\n{turns}\n\n"

    def _build_area_context(
        self, summary: AreaSummary, prompt: str = "", limit: int = 80
    ) -> str:
        # 상권 1650개 전체를 넣으면 경량 모델(2.4B) 컨텍스트를 초과한다.
        # 질문에 언급된 자치구를 우선 포함하고, 나머지는 월매출 상위로 상한까지 채운다.
        def sales_of(a) -> int:
            return summary.sales_by_code.get(a.trdar_code) or 0

        def mentioned(a) -> bool:
            d = a.district_name
            if not d:
                return False
            stripped = d[:-1] if d.endswith("구") else d
            return d in prompt or (len(stripped) >= 2 and stripped in prompt)

        ranked = sorted(summary.areas, key=sales_of, reverse=True)
        picked = [a for a in ranked if mentioned(a)][:limit]
        seen = {a.trdar_code for a in picked}
        for a in ranked:
            if len(picked) >= limit:
                break
            if a.trdar_code not in seen:
                picked.append(a)
                seen.add(a.trdar_code)

        lines = ["상권코드|상권명|자치구|행정동|상권전체월매출합계(만원)"]
        for a in picked:
            sales = summary.sales_by_code.get(a.trdar_code)
            wan = round(sales / 10000) if sales else None
            lines.append(
                f"{a.trdar_code}|{a.trdar_name}|{a.district_name}|{a.adm_dong_name}"
                f"|{wan if wan is not None else '데이터없음'}"
            )
        return "\n".join(lines)

    def _format_stats(
        self, raw_stats: dict[int, AreaRawStat], quarter: int,
    ) -> dict[int, AreaStatDto]:
        quarter_label = f"{str(quarter)[:4]}년 {str(quarter)[4]}분기"

        result: dict[int, AreaStatDto] = {}
        for code, raw in raw_stats.items():
            has_data = raw.has_sales or raw.has_store or raw.has_fp

            if raw.has_sales and raw.has_store and raw.store_count and raw.store_count > 0:
                sales_wan = round(raw.monthly_sales_amount / 10000)
                per_store_wan = round(sales_wan / raw.store_count)
                revenue_text = f"점포당 월평균 {per_store_wan:,}만원"
                revenue_source = f"업종 월 총매출 {sales_wan / 10000:.1f}억원 ÷ {raw.store_count}개 점포로 계산"
            elif raw.has_sales:
                sales_wan = round(raw.monthly_sales_amount / 10000)
                revenue_text = f"업종 월 총매출 {sales_wan:,}만원 (점포수 미집계)"
                revenue_source = "점포당 매출 계산 불가 (점포수 데이터 없음)"
            else:
                revenue_text = "매출 데이터 없음"
                revenue_source = "해당 분기 데이터 미수집"

            weekday_text = "데이터 없음"
            if raw.has_sales and raw.monthly_sales_amount and raw.weekday_sales_amount:
                wd = round(raw.weekday_sales_amount / raw.monthly_sales_amount * 100)
                weekday_text = f"주중 {wd}% / 주말 {100 - wd}%"

            store_count_text = f"{raw.store_count}개 점포 영업 중" if raw.has_store else "점포 데이터 없음"
            closure_text = f"분기 폐업률 {raw.closure_rate}%" if raw.has_store else "데이터 없음"
            opening_text = f"분기 개업률 {raw.opening_rate}%" if raw.has_store else "데이터 없음"

            if raw.has_store and raw.store_count and raw.store_count > 0:
                fr = round(raw.franchise_store_count / raw.store_count * 100)
                franchise_text = f"프랜차이즈 {raw.franchise_store_count}개 ({fr}%)"
            else:
                franchise_text = "데이터 없음"

            if raw.has_fp:
                daily = round(raw.total_floating_pop / 91)
                foot_text = f"일평균 {daily:,}명 (분기 총 {raw.total_floating_pop:,}명 ÷ 91일)"
                top_age = _top_field(raw, AGE_FIELDS)
                peak_time = _top_field(raw, TIME_FIELDS)
            else:
                foot_text = "유동인구 데이터 없음"
                top_age = "데이터 없음"
                peak_time = "데이터 없음"

            if raw.has_cc:
                change_text = raw.change_indicator_name or "데이터 없음"
                op_months = raw.operating_months_avg
                seoul_op = raw.seoul_operating_months_avg
                op_text = (
                    f"이 상권 평균 {op_months}개월 영업 (서울 평균 {seoul_op}개월)"
                    if op_months else "데이터 없음"
                )
            else:
                change_text = "데이터 없음"
                op_text = "데이터 없음"

            result[code] = {
                "revenue_text": revenue_text,
                "revenue_source": revenue_source,
                "weekday_text": weekday_text,
                "store_count_text": store_count_text,
                "closure_text": closure_text,
                "opening_text": opening_text,
                "franchise_text": franchise_text,
                "foot_text": foot_text,
                "top_age": top_age,
                "peak_time": peak_time,
                "change_text": change_text,
                "op_months_text": op_text,
                "quarter_label": quarter_label,
                "has_data": has_data,
            }

        return result

    async def ask(self, prompt: str, conversation_id: int | None = None) -> AskResponse:
        if conversation_id is None:
            conversation_id = (await self._conversations.create_conversation()).id
        history = await self._conversations.get_messages(conversation_id)
        await self._conversations.add_message(conversation_id, "user", prompt)

        # phase0(의도 분류 = 도메인 판단) → 도메인 경량 모델(2.4B)로 내려 씀
        intent, stock_query = await self._classify_intent(prompt, history)
        if intent == "stock":
            return await self._answer_stock(conversation_id, prompt, stock_query)

        summary = await self._market.get_area_summary()
        quarter = summary.latest_quarter
        if not quarter:
            raise CommercialDataUnavailableError("상권 데이터가 없습니다.")

        area_map = {a.trdar_code: a for a in summary.areas}
        area_context = self._build_area_context(summary, prompt)

        service_codes = await self._market.get_service_codes()
        service_code_list = "\n".join(f"{sc.code}|{sc.name}" for sc in service_codes)

        phase1_contents = (
            f"{self._history_block(history)}"
            f"사용자 질문: {prompt}\n\n"
            f"업종 코드 목록:\n{service_code_list}\n\n"
            f"서울 상권 데이터:\n{area_context}"
        )
        # phase1(상권/업종 선택 = 도메인 판단) → 도메인 경량 모델(2.4B)로 내려 씀
        p1_raw = await llm_orchestrator.orchestrate(
            f"{PHASE1_PROMPT}\n\n{phase1_contents}", model=EXAONE_2_4B, format="json",
        )

        try:
            p1 = _parse_llm_json(p1_raw)
        except Exception:
            logger.error("[chat] Phase1 파싱 실패: %s", p1_raw[:200])
            raise InvalidLLMResponseError("AI 응답 파싱 실패")

        service_code: str = p1.get("service_code", "")
        service_name: str = p1.get("service_name", "")
        trdar_codes: list[int] = [int(c) for c in p1.get("trdar_codes", []) if str(c).isdigit()]
        valid_codes = [c for c in trdar_codes if c in area_map]
        if not valid_codes:
            raise NoValidAreaError("유효한 상권을 찾지 못했습니다.")

        raw_stats = await self._market.get_area_raw_stats(valid_codes, service_code, quarter)
        real_stats = self._format_stats(raw_stats, quarter)

        quarter_label = f"{str(quarter)[:4]}년 {str(quarter)[4]}분기"
        stats_context_lines = [f"사용자 질문: {prompt}\n업종: {service_name}\n기준: {quarter_label}\n"]
        for code in valid_codes:
            area = area_map[code]
            st = real_stats.get(code, {})
            stats_context_lines.append(
                f"[{area.trdar_name} / {area.district_name}] (trdar_code: {code})\n"
                f"- 수익: {st.get('revenue_text')} | {st.get('revenue_source')}\n"
                f"- 매출패턴: {st.get('weekday_text')}\n"
                f"- 점포: {st.get('store_count_text')} | {st.get('closure_text')} | {st.get('opening_text')} | {st.get('franchise_text')}\n"
                f"- 유동인구: {st.get('foot_text')}\n"
                f"- 주요 연령대: {st.get('top_age')} | 피크시간: {st.get('peak_time')}\n"
                f"- 상권변화: {st.get('change_text')} | {st.get('op_months_text')}\n"
            )

        # phase2(최종 서술 = 최종 사용자 답변) → 오케스트레이터 기본 모델(7.8B)
        p2_raw = await llm_orchestrator.orchestrate(
            f"{PHASE2_PROMPT}\n\n" + "\n".join(stats_context_lines), format="json",
        )

        try:
            p2 = _parse_llm_json(p2_raw)
        except Exception:
            logger.error("[chat] Phase2 파싱 실패: %s", p2_raw[:200])
            raise InvalidLLMResponseError("AI 서술 생성 실패")

        reason_map = {item["trdar_code"]: item["reason"] for item in p2.get("areas", [])}

        recommendations: list[AreaRecommendation] = []
        for code in valid_codes:
            area = area_map[code]
            st = real_stats.get(code, {})
            recommendations.append(AreaRecommendation(
                id=str(code),
                name=area.trdar_name,
                lat=area.lat,
                lng=area.lng,
                category=service_name,
                reason=reason_map.get(code, ""),
                stats=AreaStats(
                    monthlyRevenueText=st.get("revenue_text", ""),
                    revenueSourceText=st.get("revenue_source", ""),
                    weekdayText=st.get("weekday_text", ""),
                    storeCountText=st.get("store_count_text", ""),
                    closureRateText=st.get("closure_text", ""),
                    openingRateText=st.get("opening_text", ""),
                    franchiseText=st.get("franchise_text", ""),
                    footTrafficText=st.get("foot_text", ""),
                    topAgeText=st.get("top_age", ""),
                    peakTimeText=st.get("peak_time", ""),
                    changeText=st.get("change_text", ""),
                    operatingMonthsText=st.get("op_months_text", ""),
                    dataSource=f"서울시 공공데이터 {quarter_label} 기준",
                    hasRealData=st.get("has_data", False),
                ),
            ))

        text = p2.get("text", "")
        await self._conversations.add_message(conversation_id, "assistant", text)

        # 기록 경로: chat → 허브 포트 → recommendation (스포크끼리 직접 잇지 않음)
        await self._recorder.record(
            conversation_id,
            [
                RecommendedArea(
                    trdar_code=code,
                    trdar_name=area_map[code].trdar_name,
                    district_name=area_map[code].district_name,
                    category=service_name,
                    reason=reason_map.get(code, ""),
                    lat=area_map[code].lat,
                    lng=area_map[code].lng,
                )
                for code in valid_codes
            ],
        )

        return AskResponse(
            text=text, recommendations=recommendations, conversationId=conversation_id,
        )

    async def _classify_intent(self, prompt: str, history: list[Message]) -> tuple[str, str]:
        raw = await llm_orchestrator.orchestrate(
            f"{INTENT_PROMPT}\n\n{self._history_block(history)}사용자 질문: {prompt}",
            model=EXAONE_2_4B, format="json",
        )
        try:
            parsed = _parse_llm_json(raw)
        except Exception:
            logger.warning("[chat] 의도 분류 파싱 실패 → market 폴백: %s", raw[:100])
            return "market", ""
        stock_query = str(parsed.get("stock_query") or "").strip()
        if parsed.get("intent") == "stock" and stock_query:
            return "stock", stock_query
        return "market", ""

    async def _answer_stock(
        self, conversation_id: int, prompt: str, stock_query: str
    ) -> AskResponse:
        try:
            analysis = await self._stocks.analyze(stock_query)
        except StockAnalysisUnavailable as e:
            text = f"{e.detail} 정확한 종목명이나 티커로 다시 물어봐 주세요."
            await self._conversations.add_message(conversation_id, "assistant", text)
            return AskResponse(text=text, recommendations=[], conversationId=conversation_id)

        context = self._format_stock_context(prompt, analysis)
        # 최종 서술(최종 사용자 답변) → 오케스트레이터 기본 모델(7.8B)
        text = await llm_orchestrator.orchestrate(f"{STOCK_ANSWER_PROMPT}\n\n{context}")
        await self._conversations.add_message(conversation_id, "assistant", text)
        card = StockCard(
            symbol=analysis.symbol,
            price=analysis.price,
            direction=analysis.direction,
            confidence=analysis.confidence,
            rsi=analysis.rsi,
            ma20=analysis.ma20,
            ma50=analysis.ma50,
            support=analysis.support,
            resistance=analysis.resistance,
            sentimentLabel=analysis.sentiment_label,
            headlines=analysis.headlines,
        )
        return AskResponse(
            text=text, recommendations=[], conversationId=conversation_id, stock=card,
        )

    @staticmethod
    def _format_stock_context(prompt: str, r: StockAnalysisResult) -> str:
        headlines = "\n".join(f"- {h}" for h in r.headlines) if r.headlines else "- (없음)"
        return (
            f"사용자 질문: {prompt}\n\n"
            f"[{r.symbol} 분석 데이터]\n"
            f"- 현재가: {r.price:,.2f}\n"
            f"- 방향 신호: {r.direction} (확신도 {r.confidence:.2f})\n"
            f"- RSI(14): {r.rsi:.1f} (30↓ 과매도 / 70↑ 과매수)\n"
            f"- 20일 이동평균: {r.ma20:,.2f} / 50일 이동평균: {r.ma50:,.2f}\n"
            f"- 지지선: {r.support:,.2f} / 저항선: {r.resistance:,.2f} (최근 60거래일 저/고점)\n"
            f"- 뉴스 감성: {r.sentiment:+.2f} ({r.sentiment_label})\n"
            f"- 최근 헤드라인:\n{headlines}"
        )

    async def stream_reply(self, prompt: str, conversation_id: int | None = None):
        if conversation_id is None:
            conversation_id = (await self._conversations.create_conversation()).id
        yield {"type": "meta", "conversationId": conversation_id}

        history = await self._conversations.get_messages(conversation_id)
        await self._conversations.add_message(conversation_id, "user", prompt)
        hist_msgs = [{"role": m.role, "content": m.content} for m in history[-8:]]

        parts: list[str] = []
        # 대화 스트리밍(최종 사용자 답변) → 오케스트레이터 기본 모델(7.8B)
        async for chunk in llm_orchestrator.orchestrate_stream(
            prompt, system=STREAM_SYSTEM_PROMPT, history=hist_msgs,
        ):
            parts.append(chunk)
            yield {"type": "delta", "text": chunk}

        await self._conversations.add_message(conversation_id, "assistant", "".join(parts))
        yield {"type": "done"}
