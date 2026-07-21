// 백엔드 계약 타입 모음 — 채팅 응답(AskResponse)과 조회 API 응답의 단일 정의처.

// ── 채팅 응답: 상권 추천 카드 (AreaStats는 서버가 문장으로 포맷한 텍스트 계약) ──

export type AreaStats = {
  // 수익성 (공공데이터 실계산)
  monthlyRevenueText: string;
  revenueSourceText: string;
  weekdayText: string;
  // 점포 현황
  storeCountText: string;
  closureRateText: string;
  openingRateText: string;
  franchiseText: string;
  // 유동인구
  footTrafficText: string;
  topAgeText: string;
  peakTimeText: string;
  // 상권 변화
  changeText: string;
  operatingMonthsText: string;
  // 메타
  dataSource: string;
  hasRealData: boolean;
};

export type Area = {
  id: string; // trdar_code — /market/trdar/{id}/stats 조회 키
  name: string;
  lat: number;
  lng: number;
  category: string;
  reason: string;
  stats: AreaStats;
};

// ── 채팅 응답: 종목 카드 ──

export type StockAnalysis = {
  symbol: string;
  price: number;
  direction: "UP" | "DOWN" | "NEUTRAL";
  confidence: number;
  rsi: number;
  ma20: number;
  ma50: number;
  support: number;
  resistance: number;
  sentimentLabel: string;
  headlines: string[];
  atrPct?: number;
  bbPercentB?: number;
  volumeRatio?: number;
  obvSlope?: number;
  momentum12To1?: number;
  referenceUpSignal?: boolean;
};

// ── POST /stock/analyze (직접 호출 — snake_case DTO) ──

export type SignalContribution = {
  key: "sentiment" | "rsi" | "trend" | "bollinger" | "obv" | "momentum";
  signal: number; // -1 ~ 1 원신호
  weight: number;
  contribution: number; // signal × weight
};

export type StockAnalyzeResult = {
  symbol: string;
  price: number;
  direction: "UP" | "DOWN" | "NEUTRAL";
  confidence: number;
  sentiment: number;
  sentiment_label: string;
  rsi: number;
  ma20: number;
  ma50: number;
  support: number;
  resistance: number;
  headlines: string[];
  atr_pct: number;
  bb_percent_b: number;
  volume_ratio: number;
  obv_slope: number;
  momentum_12_1: number;
  reference_up_signal: boolean;
  // 신규 필드 — 구버전 응답 호환을 위해 옵셔널
  score?: number; // 가중 합산 종합 점수 (-1~1)
  up_threshold?: number;
  down_threshold?: number;
  neutral_reason?: "atr_veto" | "volume_confirm" | null;
  signals?: SignalContribution[];
  insights?: Insight[];
};

// ── GET /stock/{symbol}/forecast ──

export type StockForecast = {
  symbol: string;
  resolved_ticker: string;
  as_of: string;
  base_price: number;
  horizon_days: number;
  signal_direction: "UP" | "DOWN" | "NEUTRAL"; // 지표 신호 기준(감성 미반영)
  probability: {
    up_rate: number;
    sample_size: number;
    hits: number;
    ci_low: number; // Wilson 95%
    ci_high: number;
    baseline_up_rate: number;
    ready: boolean; // n≥100 + 하한 > 기준선
  } | null;
  band: {
    source: "quantile" | "atr";
    q25_pct: number; // horizon일 뒤 수익률 (-0.011 = -1.1%)
    median_pct: number;
    q75_pct: number;
  } | null;
  insights: Insight[];
  live?: boolean; // true = 미수집 종목 — yfinance 라이브 이력 기반 계산
};

// ── GET /stock/{symbol}/quote ──

export type StockQuote = {
  symbol: string;
  price: number;
  delayed: boolean; // true = 지연 시세(yfinance 무료)
};

// ── GET /stock/{symbol}/prices ──

export type PriceBar = {
  ts: string; // 봉 시작(UTC ISO)
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type PriceHistory = {
  symbol: string;
  resolvedTicker: string;
  timeframe: "1d" | "5m";
  bars: PriceBar[]; // ts 오름차순
  live?: boolean; // true = 미수집 종목 — yfinance 라이브 이력 폴백
};

// ── GET /stock/{symbol}/news ──

export type StockNewsItem = {
  id: number;
  title: string;
  source: string;
  url: string;
  publishedAt: string | null;
  sentiment: number | null; // -1 ~ +1
  eventType: string | null;
  confidence: number | null;
};

// ── GET /stock/{symbol}/fundamentals ──

export type FundamentalSnapshot = {
  asOf: string;
  source: "yfinance" | "dart";
  per: number | null;
  pbr: number | null;
  roe: number | null;
  debtToEquity: number | null;
  fcf: number | null;
  marketCap: number | null;
  eps: number | null;
  bps: number | null;
};

export type Fundamentals = {
  symbol: string;
  snapshots: FundamentalSnapshot[];
  insights?: Insight[]; // 규칙 기반 해석(dart 우선 병합)
};

// ── GET /market/trdar/{code}/stats ──

export type QuarterStat = {
  yearQuarter: number; // 예: 20244
  monthlySales: number | null;
  weekdaySales: number | null;
  storeCount: number | null;
  openingRate: number | null;
  closureRate: number | null;
  franchiseCount: number | null;
  totalFloatingPop: number | null;
};

export type AreaStatsDetail = {
  trdarCode: number;
  trdarName: string;
  districtName: string;
  serviceCode: string | null;
  serviceName: string | null;
  series: QuarterStat[]; // yearQuarter 오름차순
  latest: {
    floatingByAge: {
      age10: number; age20: number; age30: number;
      age40: number; age50: number; age60Plus: number;
    } | null;
    floatingByTime: {
      t00_06: number; t06_11: number; t11_14: number;
      t14_17: number; t17_21: number; t21_24: number;
    } | null;
    changeIndicator: string | null;
    operatingMonthsAvg: number | null;
    regionOperatingMonthsAvg: number | null;
  };
};

// ── GET /market/trdar/{code}/score ──

export type ScoreComponent = {
  key: "sales_growth" | "floating_growth" | "store_health" | "persistence";
  name: string;
  score: number; // 0~100 — 50이 시도 벤치마크 동률
  value: number;
  benchmark: number;
};

export type AreaScoreDetail = {
  trdarCode: number;
  trdarName: string;
  districtName: string;
  score: {
    total: number;
    grade: string; // 우수 / 양호 / 보통 / 주의 / 위험
    components: ScoreComponent[];
  } | null;
  trend: {
    yearQuarter: number;
    monthlySales: number | null;
    salesQoq: number | null; // 직전 분기 대비 %
    totalFloatingPop: number | null;
    floatingQoq: number | null;
  }[];
};

// ── GET /market/trdar/{code}/detail ──

export type Insight = {
  key: string;
  tone: "positive" | "neutral" | "warning";
  text: string;
};

export type AgeBandRow = { band: string; male: number; female: number };

export type AreaDetail = {
  trdarCode: number;
  trdarName: string;
  districtName: string;
  serviceCode: string | null;
  serviceName: string | null;
  salesMix: {
    yearQuarter: number;
    weekdayAmount: number;
    weekendAmount: number;
    byDay: Record<string, number>; // mon..sun
    byTime: Record<string, number>; // t00_06..t21_24
    byGender: { male: number; female: number };
    byAge: Record<string, number>; // age10..age60Plus
    monthlyCount: number;
  } | null;
  demand: {
    resident: { yearQuarter: number; total: number; byAge: AgeBandRow[] } | null;
    working: { yearQuarter: number; total: number; byAge: AgeBandRow[] } | null;
    households: { total: number; apartment: number } | null;
    apartment: {
      yearQuarter: number;
      complexCount: number;
      avgPrice: number; // 원
      avgArea: number; // ㎡
    } | null;
  } | null;
  spending: {
    yearQuarter: number;
    monthlyAvgIncome: number | null; // 원
    totalExpenditure: number | null; // 원
    byCategory: { key: string; label: string; amount: number }[]; // 금액 내림차순
  } | null;
  insights: Insight[];
};

// ── 채팅 응답: market_news 뉴스 근거 카드 ──

export type NewsCardItem = {
  title: string;
  publishedAt: string | null; // YYYY-MM-DD
  ticker: string | null;
  sentiment: number | null; // -1 ~ +1
  eventType: string | null;
};

// ── GET /chat/conversations ──

export type ConversationSummary = {
  id: number;
  title: string;
  createdAt: string;
};

export type ConversationMessage = {
  role: "user" | "assistant";
  content: string;
  payload: { recommendations?: Area[]; stock?: StockAnalysis; news?: NewsCardItem[] } | null;
  createdAt: string;
};

// ── GET /recommendations ──

export type RecommendationItem = {
  id: number;
  conversation_id: number;
  trdar_code: number;
  trdar_name: string;
  district_name: string;
  category: string;
  reason: string;
  lat: number;
  lng: number;
  created_at: string;
};

// ── GET /market/areas ──

export type MarketArea = {
  trdar_code: number;
  trdar_name: string;
  trdar_div_code: string;
  trdar_div_name: string;
  lat: number;
  lng: number;
  district_name: string;
  adm_dong_name: string;
  area_size: number;
  region: string;
};
