import { Search, UserPlus, TrendingUp } from "lucide-react";

const kpis = [
  { label: "전체 회원", value: "8,316", delta: "+12.8%" },
  { label: "이번 달 신규", value: "642", delta: "+8.1%" },
  { label: "활성 (30일)", value: "5,107", delta: "+4.5%" },
  { label: "이탈 위험", value: "218", delta: "-2.3%" },
];

const members = [
  { name: "김지은", email: "jieun.k@gmail.com", via: "카카오", joined: "2026-06-18", uses: 14, status: "활성" },
  { name: "박서준", email: "seojun@naver.com", via: "네이버", joined: "2026-06-15", uses: 7, status: "활성" },
  { name: "이도윤", email: "doyoon.lee@gmail.com", via: "구글", joined: "2026-06-12", uses: 22, status: "활성" },
  { name: "최유나", email: "yuna.c@kakao.com", via: "카카오", joined: "2026-05-30", uses: 2, status: "휴면" },
  { name: "정하준", email: "hajun@gmail.com", via: "구글", joined: "2026-05-21", uses: 41, status: "활성" },
  { name: "강민서", email: "minseo.k@naver.com", via: "네이버", joined: "2026-04-09", uses: 0, status: "휴면" },
];

export default function MembersPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">회원 관리</h1>
          <p className="mt-1 text-sm text-foreground-muted">가입 회원 및 활동 현황</p>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-4 h-10 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors"
        >
          <UserPlus size={16} /> 회원 초대
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <p className="text-2xl font-bold tracking-tight">{k.value}</p>
            <div className="mt-1 flex items-center justify-between">
              <span className="text-xs text-foreground-muted">{k.label}</span>
              <span className={`text-xs font-medium inline-flex items-center gap-0.5 ${k.delta.startsWith("-") ? "text-foreground-muted" : "text-emerald-600"}`}>
                <TrendingUp size={12} /> {k.delta}
              </span>
            </div>
          </div>
        ))}
      </div>

      <label className="flex items-center gap-2 px-3.5 h-10 rounded-full bg-surface border border-border text-sm">
        <Search size={16} className="text-foreground-muted shrink-0" />
        <input name="q" placeholder="이름 또는 이메일 검색" className="bg-transparent outline-none flex-1 placeholder:text-foreground-muted" />
      </label>

      <section className="rounded-2xl bg-surface border border-border overflow-hidden">
        <div className="hidden sm:block">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-foreground-muted border-b border-border bg-background/60">
                <th className="font-medium px-5 py-2.5">회원</th>
                <th className="font-medium px-5 py-2.5">가입 경로</th>
                <th className="font-medium px-5 py-2.5">가입일</th>
                <th className="font-medium px-5 py-2.5 text-right">추천 이용</th>
                <th className="font-medium px-5 py-2.5 text-right">상태</th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <tr key={m.email} className="border-b border-border last:border-0 hover:bg-background/40">
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">
                      <span className="grid place-items-center w-8 h-8 rounded-full bg-brand/10 text-brand text-xs font-semibold">{m.name[0]}</span>
                      <div>
                        <p className="font-medium">{m.name}</p>
                        <p className="text-xs text-foreground-muted">{m.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-foreground-muted">{m.via}</td>
                  <td className="px-5 py-3 text-foreground-muted tabular-nums">{m.joined}</td>
                  <td className="px-5 py-3 text-right tabular-nums">{m.uses}회</td>
                  <td className="px-5 py-3 text-right"><Badge status={m.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="sm:hidden divide-y divide-border">
          {members.map((m) => (
            <div key={m.email} className="px-4 py-3 flex items-center gap-3">
              <span className="grid place-items-center w-9 h-9 rounded-full bg-brand/10 text-brand text-sm font-semibold shrink-0">{m.name[0]}</span>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{m.name}</p>
                <p className="text-xs text-foreground-muted truncate">{m.email} · {m.via} · {m.uses}회</p>
              </div>
              <Badge status={m.status} />
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
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${active ? "bg-emerald-50 text-emerald-700" : "bg-foreground/5 text-foreground-muted"}`}>
      {status}
    </span>
  );
}
