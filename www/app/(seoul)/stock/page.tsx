"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { ApiError, fetchPriceHistory, fetchStockAnalysis } from "@/lib/api";
import { useChatStore } from "@/lib/store";
import WorkspaceShell from "@/components/workspace/WorkspaceShell";
import ChatPanel from "@/components/chat/ChatPanel";
import SymbolHeader from "@/components/stock/SymbolHeader";
import StockPanel from "@/components/stock/StockPanel";

// lightweight-charts는 SSR 불가 — 클라이언트에서만 로드
const CandleChart = dynamic(() => import("@/components/stock/CandleChart"), {
  ssr: false,
  loading: () => <div className="flex-1 m-4 skeleton rounded-xl" />,
});

type Timeframe = "1d" | "5m";

const EMPTY_PROMPTS = [
  "삼성전자 주가 어때요?",
  "엔비디아 지금 들어가도 될까요?",
  "요즘 시장 분위기 어때요?",
];

function StockWorkspace() {
  const router = useRouter();
  const params = useSearchParams();
  const symbol = params.get("symbol") ?? "";
  const c = params.get("c");
  const [timeframe, setTimeframe] = useState<Timeframe>("1d");

  const conversationId = useChatStore((s) => s.conversationId);
  const messages = useChatStore((s) => s.messages);

  const setSymbol = (next: string) => {
    const cid = conversationId ?? c;
    router.replace(
      `/stock?symbol=${encodeURIComponent(next)}${cid ? `&c=${cid}` : ""}`,
      { scroll: false },
    );
  };

  // 채팅 응답에 종목 카드가 오면 URL(?symbol)에 반영 — 마운트 시 기존 메시지는 건너뛴다
  const handledRef = useRef<string | null>(messages[messages.length - 1]?.id ?? null);
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (!last || last.role !== "assistant" || handledRef.current === last.id) return;
    handledRef.current = last.id;
    if (last.stock && last.stock.symbol !== symbol) setSymbol(last.stock.symbol);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  const analyzeQ = useQuery({
    queryKey: ["stock-analyze", symbol],
    queryFn: () => fetchStockAnalysis(symbol),
    enabled: !!symbol,
    staleTime: 5 * 60_000, // 분석은 yfinance+LLM 경유라 느림 — 심볼 전환 재방문 캐시 히트
  });
  const pricesQ = useQuery({
    queryKey: ["prices", symbol, timeframe],
    queryFn: () => fetchPriceHistory(symbol, timeframe),
    enabled: !!symbol,
    retry: false,
  });

  const pricesNotCollected = pricesQ.error instanceof ApiError && pricesQ.error.status === 404;

  const stage = !symbol ? (
    <EmptyStage onSubmit={setSymbol} />
  ) : (
    <>
      <SymbolHeader
        symbol={symbol}
        resolvedTicker={pricesQ.data?.resolvedTicker}
        analyze={analyzeQ.data}
        isLoading={analyzeQ.isLoading}
      />
      {pricesQ.isLoading && <div className="flex-1 m-4 skeleton rounded-xl" />}
      {pricesNotCollected && (
        <div className="flex-1 grid place-items-center px-6 text-center">
          <div>
            <p className="text-sm font-medium">이 종목은 시세 수집 대상이 아니에요</p>
            <p className="mt-1.5 text-xs text-foreground-muted leading-relaxed">
              차트는 워치리스트 종목만 제공됩니다.
              <br />
              우측 지표·분석은 실시간 조회라 정상 동작해요.
            </p>
          </div>
        </div>
      )}
      {pricesQ.data && (
        <CandleChart
          bars={pricesQ.data.bars}
          support={analyzeQ.data?.support}
          resistance={analyzeQ.data?.resistance}
        />
      )}
      <div className="shrink-0 flex items-center gap-1 px-4 py-2 border-t border-border">
        {(["1d", "5m"] as const).map((tf) => (
          <button
            key={tf}
            type="button"
            onClick={() => setTimeframe(tf)}
            aria-pressed={timeframe === tf}
            className={`px-3 h-7 rounded-md text-xs font-medium transition-colors ${
              timeframe === tf
                ? "bg-brand text-white"
                : "text-foreground-muted hover:bg-black/5"
            }`}
          >
            {tf === "1d" ? "일봉" : "5분봉"}
          </button>
        ))}
        {timeframe === "5m" && (
          <span className="ml-2 text-[11px] text-foreground-muted">최근 60일 보유</span>
        )}
      </div>
    </>
  );

  return (
    <WorkspaceShell
      stageLabel="차트"
      stage={stage}
      panel={<StockPanel symbol={symbol} analyze={analyzeQ.data} />}
      chat={
        <ChatPanel
          workspace="stock"
          placeholder="종목명이나 티커로 물어보세요"
          emptyPrompts={EMPTY_PROMPTS}
          onSelectStock={(stock) => setSymbol(stock.symbol)}
        />
      }
    />
  );
}

function EmptyStage({ onSubmit }: { onSubmit: (symbol: string) => void }) {
  // FormData 패턴 — 제출 시점에만 값 수집 (REACT_RULES 패턴 A)
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const value = String(new FormData(e.currentTarget).get("symbol") ?? "").trim();
    if (value) onSubmit(value);
  };

  return (
    <div className="flex-1 grid place-items-center px-6">
      <div className="w-full max-w-sm text-center">
        <h2 className="text-lg font-semibold">주식 분석 워크스페이스</h2>
        <p className="mt-1.5 text-sm text-foreground-muted">
          채팅으로 물어보거나 종목 코드를 직접 입력하세요
        </p>
        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
          <input
            name="symbol"
            aria-label="종목 코드 또는 티커"
            placeholder="005930, AAPL …"
            className="flex-1 h-10 px-3.5 rounded-xl border border-border bg-surface outline-none text-sm focus:border-brand/50"
          />
          <button
            type="submit"
            className="h-10 px-4 rounded-xl bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors inline-flex items-center gap-1.5"
          >
            <Search size={15} strokeWidth={2} />
            열기
          </button>
        </form>
      </div>
    </div>
  );
}

export default function StockPage() {
  return (
    <Suspense>
      <StockWorkspace />
    </Suspense>
  );
}
