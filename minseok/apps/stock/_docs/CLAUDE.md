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
- 감성 점수화는 `ExaoneSentimentAdapter`가 LLM 오케스트레이터(`orchestrate(model=EXAONE_2_4B)`)로 수행.
- **수집 뉴스(DB)**: n8n이 허브 `/automation/news`로 적재(허브 `NewsStoragePort`를
  `NewsStorageGateway`가 구현, `news_articles` 테이블·url 유니크). 분석 시 DB 뉴스를
  벤더(yfinance) 뉴스보다 우선 병합 — 한국 종목 뉴스 공백 해소. n8n은 허브만 안다.
- **백테스트**: `Backtester`(순수 도메인) + `scripts/backtest_stock.py`. 워크포워드로 t까지의
  데이터만 써서 t+horizon 종가와 비교, 항상-UP 기준선과 대조한다. 과거 뉴스는 수집 불가라
  감성 중립(0.0) 고정 — 지표 신호만 채점.
  - **스윕 결론(2026-07, 24종목 KR12+US12 · 5y · horizon 5)**: RSI+MA 규칙 신호는
    가중치 4종 × 임계값 3~4종 어떤 조합에서도 항상-UP 기준선을 유의하게 못 이긴다
    (UP 적중률 기준선 ±1%p 이내, DOWN은 역기준선 수준). 2종목(2y)에서 보였던 우위는
    다종목에서 소멸 — 국면 착시. → **기본값(±0.3) 유지**, 규칙 점수를 "확률"로 제시하는 것은
    근거 부족. 확률 제시는 학습 기반 예측기(자체 모델 비전) 또는 피처 확장(거래량·변동성 등)
    후 이 하네스로 재채점해서 결정한다.

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
