import type {
  AreaDetail,
  AreaScoreDetail,
  AreaStatsDetail,
  ConversationMessage,
  ConversationSummary,
  Fundamentals,
  MarketArea,
  PriceHistory,
  RecommendationItem,
  StockAnalyzeResult,
  StockBoard,
  StockForecast,
  StockNewsItem,
  StockQuote,
} from "./types";

// 모든 GET 조회는 next.config rewrites(/api/backend/* → FastAPI)를 경유한다.
async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`/api/backend${path}`);  // 세션은 httpOnly 쿠키 — 자동 동행
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiError(res.status, detail?.detail ?? "요청에 실패했습니다.");
  }
  return res.json();
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

// 조회형 POST(부작용 없음) — react-query useQuery로 소비한다.
export const fetchStockAnalysis = async (symbol: string): Promise<StockAnalyzeResult> => {
  const res = await fetch(
    `/api/backend/stock/analyze?symbol=${encodeURIComponent(symbol)}`,
    { method: "POST" },
  );
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiError(res.status, detail?.detail ?? "분석에 실패했습니다.");
  }
  return res.json();
};

export const fetchPriceHistory = (
  symbol: string,
  timeframe: "1d" | "5m",
  limit = 500,
): Promise<PriceHistory> =>
  getJson(`/stock/${encodeURIComponent(symbol)}/prices?timeframe=${timeframe}&limit=${limit}`);

export const fetchStockNews = (symbol: string, limit = 20): Promise<StockNewsItem[]> =>
  getJson(`/stock/${encodeURIComponent(symbol)}/news?limit=${limit}`);

export const fetchFundamentals = (symbol: string): Promise<Fundamentals> =>
  getJson(`/stock/${encodeURIComponent(symbol)}/fundamentals`);

export const fetchStockForecast = (symbol: string): Promise<StockForecast> =>
  getJson(`/stock/${encodeURIComponent(symbol)}/forecast`);

export const fetchStockQuote = (symbol: string): Promise<StockQuote> =>
  getJson(`/stock/${encodeURIComponent(symbol)}/quote`);

// 워치리스트 신호 보드 — 종목별 analyze/forecast를 N번 부르지 않고 축적 스냅샷을 한 번에 읽는다
export const fetchStockBoard = (horizon = 5, limit = 40): Promise<StockBoard> =>
  getJson(`/stock/board?horizon=${horizon}&limit=${limit}`);

export const fetchAreaStats = (trdarCode: string | number): Promise<AreaStatsDetail> =>
  getJson(`/market/trdar/${trdarCode}/stats`);

export const fetchAreaScore = (trdarCode: string | number): Promise<AreaScoreDetail> =>
  getJson(`/market/trdar/${trdarCode}/score`);

export const fetchAreaInfo = (trdarCode: string | number): Promise<MarketArea> =>
  getJson(`/market/trdar/${trdarCode}/area`);

export const fetchAreaDetail = (trdarCode: string | number): Promise<AreaDetail> =>
  getJson(`/market/trdar/${trdarCode}/detail`);

export const fetchConversations = (limit = 30): Promise<ConversationSummary[]> =>
  getJson(`/chat/conversations?limit=${limit}`);

export const fetchConversationMessages = (id: number): Promise<ConversationMessage[]> =>
  getJson(`/chat/conversations/${id}/messages`);

export const fetchRecommendations = (limit = 8): Promise<RecommendationItem[]> =>
  getJson(`/recommendations?limit=${limit}`);
