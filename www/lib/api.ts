import { authHeader } from "./tokenStorage";
import type {
  AreaScoreDetail,
  AreaStatsDetail,
  ConversationMessage,
  ConversationSummary,
  Fundamentals,
  MarketArea,
  PriceHistory,
  RecommendationItem,
  StockAnalyzeResult,
  StockNewsItem,
} from "./types";

// 모든 GET 조회는 next.config rewrites(/api/backend/* → FastAPI)를 경유한다.
async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`/api/backend${path}`, { headers: authHeader() });
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
    { method: "POST", headers: authHeader() },
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

export const fetchAreaStats = (trdarCode: string | number): Promise<AreaStatsDetail> =>
  getJson(`/market/trdar/${trdarCode}/stats`);

export const fetchAreaScore = (trdarCode: string | number): Promise<AreaScoreDetail> =>
  getJson(`/market/trdar/${trdarCode}/score`);

export const fetchAreaInfo = (trdarCode: string | number): Promise<MarketArea> =>
  getJson(`/market/trdar/${trdarCode}/area`);

export const fetchConversations = (limit = 30): Promise<ConversationSummary[]> =>
  getJson(`/chat/conversations?limit=${limit}`);

export const fetchConversationMessages = (id: number): Promise<ConversationMessage[]> =>
  getJson(`/chat/conversations/${id}/messages`);

export const fetchRecommendations = (limit = 8): Promise<RecommendationItem[]> =>
  getJson(`/recommendations?limit=${limit}`);
