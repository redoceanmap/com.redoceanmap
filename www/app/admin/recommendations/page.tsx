import { Sparkles, Search } from "lucide-react";

const kpis = [
  { label: "오늘 추천", value: "124" },
  { label: "이번 주", value: "812" },
  { label: "평균 응답", value: "2.4초" },
  { label: "전환율", value: "18.6%" },
];

const logs = [
  { user: "김지은", budget: "5,000만", category: "카페", area: "성수동 카페거리", at: "방금", status: "완료" },
  { user: "박서준", budget: "1억 2,000만", category: "음식점", area: "강남역", at: "6분 전", status: "완료" },
  { user: "이도윤", budget: "3,000만", category: "소매", area: "연남동", at: "18분 전", status: "완료" },
  { user: "최유나", budget: "8,000만", category: "주점", area: "경리단길", at: "42분 전", status: "완료" },
  { user: "정하준", budget: "2,000만", category: "디저트", area: "익선동", at: "1시간 전", status: "실패" },
  { user: "강민서", budget: "1억", category: "음식점", area: "홍대입구역", at: "2시간 전", status: "완료" },
];

export default function RecommendationsPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">추천 기록</h1>
        <p className="mt-1 text-sm text-foreground-muted">AI 상권 추천 로그 및 성능</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <p className="text-2xl font-bold tracking-tight">{k.value}</p>
            <p className="text-xs text-foreground-muted mt-0.5">{k.label}</p>
          </div>
        ))}
      </div>

      <label className="flex items-center gap-2 px-3.5 h-10 rounded-full bg-surface border border-border text-sm">
        <Search size={16} className="text-foreground-muted shrink-0" />
        <input name="q" placeholder="회원 또는 상권 검색" className="bg-transparent outline-none flex-1 placeholder:text-foreground-muted" />
      </label>

      <section className="rounded-2xl bg-surface border border-border overflow-hidden">
        <div className="hidden sm:block">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-foreground-muted border-b border-border bg-background/60">
                <th className="font-medium px-5 py-2.5">회원</th>
                <th className="font-medium px-5 py-2.5">예산</th>
                <th className="font-medium px-5 py-2.5">업종</th>
                <th className="font-medium px-5 py-2.5">추천 상권</th>
                <th className="font-medium px-5 py-2.5">시각</th>
                <th className="font-medium px-5 py-2.5 text-right">결과</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l, i) => (
                <tr key={i} className="border-b border-border last:border-0 hover:bg-background/40">
                  <td className="px-5 py-3 font-medium">{l.user}</td>
                  <td className="px-5 py-3 text-foreground-muted tabular-nums">{l.budget}</td>
                  <td className="px-5 py-3 text-foreground-muted">{l.category}</td>
                  <td className="px-5 py-3">
                    <span className="inline-flex items-center gap-1.5 text-brand">
                      <Sparkles size={13} /> {l.area}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-foreground-muted">{l.at}</td>
                  <td className="px-5 py-3 text-right"><Badge status={l.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="sm:hidden divide-y divide-border">
          {logs.map((l, i) => (
            <div key={i} className="px-4 py-3">
              <div className="flex items-center justify-between gap-3">
                <span className="font-medium">{l.user}</span>
                <Badge status={l.status} />
              </div>
              <p className="mt-1 text-xs text-foreground-muted">
                {l.budget} · {l.category} · {l.at}
              </p>
              <p className="mt-1.5 inline-flex items-center gap-1.5 text-sm text-brand">
                <Sparkles size={13} /> {l.area}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Badge({ status }: { status: string }) {
  const ok = status === "완료";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${ok ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}>
      {status}
    </span>
  );
}
