import { ChevronDown } from "lucide-react";
import type { StockForecast } from "@/lib/types";
import InsightList from "@/components/common/InsightList";

const DIRECTION_LABEL = { UP: "상승 신호", DOWN: "하락 신호", NEUTRAL: "중립 신호" } as const;

// 백테스트 실측 기반 상승 확률 — 표본·신뢰구간·기준선·고지 병기(확률 단정 금지 정책)
export default function ProbabilityCard({ forecast }: { forecast: StockForecast }) {
  const p = forecast.probability;
  if (!p) return null;
  const upPct = Math.round(p.up_rate * 100);
  const basePct = Math.round(p.baseline_up_rate * 100);

  return (
    <div className="shrink-0 px-4 py-2.5 border-b border-border">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <div className="flex items-baseline gap-1.5">
          <span className="text-[11px] text-foreground-muted">
            {forecast.horizon_days}일 뒤 상승 확률
          </span>
          <span className={`text-xl font-bold ${upPct >= basePct ? "text-red-600" : "text-blue-600"}`}>
            {upPct}%
          </span>
        </div>
        <span className="text-[11px] text-foreground-muted">
          과거 같은 {DIRECTION_LABEL[forecast.signal_direction]} {p.sample_size}회 중 {p.hits}회 상승
          {" · "}95% 구간 {Math.round(p.ci_low * 100)}~{Math.round(p.ci_high * 100)}%
          {" · "}평소 상승률 {basePct}%
        </span>
        {!p.ready && (
          <span className="px-2 py-0.5 rounded-full border border-amber-200 bg-amber-50 text-amber-700 text-[10px] font-medium">
            참고용 (표본 부족)
          </span>
        )}
      </div>
      <details className="mt-1 group">
        <summary className="flex items-center gap-1 text-[11px] text-foreground-muted cursor-pointer list-none select-none">
          <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
          근거 보기 — 과거 통계이며 미래를 보장하지 않습니다
        </summary>
        <div className="mt-1.5 pl-1">
          <InsightList insights={forecast.insights} />
        </div>
      </details>
    </div>
  );
}
