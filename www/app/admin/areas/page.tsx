"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { fetchAdminAreas, formatSalesMan, type AdminAreaRow } from "@/lib/adminApi";

// 폐업률이 이 값 이상이면 "주의" 배지 — 어드민 목록 표시용 임계값
const CLOSURE_WARN = 7;

export default function AreasPage() {
  // REACT_RULES 패턴 B: 실시간 필터 상태는 단일 객체 useState
  const [filter, setFilter] = useState({ q: "", gu: "전체" });
  const { data, isPending, isError } = useQuery({
    queryKey: ["admin-areas"],
    queryFn: fetchAdminAreas,
  });

  const areas = data?.areas ?? [];

  const guList = useMemo(
    () => ["전체", ...Array.from(new Set(areas.map((a) => a.gu_name).filter(Boolean))).sort()],
    [areas],
  );

  const rows = useMemo(
    () =>
      areas.filter(
        (a) =>
          (filter.gu === "전체" || a.gu_name === filter.gu) &&
          (!filter.q || a.trdar_name.includes(filter.q) || a.dong_name.includes(filter.q)),
      ),
    [areas, filter],
  );

  const warnCount = rows.filter(
    (a) => a.closure_rate != null && a.closure_rate >= CLOSURE_WARN,
  ).length;

  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">상권 관리</h1>
        <p className="mt-1 text-sm text-foreground-muted">서울시 등록 상권 데이터 (최신 분기 집계)</p>
      </div>

      {/* 요약 */}
      <div className="grid grid-cols-3 gap-3 sm:gap-4">
        <Stat label="전체 상권" value={areas.length.toLocaleString()} />
        <Stat label="조회 결과" value={rows.length.toLocaleString()} />
        <Stat label={`주의 (폐업률 ${CLOSURE_WARN}%↑)`} value={warnCount.toLocaleString()} />
      </div>

      {/* 검색 + 자치구 필터 */}
      <label className="flex items-center gap-2 px-3.5 h-10 rounded-full bg-surface border border-border text-sm">
        <Search size={16} className="text-foreground-muted shrink-0" />
        <input
          value={filter.q}
          onChange={(e) => setFilter((prev) => ({ ...prev, q: e.target.value }))}
          placeholder="상권명·행정동 검색"
          className="bg-transparent outline-none flex-1 placeholder:text-foreground-muted"
        />
      </label>
      <div className="flex gap-2 overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0 pb-1">
        {guList.map((gu) => (
          <button
            key={gu}
            type="button"
            onClick={() => setFilter((prev) => ({ ...prev, gu }))}
            className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter.gu === gu
                ? "bg-brand text-white"
                : "bg-surface border border-border text-foreground/70 hover:text-foreground"
            }`}
          >
            {gu}
          </button>
        ))}
      </div>

      {/* 목록 */}
      <section className="rounded-2xl bg-surface border border-border overflow-hidden">
        {isPending && <Empty msg="상권 데이터를 불러오는 중…" />}
        {isError && <Empty msg="상권 데이터를 불러오지 못했습니다." />}
        {!isPending && !isError && rows.length === 0 && <Empty msg="조건에 맞는 상권이 없습니다." />}
        {rows.length > 0 && (
          <>
            <div className="hidden sm:block max-h-[32rem] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-surface">
                  <tr className="text-left text-xs text-foreground-muted border-b border-border bg-background/60">
                    <th className="font-medium px-5 py-2.5">상권</th>
                    <th className="font-medium px-5 py-2.5">자치구</th>
                    <th className="font-medium px-5 py-2.5">행정동</th>
                    <th className="font-medium px-5 py-2.5 text-right">점포수</th>
                    <th className="font-medium px-5 py-2.5 text-right">추정매출(월)</th>
                    <th className="font-medium px-5 py-2.5 text-right">폐업률</th>
                    <th className="font-medium px-5 py-2.5 text-right">상태</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((a) => (
                    <tr key={a.trdar_code} className="border-b border-border last:border-0 hover:bg-background/40">
                      <td className="px-5 py-3 font-medium">{a.trdar_name}</td>
                      <td className="px-5 py-3 text-foreground-muted">{a.gu_name || "—"}</td>
                      <td className="px-5 py-3 text-foreground-muted">{a.dong_name || "—"}</td>
                      <td className="px-5 py-3 text-right tabular-nums">
                        {a.store_count?.toLocaleString() ?? "—"}
                      </td>
                      <td className="px-5 py-3 text-right tabular-nums">{formatSalesMan(a.monthly_sales)}</td>
                      <td className="px-5 py-3 text-right tabular-nums">
                        {a.closure_rate != null ? `${a.closure_rate.toFixed(1)}%` : "—"}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <Badge row={a} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="sm:hidden divide-y divide-border max-h-[32rem] overflow-y-auto">
              {rows.map((a) => (
                <div key={a.trdar_code} className="px-4 py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-medium">{a.trdar_name}</p>
                    <p className="text-xs text-foreground-muted mt-0.5">
                      {a.gu_name || "—"} · 점포 {a.store_count?.toLocaleString() ?? "—"} · 매출{" "}
                      {formatSalesMan(a.monthly_sales)} · 폐업{" "}
                      {a.closure_rate != null ? `${a.closure_rate.toFixed(1)}%` : "—"}
                    </p>
                  </div>
                  <Badge row={a} />
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-surface border border-border p-4">
      <p className="text-2xl font-bold tracking-tight">{value}</p>
      <p className="text-xs text-foreground-muted mt-0.5">{label}</p>
    </div>
  );
}

function Badge({ row }: { row: AdminAreaRow }) {
  if (row.closure_rate == null) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-foreground/5 text-foreground-muted">
        데이터 없음
      </span>
    );
  }
  const warn = row.closure_rate >= CLOSURE_WARN;
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
        warn ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"
      }`}
    >
      {warn ? "주의" : "활성"}
    </span>
  );
}

function Empty({ msg }: { msg: string }) {
  return <p className="p-8 text-center text-sm text-foreground-muted">{msg}</p>;
}
