"use client";

import { useQuery } from "@tanstack/react-query";
import { Database } from "lucide-react";
import { fetchAdminDataSources, formatLatestLabel } from "@/lib/adminApi";
import BlockSkeleton from "@/components/admin/BlockSkeleton";
import Empty from "@/components/admin/Empty";

// 데이터셋 key → 부가 설명 (수집 경로는 백엔드/cron 소관 — 어드민은 열람만)
const NOTES: Record<string, string> = {
  trade_area: "서울 열린데이터광장 · 상권 차원",
  estimated_sales: "서울 열린데이터광장 · 분기 팩트",
  store: "서울 열린데이터광장 · 분기 팩트",
  floating_population: "서울 열린데이터광장 · 분기 팩트",
  market_news: "Google News RSS · 일 단위 수집",
  recommendations: "AI 추천 파이프라인 산출물",
  price_bars: "yfinance OHLCV · 자동 수집",
};

export default function DataSourcesPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["admin-data-sources"],
    queryFn: fetchAdminDataSources,
  });

  const datasets = data?.datasets ?? [];

  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">데이터 소스</h1>
        <p className="mt-1 text-sm text-foreground-muted">
          데이터셋별 적재 현황 (수집은 스크립트·자동화 파이프라인이 수행)
        </p>
      </div>

      {isPending && <BlockSkeleton rows={4} />}
      {isError && <Empty msg="적재 현황을 불러오지 못했습니다." />}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {datasets.map((d) => (
          <div key={d.key} className="rounded-2xl bg-surface border border-border p-5">
            <div className="flex items-start gap-3">
              <span className="grid place-items-center w-10 h-10 rounded-xl bg-brand/10 text-brand shrink-0">
                <Database size={18} strokeWidth={1.9} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-semibold truncate">{d.name}</p>
                <p className="text-xs text-foreground-muted">{NOTES[d.key] ?? d.key}</p>
              </div>
              <span
                className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                  d.row_count > 0
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-foreground/5 text-foreground-muted"
                }`}
              >
                {d.row_count > 0 ? "적재됨" : "비어 있음"}
              </span>
            </div>

            <div className="mt-4 flex items-center justify-between text-sm">
              <span className="text-foreground-muted">레코드</span>
              <span className="font-medium tabular-nums">{d.row_count.toLocaleString()} 행</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-sm">
              <span className="text-foreground-muted">최신 시점</span>
              <span className="font-medium tabular-nums">{formatLatestLabel(d.latest_label)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
