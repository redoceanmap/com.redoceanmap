# CLAUDE.md — stock 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

주식 분석 스포크. 트레이더용 지표 + 뉴스 감성을 결합해 사용자가 물은 종목의
상승/하락 방향·확신도(장기 목표: 확률·매수 타이밍·지지/저항선 제시)를 알려준다.
매매 실행(주문/포지션)은 다루지 않는다 — 분석·정보 제공까지가 범위.

---

## 역할

- **대상 시장: 한국(코스피/코스닥) + 미국.** 한국 6자리 코드는 어댑터가 `.KS` → `.KQ` 순으로 해석.
- `StockInteractor`(대장)가 시세/지표 조회 → 뉴스 감성 점수화 → `OutlookPredictor`(도메인 서비스)로
  방향 전망 산출을 조립한다. 지표 계산(RSI·MA·지지/저항)은 `IndicatorCalculator`(순수 도메인)가 담당.
- 시세/지표/뉴스는 `YFinanceMarketDataAdapter`(yfinance, 키 불요·지연 시세). 실시간이 필요해지면
  KIS 등 벤더 어댑터로 교체한다(`MarketDataPort` 계약 동일). 헤드라인이 없으면 감성은 중립(0.0)으로
  두고 LLM을 부르지 않는다.
- 감성 점수화는 `ExaoneSentimentAdapter`가 LLM 오케스트레이터(기본 모델 7.8B — 단일 모델 정책)로 수행.
- **수집 뉴스(DB)**: n8n이 허브 `/automation/news`로 적재(허브 `NewsStoragePort`를
  `NewsStorageGateway`가 구현, `news_articles` 테이블·url 유니크). 분석 시 DB 뉴스를
  벤더(yfinance) 뉴스보다 우선 병합 — 한국 종목 뉴스 공백 해소. n8n은 허브만 안다.
- **뉴스 의미 검색(RAG)**: 적재 시 제목을 bge-m3(1024차원, 오케스트레이터 `embed_many` 경유)로
  임베딩(`news_articles.embedding`, 실패 시 NULL — 수집 우선·다음 주기 자연 재시도).
  허브 `NewsSearchPort`를 `NewsSearchGateway`가 구현 — pgvector 코사인 + 티커 하이브리드 필터 +
  news_labels 라벨 조인 + 제목 dedupe. 소비자는 chat(종목 질문 보강 + 시장 횡단 질문).
  백필은 `POST /automation/news-embeddings/backfill`. 벡터 인덱스는 10만 건+에서 hnsw 재검토.
- **수집 OHLCV(DB)**: cron(`scripts/collect_prices.py`, 뉴스와 워치리스트 공유)이 허브
  `/automation/prices`로 적재(허브 `PriceBarStoragePort`를 `PriceBarStorageGateway`가 구현,
  `price_bars` 테이블·(ticker, timeframe, ts) 유니크). 5분봉(60일 소급)·일봉(전체) —
  뉴스 발행 후 주가 반응 라벨링용. 장외 발행 뉴스는 "다음 개장 첫 봉" 기준으로 라벨한다.
- **수집 펀더멘털(DB)**: 주간 cron(`scripts/collect_fundamentals.py`, yfinance + DART 무료 API)이
  허브 `/automation/fundamentals`로 적재(허브 `FundamentalStoragePort`를 `FundamentalStorageGateway`가
  구현, `fundamental_snapshots` 테이블·(ticker, as_of, source) 유니크). PER/PBR/ROE/부채비율/FCF/EPS/BPS —
  버핏식 가치·체력 축. 한국 종목은 DART 연간 재무제표로 EPS/BPS→PER/PBR 자체 계산(source=dart 별도 행).
  판정(OutlookPredictor) 편입은 분기 지평 백테스트 설계 후 — 축적이 먼저(뉴스 감성과 동일 원칙).
- **뉴스 LLM 라벨(DB)**: 야간 cron(`scripts/label_news.py`, EXAONE 7.8B Ollama 경유 —
  도메인 내부 추론 계층 준수)이 허브 `/automation/news-labels`로 적재(허브 `NewsLabelStoragePort`를
  `NewsLabelStorageGateway`가 구현, `news_labels` 테이블·(news_id, labeler) 유니크).
  감성(-1~1)·이벤트 유형·확신도. 라벨은 피처, 정답은 실현 수익률 — 라벨 품질은
  price_bars 조인으로 사후 채점한다.
- **백테스트**: `Backtester`(순수 도메인) + `scripts/backtest_stock.py`. 워크포워드로 t까지의
  데이터만 써서 t+horizon 종가와 비교, 항상-UP 기준선과 대조한다. 과거 뉴스는 수집 불가라
  감성 중립(0.0) 고정 — 지표 신호만 채점.
  - **스윕 결론 1차(2026-07 초, RSI+MA만)**: 어떤 가중치·임계값 조합도 기준선을 못 이김
    → 기본값(±0.3) 유지, 확률 제시 근거 부족.
  - **재채점 2차(2026-07-13, 피처 확장 — 로드맵 ①-M2)**: ATR·볼린저 %B·거래량비·OBV 추가,
    21조합 × 24종목 · 5y 스윕 + 판정 기준 명문화(n≥100 + Wilson 95% 하한 > 기준선,
    `backtest_report.py`). **RSI+BB ±0.35 UP 신호만 인샘플·홀드아웃(이전 5y) 양쪽 통과**
    (기준선 +1.9~2.1%p, 하한 마진 +0.4%p) — 첫 재현 양성 신호. 단 다중 비교 1건에 마진이
    얇아 **확률 제시는 계속 보류**, "참고 신호" 수준. OBV·ATR거부는 효과 없음. 다음 재채점은
    뉴스 감성 축적(~3개월) 후. 상세 →
    [[minseok/apps/stock/_docs/BACKTEST_RESCORE_2026-07|BACKTEST_RESCORE_2026-07]]
  - **재채점 3차(2026-07-14, 12-1 모멘텀 + 거래량 확인)**: `closes[-22]/closes[-253]-1` 모멘텀과
    `volume_confirm` 강등 필터 추가, 30조합 스윕(홀드아웃은 `--drop-last 1260`으로 재현).
    **RSI+BB+MOM(0.4/0.4/0.2) ±0.35 UP이 새 최우수 검증 신호**(인샘플 하한 +3.5%p·홀드아웃 +0.9%p,
    0.25 임계값도 연속 통과). 모멘텀 단독·거래량 필터는 기각, 하락 예측 불가 재확인.
    확률 제시·기본값은 계속 보류/불변. `analyze` 응답의 `reference_up_signal`은 2차 검증
    조합(RSI+BB ±0.35, `AnalysisConfig.rsi_bb_reference()`)을 노출 — 감성 재채점에서 재현 시 승격 재검토.
- **분석 API 노출 지표**: RSI(14)·MA20/50·지지/저항(60일)·ATR%·볼린저 %B·거래량비(5/20일)·
  OBV 기울기·12-1 모멘텀 + `reference_up_signal`(검증 참고 신호, 확률 아님). 시세 이력은 2y
  (모멘텀에 253거래일 필요).
- **수집 데이터 조회(프론트 자료 패널)**: `stock_history` 조회 전용 슬라이스 —
  `GET /stock/{symbol}/prices?timeframe=1d|5m&limit=`(OHLCV, ts 오름차순, 미보유 심볼 404),
  `GET /stock/{symbol}/news?limit=`(뉴스+라벨 조인, 발행일 내림차순),
  `GET /stock/{symbol}/fundamentals`(소스별 최신 스냅샷). 분석(yfinance 라이브)과 달리
  DB 축적분만 읽는다. 거래소 접미 매칭(005930 ↔ 005930.KS)은 PG 리포지토리가 맡고,
  실제 저장 티커는 `resolvedTicker`로 노출한다.

## 레이어

```
apps/stock/
├── domain/
│   ├── entities/{analysis_config,outlook}.py       # AnalysisConfig · Outlook(Direction)
│   ├── value_objects/{indicators,market_values,sentiment_score}.py
│   └── services/
│       ├── indicator_calculator.py                  # OHLC 시계열 → RSI/MA/지지·저항 (순수)
│       └── outlook_predictor.py                     # 지표+감성 → 방향/확신도 (순수)
├── app/
│   ├── dtos/stock_analysis_dto.py                   # StockAnalysis
│   ├── exceptions.py                                # StockError · MarketDataUnavailableError
│   ├── ports/input/stock_use_case.py
│   ├── ports/output/{market_data_port,sentiment_port}.py
│   └── use_cases/stock_interactor.py                # 대장
├── adapter/
│   ├── inbound/api/v1/stock_router.py               # POST /stock/analyze (앱 예외 → 404)
│   └── outbound/
│       ├── yfinance_market_data_adapter.py          # MarketDataPort 구현 (한국+미국)
│       ├── fake_market_data_adapter.py              # 테스트용 고정값
│       └── exaone_sentiment_adapter.py              # SentimentPort 구현 (오케스트레이터 경유)
├── dependencies/stock_provider.py
└── tests/                                           # 라이브 조회 테스트는 @pytest.mark.network
```

**의존 방향:** `adapter → app → domain`. 컨벤션 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].
