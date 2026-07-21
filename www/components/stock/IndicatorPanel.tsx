"use client";

import type { StockAnalyzeResult } from "@/lib/types";
import InsightList from "@/components/common/InsightList";
import SignalBreakdown from "./SignalBreakdown";

const fmt = (v: number, digits = 2) =>
  v.toLocaleString("ko-KR", { maximumFractionDigits: digits });

export default function IndicatorPanel({ analyze }: { analyze?: StockAnalyzeResult }) {
  if (!analyze) {
    return (
      <div className="p-4 grid grid-cols-2 gap-2">
        {Array.from({ length: 8 }, (_, i) => (
          <div key={i} className="skeleton h-14 rounded-lg" />
        ))}
      </div>
    );
  }

  const stats: [string, string][] = [
    ["RSI(14)", fmt(analyze.rsi, 1)],
    ["볼린저 %B", fmt(analyze.bb_percent_b)],
    ["거래량비 (5/20일)", `${fmt(analyze.volume_ratio)}x`],
    ["OBV 기울기", fmt(analyze.obv_slope, 3)],
    ["12-1 모멘텀", `${fmt(analyze.momentum_12_1 * 100, 1)}%`],
    ["ATR (변동성)", `${fmt(analyze.atr_pct * 100, 1)}%`],
    ["20일 이평", fmt(analyze.ma20)],
    ["50일 이평", fmt(analyze.ma50)],
    ["지지선", fmt(analyze.support)],
    ["저항선", fmt(analyze.resistance)],
  ];

  return (
    <div className="p-4 flex flex-col gap-3">
      <SignalBreakdown analyze={analyze} />

      {analyze.insights && analyze.insights.length > 0 && (
        <div className="bg-surface border border-border rounded-lg px-3 py-2.5">
          <InsightList insights={analyze.insights} />
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        {stats.map(([label, value]) => (
          <div key={label} className="bg-surface border border-border rounded-lg px-3 py-2.5">
            <div className="text-[11px] text-foreground-muted">{label}</div>
            <div className="text-sm font-semibold mt-0.5">{value}</div>
          </div>
        ))}
      </div>

      <div className="bg-surface border border-border rounded-lg px-3 py-2.5">
        <div className="text-[11px] text-foreground-muted">뉴스 감성</div>
        <div className="text-sm font-semibold mt-0.5">
          {analyze.sentiment_label}{" "}
          <span className="text-xs font-normal text-foreground-muted">
            ({analyze.sentiment > 0 ? "+" : ""}{fmt(analyze.sentiment)})
          </span>
        </div>
      </div>

      <p className="text-[11px] text-foreground-muted leading-relaxed">
        지연 시세 기반 참고 지표입니다. 매매 지시가 아니며 투자 판단과 책임은 본인에게 있습니다.
      </p>
    </div>
  );
}
