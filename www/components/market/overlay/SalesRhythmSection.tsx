import type { AreaDetail } from "@/lib/types";
import { formatMoney } from "./format";

const DAY_LABELS: [string, string][] = [
  ["mon", "월"], ["tue", "화"], ["wed", "수"], ["thu", "목"],
  ["fri", "금"], ["sat", "토"], ["sun", "일"],
];
const TIME_LABELS: [string, string][] = [
  ["t00_06", "0-6"], ["t06_11", "6-11"], ["t11_14", "11-14"],
  ["t14_17", "14-17"], ["t17_21", "17-21"], ["t21_24", "21-24"],
];

// 값 비례 배경 농도의 1행 히트스트립 — 요일·시간대는 각각 실측(교차 데이터 없음)
function HeatStrip({ entries, values }: { entries: [string, string][]; values: Record<string, number> }) {
  const total = entries.reduce((sum, [key]) => sum + (values[key] ?? 0), 0);
  const max = Math.max(...entries.map(([key]) => values[key] ?? 0));
  if (total <= 0 || max <= 0) return null;
  return (
    <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${entries.length}, 1fr)` }}>
      {entries.map(([key, label]) => {
        const v = values[key] ?? 0;
        const share = Math.round((v / total) * 100);
        const intensity = 0.08 + (v / max) * 0.72;
        return (
          <div
            key={key}
            className="rounded-md py-1.5 text-center"
            style={{ backgroundColor: `rgba(153, 27, 27, ${intensity})` }}
            title={`${label}: ${formatMoney(v)} (${share}%)`}
          >
            <p className={`text-[10px] leading-tight ${intensity > 0.45 ? "text-white/80" : "text-foreground-muted"}`}>
              {label}
            </p>
            <p className={`text-xs font-semibold leading-tight ${intensity > 0.45 ? "text-white" : "text-foreground"}`}>
              {share}%
            </p>
          </div>
        );
      })}
    </div>
  );
}

export default function SalesRhythmSection({ salesMix }: { salesMix: NonNullable<AreaDetail["salesMix"]> }) {
  const weekTotal = salesMix.weekdayAmount + salesMix.weekendAmount;
  const weekendPct = weekTotal > 0 ? Math.round((salesMix.weekendAmount / weekTotal) * 100) : null;

  return (
    <div className="flex flex-col gap-3">
      <div>
        <p className="text-xs text-foreground-muted mb-1.5">요일별 매출 비중</p>
        <HeatStrip entries={DAY_LABELS} values={salesMix.byDay} />
      </div>
      <div>
        <p className="text-xs text-foreground-muted mb-1.5">시간대별 매출 비중</p>
        <HeatStrip entries={TIME_LABELS} values={salesMix.byTime} />
      </div>
      {weekendPct !== null && (
        <div>
          <p className="text-xs text-foreground-muted mb-1">
            주중 {100 - weekendPct}% · 주말 {weekendPct}%
          </p>
          <div className="flex h-2 rounded-full overflow-hidden bg-border">
            <div className="bg-brand/80" style={{ width: `${100 - weekendPct}%` }} />
            <div className="bg-brand/40" style={{ width: `${weekendPct}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}
