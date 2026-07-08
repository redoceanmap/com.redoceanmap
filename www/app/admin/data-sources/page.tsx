import { RefreshCw, Database, CheckCircle2, Clock } from "lucide-react";

const sources = [
  { name: "서울 열린데이터광장", note: "상권·점포 현황 API", rows: "1,742 상권", last: "오늘 03:00", state: "동기화됨", freshness: 96 },
  { name: "소상공인시장진흥공단", note: "상가업소 데이터", rows: "421,330 행", last: "오늘 03:12", state: "동기화됨", freshness: 92 },
  { name: "추정매출 파이프라인", note: "Phase 1 집계", rows: "85,732 행", last: "오늘 02:40", state: "동기화됨", freshness: 100 },
  { name: "국토부 실거래가", note: "임대료 추정 보조", rows: "—", last: "6일 전", state: "대기", freshness: 41 },
];

export default function DataSourcesPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">데이터 소스</h1>
          <p className="mt-1 text-sm text-foreground-muted">공공데이터 연동 및 동기화 상태</p>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-4 h-10 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors"
        >
          <RefreshCw size={15} /> 전체 동기화
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {sources.map((s) => {
          const synced = s.state === "동기화됨";
          return (
            <div key={s.name} className="rounded-2xl bg-surface border border-border p-5">
              <div className="flex items-start gap-3">
                <span className="grid place-items-center w-10 h-10 rounded-xl bg-brand/10 text-brand shrink-0">
                  <Database size={18} strokeWidth={1.9} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold truncate">{s.name}</p>
                  <p className="text-xs text-foreground-muted">{s.note}</p>
                </div>
                <span className={`inline-flex items-center gap-1 text-xs font-medium ${synced ? "text-emerald-600" : "text-amber-600"}`}>
                  {synced ? <CheckCircle2 size={13} /> : <Clock size={13} />}
                  {s.state}
                </span>
              </div>

              <div className="mt-4 flex items-center justify-between text-sm">
                <span className="text-foreground-muted">레코드</span>
                <span className="font-medium tabular-nums">{s.rows}</span>
              </div>
              <div className="mt-2 flex items-center justify-between text-sm">
                <span className="text-foreground-muted">최근 동기화</span>
                <span className="font-medium tabular-nums">{s.last}</span>
              </div>

              <div className="mt-4">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-foreground-muted">신선도</span>
                  <span className="font-medium tabular-nums">{s.freshness}%</span>
                </div>
                <div className="h-2 rounded-full bg-brand/10 overflow-hidden">
                  <div className={`h-full rounded-full ${synced ? "bg-brand" : "bg-amber-400"}`} style={{ width: `${s.freshness}%` }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
