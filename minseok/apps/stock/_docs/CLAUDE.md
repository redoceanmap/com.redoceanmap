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
- **워치리스트 3계층** (`scripts/news_watchlist.txt`, 뉴스·시세·펀더멘털 수집기 공유):
  ① 코어 68(한국 2 고정 — 추가 금지 2026-07-21 확정 + 빅테크·테크 28 + 업종 다양성 38,
  GME 포함, 수동 관리), ② `auto:screened` 10 — `scripts/screen_us_undervalued.py`(주 1회 cron)가
  yfinance 무료 스크리너로 미국 저평가 대형주를 PER+PBR 랭킹해 자동 교체(히스테리시스:
  기존 편입은 상위 20위 이내면 유지, 한국 기업 ADR 제외), ③ `auto:demand` ≤5 — 분석 질문
  수요(`stock_demand` 테이블, `StockInteractor`가 기록) 상위를 같은 스크립트가 편입,
  14일 질문 없으면 퇴출. 허브 `StockDemandPort`(`GET /automation/stock-demand`)가 조회 창구.
  기관등급(yfinance)은 429 방지를 위해 `collect_news.py --analyst`로 분리(일 1회 cron).
- **미수집 종목 라이브 폴백**: `stock_history`(1d)·`stock_forecast`는 DB에 봉이 없으면
  `MarketDataPort.daily_bars`(yfinance 2y)로 즉석 계산하고 응답에 `live: true`를 표기 —
  임의 티커도 첫 질문부터 차트·확률이 뜬다(저장 안 함, 5m는 폴백 없음). quote는 서버 측
  심볼당 20초 공유 캐시로 다중 사용자 폴링에도 벤더 호출을 상한한다.
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
  `GET /stock/{symbol}/fundamentals`(소스별 최신 스냅샷 + `fundamental_narrator` 규칙 해석 —
  PER/PBR/ROE, dart 우선 병합, debt_to_equity는 단위 혼재로 해석 제외). 분석(yfinance 라이브)과
  달리 DB 축적분만 읽는다. 거래소 접미 매칭(005930 ↔ 005930.KS)은 PG 리포지토리가 맡고,
  실제 저장 티커는 `resolvedTicker`로 노출한다.
- **확률·예측 밴드(`stock_forecast` 슬라이스)**: `GET /stock/{symbol}/forecast?horizon=5` —
  저장 일봉 전체에 `Backtester.distribution()`(워크포워드, 감성 중립)을 돌려 **지금과 같은
  방향 신호가 났던 과거 평가일들의 상승 비율(확률)과 실현 수익률 분위수(25/50/75%)**를 반환.
  표본수·Wilson 95% 구간·기준선(평소 상승률)·`ready`(n≥100 + 하한>기준선) 동반, 같은 신호
  표본 30 미만이면 ATR 콘 폴백(`band.source: "atr"`). 인메모리 캐시(티커·horizon별, 마지막 봉
  ts 기준)로 일 1회만 재계산. **확률 노출 정책**: 실측 통계 + 표본·신뢰구간·기준선·"과거
  통계" 고지 병기 형태만 허용 — score 환산 등 근거 없는 확률 숫자 단독 노출 금지(기존 "확률
  제시 보류"의 해소 형태). chat 답변의 확률 단정 금지는 그대로 유지(페이지 전용).
- **예측 스냅샷·사후 채점(`forecast_snapshot` 슬라이스)**: 일일 cron(`scripts/snapshot_forecasts.py`,
  07:30, horizons 5·20)이 허브 `POST /automation/forecast-snapshots`(+`/score`)로 워치리스트
  forecast(방향·확률·밴드)와 신호 분해(breakdown)를 `forecast_snapshots` 테이블에 동결하고
  ((ticker, horizon_days, as_of) 유니크 — 재실행 멱등), horizon 도래분을 price_bars(1d)
  실현 수익률로 채점한다(UP→상승, DOWN→비상승 적중, NEUTRAL은 hit NULL — Backtester 의미론).
  캡처는 `StockForecastUseCase` 재사용 + market_data=None(라이브 폴백 차단, 미수집 종목 skip).
  요약(`summary`)은 방향·호라이즌·신호별(원신호 부호↔실현 수익률 부호 일치율) 적중률을 집계 —
  허브 `ForecastSnapshotPort`를 `ForecastSnapshotGateway`가 구현, admin `/admin/forecasts`가 소비.
  가중치 재적합·캘리브레이션의 원료 데이터 축(백테스트가 못 주는 진짜 out-of-sample 성적).
- **현재가 폴링(`stock_quote` 슬라이스)**: `GET /stock/{symbol}/quote` — `MarketDataPort.quote()`
  (yfinance fast_info, 이력 미조회)로 지연 시세 현재가만 경량 반환(`delayed: true`). 프론트
  30초 폴링용. 진짜 실시간은 KIS 등 벤더 어댑터 교체 경로(계약 동일)로 후속.

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
