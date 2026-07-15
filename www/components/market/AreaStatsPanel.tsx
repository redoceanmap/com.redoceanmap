"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3, Gauge, Store, TrendingUp, Users } from "lucide-react";
import { fetchAreaStats } from "@/lib/api";
import type { QuarterStat } from "@/lib/types";
import AreaScoreCard from "./AreaScoreCard";
import SalesTrendChart from "./SalesTrendChart";
import PopulationCharts from "./PopulationCharts";
import StorePanel from "./StorePanel";

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: typeof TrendingUp;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h3 className="flex items-center gap-1.5 text-xs font-semibold text-foreground-muted uppercase tracking-wide mb-2">
        <Icon size={13} strokeWidth={2} />
        {title}
      </h3>
      {children}
    </section>
  );
}

// 상권 자료 패널 — ?trdar 를 키로 원시 수치 API를 조회해 차트를 그린다
export default function AreaStatsPanel({ trdarCode }: { trdarCode: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["area-stats", trdarCode],
    queryFn: () => fetchAreaStats(trdarCode),
    enabled: !!trdarCode,
  });

  if (!trdarCode) {
    return (
      <p className="p-4 text-sm text-foreground-muted">
        지도에서 상권을 선택하거나 채팅으로 추천받으면 통계가 표시됩니다.
      </p>
    );
  }
  if (isLoading) {
    return (
      <div className="p-4 flex flex-col gap-3">
        <div className="skeleton h-6 w-2/3 rounded-md" />
        <div className="skeleton h-40 rounded-xl" />
        <div className="skeleton h-32 rounded-xl" />
        <div className="skeleton h-24 rounded-xl" />
      </div>
    );
  }
  if (isError || !data) {
    return <p className="p-4 text-sm text-foreground-muted">상권 통계를 불러오지 못했습니다.</p>;
  }

  return (
    <div className="p-4 flex flex-col gap-5">
      <div>
        <p className="text-xs text-foreground-muted">{data.districtName}</p>
        <h2 className="text-base font-semibold mt-0.5">{data.trdarName}</h2>
        {data.serviceName && (
          <p className="text-xs text-foreground-muted mt-1">
            기준 업종 <span className="font-medium text-foreground">{data.serviceName}</span>
            {" · "}서울시 상권분석서비스
          </p>
        )}
      </div>

      <Section icon={Gauge} title="상권 종합점수">
        <AreaScoreCard trdarCode={trdarCode} />
      </Section>

      <Section icon={TrendingUp} title="분기 매출 추이">
        <SalesTrendChart series={data.series} />
      </Section>

      <Section icon={Users} title="유동인구 (최신 분기)">
        <PopulationCharts latest={data.latest} />
      </Section>

      <Section icon={Store} title="점포 현황">
        <StorePanel series={data.series} latest={data.latest} />
      </Section>

      <Section icon={BarChart3} title="유동인구 추이">
        <FloatingTrend series={data.series} />
      </Section>
    </div>
  );
}

function FloatingTrend({ series }: { series: QuarterStat[] }) {
  const points = series.filter((q) => q.totalFloatingPop !== null);
  if (points.length === 0) {
    return <p className="text-sm text-foreground-muted">데이터가 없습니다.</p>;
  }
  const max = Math.max(...points.map((q) => q.totalFloatingPop as number));
  return (
    <div className="flex items-end gap-2 h-20">
      {points.map((q) => (
        <div key={q.yearQuarter} className="flex-1 flex flex-col items-center gap-1">
          <div
            className="w-full max-w-10 bg-brand/70 rounded-t"
            style={{ height: `${Math.max(8, ((q.totalFloatingPop as number) / max) * 100)}%` }}
            title={`${(q.totalFloatingPop as number).toLocaleString("ko-KR")}명`}
          />
          <span className="text-[10px] text-foreground-muted">
            {String(q.yearQuarter).slice(4)}Q
          </span>
        </div>
      ))}
    </div>
  );
}
