"use client";

import { ShieldCheck } from "lucide-react";
import type { StockAnalyzeResult } from "@/lib/types";
import { formatPrice } from "@/lib/currency";

type SymbolHeaderProps = {
  symbol: string;
  resolvedTicker?: string;
  analyze?: StockAnalyzeResult;
  isLoading: boolean;
  quotePrice?: number | null; // 30초 폴링 현재가(지연 시세) — 있으면 분석 시점 가격보다 우선
  previousClose?: number | null; // 전일 종가 — 등락률 기준
};

export default function SymbolHeader({
  symbol,
  resolvedTicker,
  analyze,
  isLoading,
  quotePrice,
  previousClose,
}: SymbolHeaderProps) {
  const price = quotePrice ?? analyze?.price;
  const changePct =
    price != null && previousClose ? (price / previousClose - 1) * 100 : null;

  return (
    <div className="shrink-0 flex flex-wrap items-center gap-x-3 gap-y-1 px-4 py-2.5 border-b border-border">
      <span className="text-base font-bold">{symbol}</span>
      {resolvedTicker && resolvedTicker !== symbol && (
        <span className="text-xs text-foreground-muted">{resolvedTicker}</span>
      )}
      {isLoading && <span className="skeleton h-5 w-28 rounded-md" />}
      {analyze && (
        <>
          <span className="text-lg font-bold">
            {formatPrice(quotePrice ?? analyze.price, resolvedTicker ?? symbol)}
          </span>
          {changePct !== null && (
            <span
              className={`text-sm font-semibold tabular-nums ${
                changePct > 0 ? "text-red-600" : changePct < 0 ? "text-blue-600" : "text-foreground-muted"
              }`}
            >
              {changePct > 0 ? "+" : ""}
              {changePct.toFixed(2)}%
              <span className="ml-1 text-[10px] font-normal text-foreground-muted">전일 대비</span>
            </span>
          )}
          {quotePrice != null && (
            <span className="text-[10px] text-foreground-muted">지연 시세 · 30초 갱신</span>
          )}
          {/* 방향·확신도 배지는 StageSummary가 단독으로 말한다 — 여기 두면 확률 카드와
              서로 반박하는 숫자가 한 화면에 둘이 된다(상승 36% vs 평소와 다르지 않음). */}
          {analyze.reference_up_signal && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full border border-amber-200 bg-amber-50 text-amber-700 text-xs font-medium">
              <ShieldCheck size={13} strokeWidth={2} />
              백테스트 참고 신호
            </span>
          )}
        </>
      )}
    </div>
  );
}
