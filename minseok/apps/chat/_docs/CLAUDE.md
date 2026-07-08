# CLAUDE.md — chat 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

**대화형 분석 어시스턴트**(ChatGPT·Gemini·Claude 형). 사용자와 멀티턴으로 소통하며
상권 데이터에 근거한 창업/입지 추천과 주식 분석(허브 경유)을 답한다.

---

## 데이터 접근 — 허브 포트만 사용

chat은 다른 스포크를 **직접 import하지 않는다**. 허브 `hub`가 공개한 포트
(→ hub CLAUDE)만 의존하고, 구현은 각 스포크가 제공,
`main.py`가 주입한다(스타 토폴로지).

| 포트 | 구현 스포크 | 용도 |
|------|------------|------|
| `CommercialDataPort` | market (`CommercialDataGateway`) | 상권 데이터 조회 |
| `RecommendationRecordPort` | recommendation (`RecommendationRecordGateway`) | 추천 기록 |
| `StockAnalysisPort` | stock (`StockAnalysisGateway`) | 주식 분석 |

## 의도 라우팅 — phase0

`ask()`는 먼저 경량 모델(2.4B)로 질문 의도를 분류한다: 주식 질문(`stock`)이면 종목 질의를
추출(한국 종목명 그대로, 해외는 티커로 정규화: 테슬라 → TSLA)해 허브 `StockAnalysisPort`로
분석하고 7.8B가 서술한다(추천 pin 없음, text + `stock` 카드 데이터). 그 외(`market`)는 기존 상권 2단계 추론으로.
분류 실패 시 market 폴백. 주식 서술 규칙: 매수/매도 지시·확률 단정 금지, 책임 고지 포함
(백테스트 결론 — 규칙 신호는 확률 근거 부족).

## 추천 기록 — 허브 포트 경유

`ask()`는 phase2 추천을 만든 뒤 허브 `RecommendationRecordPort`(구현: recommendation의
`RecommendationRecordGateway`)로 기록한다. recommendation을 직접 import하지 않고
허브 포트만 의존한다(스타 토폴로지). `stream_reply()`는 구조화 추천이 없어 기록하지 않는다.

## 단계별 추론 — 모델 계층 분리

| 단계 | 역할 | 모델 |
|------|------|------|
| **phase0** | 의도 분류(상권 vs 주식) + 종목 질의 추출 | EXAONE **2.4B** |
| **phase1** | 질문 → 업종 코드 + 후보 상권 선택 (도메인 판단) | EXAONE **2.4B** (`orchestrate(model=EXAONE_2_4B)`) |
| **phase2** | 후보의 원시 통계 → 최종 서술·추천 (**최종 사용자 답변**) | EXAONE **7.8B** (오케스트레이터 기본) |

- 두 단계 모두 `orchestrate(..., format="json")`으로 유효 JSON 출력을 강제한다(소형 모델 견고화).
- `_build_area_context`는 1650개 상권 전체 대신 **질문에 언급된 자치구 우선 + 월매출 상위 80개**로
  상한을 둔다(2.4B 컨텍스트 초과 방지).
- 모델 계층 바인딩 원칙 상세 → hub CLAUDE / 오케스트레이터.

## 멀티턴 · 스트리밍

- `conversations` / `messages` 테이블로 대화 맥락 보존. `ask(prompt, conversation_id)`가
  직전 대화를 phase1 컨텍스트에 주입한다("그 중 …" 같은 지시 해소).
- `POST /chat/stream` — SSE(`text/event-stream`)로 `meta → delta* → done` 스트리밍.

## 레이어

```
apps/chat/
├── app/use_cases/chat_interactor.py   # 대장 — 허브 포트 소비 + 2단계 오케스트레이션
├── adapter/outbound/
│   ├── orm/conversation_orm.py        # conversations · messages
│   └── pg/conversation_pg_repository.py
├── adapter/inbound/api/v1/chat_router.py  # /chat/ask · /chat/stream
└── dependencies/chat_provider.py
```
