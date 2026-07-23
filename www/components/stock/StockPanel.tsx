"use client";

import { useState } from "react";
import { useDensityStore } from "@/lib/uiStore";
import type { StockAnalyzeResult } from "@/lib/types";
import IndicatorPanel from "./IndicatorPanel";
import NewsPanel from "./NewsPanel";
import FundamentalsPanel from "./FundamentalsPanel";

type Tab = "indicators" | "news" | "fundamentals";

const TABS: { key: Tab; label: string }[] = [
  { key: "indicators", label: "지표" },
  { key: "news", label: "뉴스" },
  { key: "fundamentals", label: "펀더멘털" },
];

// 주식 자료 패널 — 지표/뉴스/펀더멘털 탭. 단일 useState(탭)만 사용.
export default function StockPanel({
  symbol,
  analyze,
}: {
  symbol: string;
  analyze?: StockAnalyzeResult;
}) {
  const [tab, setTab] = useState<Tab>("indicators");
  const expert = useDensityStore((s) => s.expert);

  if (!symbol) {
    return <p className="p-4 text-sm text-foreground-muted">종목을 선택하면 자료가 표시됩니다.</p>;
  }

  return (
    <div>
      <nav className="sticky top-0 bg-background z-10 flex border-b border-border" aria-label="자료 탭">
        {TABS.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            aria-pressed={tab === t.key}
            className={`flex-1 h-10 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t.key
                ? "border-brand text-brand"
                : "border-transparent text-foreground-muted hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>
      {tab === "indicators" && <IndicatorPanel analyze={analyze} symbol={symbol} expert={expert} />}
      {tab === "news" && <NewsPanel symbol={symbol} />}
      {tab === "fundamentals" && <FundamentalsPanel symbol={symbol} />}
    </div>
  );
}
