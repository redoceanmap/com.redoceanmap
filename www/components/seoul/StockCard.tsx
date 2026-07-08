import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { StockAnalysis } from "@/lib/store";

const DIRECTION_META = {
  UP: { label: "상승 신호", icon: TrendingUp, className: "text-red-600 bg-red-50 border-red-200" },
  DOWN: { label: "하락 신호", icon: TrendingDown, className: "text-blue-600 bg-blue-50 border-blue-200" },
  NEUTRAL: { label: "중립", icon: Minus, className: "text-foreground-muted bg-surface border-border" },
} as const;

function formatPrice(v: number) {
  return v.toLocaleString("ko-KR", { maximumFractionDigits: 2 });
}

export default function StockCard({ stock }: { stock: StockAnalysis }) {
  const meta = DIRECTION_META[stock.direction] ?? DIRECTION_META.NEUTRAL;
  const DirectionIcon = meta.icon;

  const stats: [string, string][] = [
    ["RSI(14)", stock.rsi.toFixed(1)],
    ["뉴스 감성", stock.sentimentLabel],
    ["20일 이평", formatPrice(stock.ma20)],
    ["50일 이평", formatPrice(stock.ma50)],
    ["지지선", formatPrice(stock.support)],
    ["저항선", formatPrice(stock.resistance)],
  ];

  return (
    <div className="mt-4 bg-surface border border-border rounded-lg p-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <div className="text-sm font-semibold">{stock.symbol}</div>
          <div className="text-lg font-bold mt-0.5">{formatPrice(stock.price)}</div>
        </div>
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full border text-xs font-medium ${meta.className}`}
        >
          <DirectionIcon size={13} strokeWidth={2} />
          {meta.label} · 확신도 {Math.round(stock.confidence * 100)}%
        </span>
      </div>

      <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-2">
        {stats.map(([label, value]) => (
          <div key={label} className="bg-background border border-border rounded-md px-2.5 py-2">
            <div className="text-[11px] text-foreground-muted">{label}</div>
            <div className="text-sm font-medium mt-0.5">{value}</div>
          </div>
        ))}
      </div>

      {stock.headlines.length > 0 && (
        <ul className="mt-3 flex flex-col gap-1">
          {stock.headlines.slice(0, 3).map((h) => (
            <li key={h} className="text-xs text-foreground/80 leading-snug truncate">
              · {h}
            </li>
          ))}
        </ul>
      )}

      <p className="mt-3 text-[11px] text-foreground-muted">
        지연 시세 기반 참고 지표입니다. 투자 판단과 책임은 본인에게 있습니다.
      </p>
    </div>
  );
}
