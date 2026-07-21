"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { fetchAdminRecommendations } from "@/lib/adminApi";
import BlockSkeleton from "@/components/admin/BlockSkeleton";
import Empty from "@/components/admin/Empty";
import Kpi from "@/components/admin/Kpi";

export default function RecommendationsPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["admin-recommendations"],
    queryFn: () => fetchAdminRecommendations(50),
  });

  const items = data?.items ?? [];

  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">추천 기록</h1>
        <p className="mt-1 text-sm text-foreground-muted">AI 상권 추천 로그 (최근 50건)</p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-md">
        <Kpi label="오늘 추천" value={data ? data.today.toLocaleString() : "—"} />
        <Kpi label="누적 추천" value={data ? data.total.toLocaleString() : "—"} />
      </div>

      <section className="rounded-2xl bg-surface border border-border overflow-hidden">
        {isPending && <BlockSkeleton rows={5} />}
        {isError && <Empty msg="추천 기록을 불러오지 못했습니다." />}
        {!isPending && !isError && items.length === 0 && <Empty msg="아직 추천 기록이 없습니다." />}
        {items.length > 0 && (
          <>
            <div className="hidden sm:block">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-foreground-muted border-b border-border bg-background/60">
                    <th className="font-medium px-5 py-2.5">추천 상권</th>
                    <th className="font-medium px-5 py-2.5">자치구</th>
                    <th className="font-medium px-5 py-2.5">업종</th>
                    <th className="font-medium px-5 py-2.5">사유</th>
                    <th className="font-medium px-5 py-2.5 text-right">시각</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((l) => (
                    <tr key={l.id} className="border-b border-border last:border-0 hover:bg-background/40">
                      <td className="px-5 py-3">
                        <Link
                          href={`/market?trdar=${l.trdar_code}`}
                          className="inline-flex items-center gap-1.5 text-brand font-medium hover:underline"
                          title="서비스 지도에서 열기"
                        >
                          <Sparkles size={13} /> {l.trdar_name}
                        </Link>
                      </td>
                      <td className="px-5 py-3 text-foreground-muted">{l.district_name}</td>
                      <td className="px-5 py-3 text-foreground-muted">{l.category}</td>
                      <td className="px-5 py-3 text-foreground-muted max-w-xs truncate" title={l.reason}>
                        {l.reason}
                      </td>
                      <td className="px-5 py-3 text-right text-foreground-muted tabular-nums whitespace-nowrap">
                        {l.created_at.slice(0, 16).replace("T", " ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="sm:hidden divide-y divide-border">
              {items.map((l) => (
                <div key={l.id} className="px-4 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <Link
                      href={`/market?trdar=${l.trdar_code}`}
                      className="inline-flex items-center gap-1.5 text-brand font-medium text-sm hover:underline"
                    >
                      <Sparkles size={13} /> {l.trdar_name}
                    </Link>
                    <span className="text-xs text-foreground-muted tabular-nums">
                      {l.created_at.slice(0, 10)}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-foreground-muted">
                    {l.district_name} · {l.category}
                  </p>
                  <p className="mt-1 text-xs text-foreground-muted line-clamp-2">{l.reason}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
