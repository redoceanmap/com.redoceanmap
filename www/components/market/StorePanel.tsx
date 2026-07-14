"use client";

import type { AreaStatsDetail, QuarterStat } from "@/lib/types";

// series 마지막 분기(최신) 점포 팩트 + 변화지표 요약
export default function StorePanel({
  series,
  latest,
}: {
  series: QuarterStat[];
  latest: AreaStatsDetail["latest"];
}) {
  const recent = [...series].reverse().find((q) => q.storeCount !== null);

  const stats: [string, string][] = recent
    ? [
        ["영업 점포", `${recent.storeCount}개`],
        ["프랜차이즈", recent.franchiseCount !== null ? `${recent.franchiseCount}개` : "—"],
        ["개업률", recent.openingRate !== null ? `${recent.openingRate}%` : "—"],
        ["폐업률", recent.closureRate !== null ? `${recent.closureRate}%` : "—"],
      ]
    : [];

  return (
    <div className="flex flex-col gap-2">
      {stats.length > 0 ? (
        <div className="grid grid-cols-2 gap-2">
          {stats.map(([label, value]) => (
            <div key={label} className="bg-surface border border-border rounded-lg px-3 py-2.5">
              <div className="text-[11px] text-foreground-muted">{label}</div>
              <div className="text-sm font-semibold mt-0.5">{value}</div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-foreground-muted">점포 데이터가 없습니다.</p>
      )}

      {(latest.changeIndicator || latest.operatingMonthsAvg !== null) && (
        <div className="bg-surface border border-border rounded-lg px-3 py-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-foreground-muted">상권 변화</span>
            {latest.changeIndicator && (
              <span className="text-[11px] font-medium px-1.5 py-0.5 rounded border border-brand/30 bg-brand/5 text-brand">
                {latest.changeIndicator}
              </span>
            )}
          </div>
          {latest.operatingMonthsAvg !== null && (
            <p className="text-sm font-semibold mt-1">
              평균 운영 {Math.round(latest.operatingMonthsAvg)}개월
              {latest.regionOperatingMonthsAvg !== null && (
                <span className="text-xs font-normal text-foreground-muted">
                  {" "}
                  · 시도 평균 {Math.round(latest.regionOperatingMonthsAvg)}개월
                </span>
              )}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
