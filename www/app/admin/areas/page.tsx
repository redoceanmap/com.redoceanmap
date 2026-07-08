import { Search, Plus, SlidersHorizontal } from "lucide-react";

const stats = [
  { label: "전체 상권", value: "1,742" },
  { label: "활성", value: "1,598" },
  { label: "주의", value: "144" },
];

const filters = ["전체", "강남구", "마포구", "성동구", "종로구", "용산구"];

const rows = [
  { name: "강남역", gu: "강남구", stores: "2,011", sales: "8,420만", closure: "4.8%", status: "활성" },
  { name: "홍대입구역", gu: "마포구", stores: "1,284", sales: "6,180만", closure: "6.2%", status: "활성" },
  { name: "성수동 카페거리", gu: "성동구", stores: "642", sales: "5,940만", closure: "5.1%", status: "주의" },
  { name: "연남동", gu: "마포구", stores: "511", sales: "4,210만", closure: "5.5%", status: "활성" },
  { name: "망원시장", gu: "마포구", stores: "388", sales: "2,870만", closure: "7.9%", status: "주의" },
  { name: "익선동", gu: "종로구", stores: "274", sales: "3,560만", closure: "6.0%", status: "활성" },
  { name: "경리단길", gu: "용산구", stores: "319", sales: "3,020만", closure: "8.4%", status: "주의" },
];

export default function AreasPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">상권 관리</h1>
          <p className="mt-1 text-sm text-foreground-muted">서울시 등록 상권 데이터 관리</p>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-4 h-10 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors"
        >
          <Plus size={16} /> 상권 추가
        </button>
      </div>

      {/* 요약 */}
      <div className="grid grid-cols-3 gap-3 sm:gap-4">
        {stats.map((s) => (
          <div key={s.label} className="rounded-2xl bg-surface border border-border p-4">
            <p className="text-2xl font-bold tracking-tight">{s.value}</p>
            <p className="text-xs text-foreground-muted mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* 검색 + 필터 */}
      <div className="flex items-center gap-2">
        <label className="flex items-center gap-2 flex-1 px-3.5 h-10 rounded-full bg-surface border border-border text-sm">
          <Search size={16} className="text-foreground-muted shrink-0" />
          <input name="q" placeholder="상권명 검색" className="bg-transparent outline-none flex-1 placeholder:text-foreground-muted" />
        </label>
        <button type="button" className="grid place-items-center w-10 h-10 rounded-full bg-surface border border-border text-foreground-muted hover:text-foreground transition-colors">
          <SlidersHorizontal size={16} />
        </button>
      </div>
      <div className="flex gap-2 overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0 pb-1">
        {filters.map((f, i) => (
          <button
            key={f}
            type="button"
            className={`shrink-0 px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              i === 0 ? "bg-brand text-white" : "bg-surface border border-border text-foreground/70 hover:text-foreground"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* 목록 */}
      <section className="rounded-2xl bg-surface border border-border overflow-hidden">
        <div className="hidden sm:block">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-foreground-muted border-b border-border bg-background/60">
                <th className="font-medium px-5 py-2.5">상권</th>
                <th className="font-medium px-5 py-2.5">자치구</th>
                <th className="font-medium px-5 py-2.5 text-right">점포수</th>
                <th className="font-medium px-5 py-2.5 text-right">추정매출</th>
                <th className="font-medium px-5 py-2.5 text-right">폐업률</th>
                <th className="font-medium px-5 py-2.5 text-right">상태</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((a) => (
                <tr key={a.name} className="border-b border-border last:border-0 hover:bg-background/40">
                  <td className="px-5 py-3 font-medium">{a.name}</td>
                  <td className="px-5 py-3 text-foreground-muted">{a.gu}</td>
                  <td className="px-5 py-3 text-right tabular-nums">{a.stores}</td>
                  <td className="px-5 py-3 text-right tabular-nums">{a.sales}</td>
                  <td className="px-5 py-3 text-right tabular-nums">{a.closure}</td>
                  <td className="px-5 py-3 text-right"><Badge status={a.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="sm:hidden divide-y divide-border">
          {rows.map((a) => (
            <div key={a.name} className="px-4 py-3 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="font-medium">{a.name}</p>
                <p className="text-xs text-foreground-muted mt-0.5">
                  {a.gu} · 점포 {a.stores} · 매출 {a.sales} · 폐업 {a.closure}
                </p>
              </div>
              <Badge status={a.status} />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Badge({ status }: { status: string }) {
  const active = status === "활성";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${active ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
      {status}
    </span>
  );
}
