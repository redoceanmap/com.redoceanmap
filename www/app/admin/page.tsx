import Link from "next/link";
import { TrendingUp, TrendingDown, Store, Users, Sparkles, Database } from "lucide-react";

/* ────────────────────────── 목 데이터 ────────────────────────── */

const kpis = [
  { icon: Store, label: "등록 상권", value: "1,742", ring: 74, delta: 4.2, up: true },
  { icon: Users, label: "활성 회원", value: "8,316", ring: 88, delta: 12.8, up: true },
  { icon: Sparkles, label: "오늘 추천", value: "124", ring: 61, delta: 6.1, up: true },
  { icon: Database, label: "데이터 신선도", value: "92%", ring: 92, delta: 1.4, up: false },
];

// 최근 12개월 추천 건수
const trend = [320, 410, 380, 520, 610, 540, 720, 690, 810, 760, 880, 940];
const trendMonths = ["7", "8", "9", "10", "11", "12", "1", "2", "3", "4", "5", "6"];

const categories = [
  { name: "음식점", pct: 32 },
  { name: "카페·디저트", pct: 24 },
  { name: "소매·판매", pct: 18 },
  { name: "생활서비스", pct: 14 },
  { name: "기타", pct: 12 },
];

const areas = [
  { name: "강남역", gu: "강남구", stores: "2,011", closure: "4.8%", status: "활성" },
  { name: "홍대입구역", gu: "마포구", stores: "1,284", closure: "6.2%", status: "활성" },
  { name: "성수동 카페거리", gu: "성동구", stores: "642", closure: "5.1%", status: "주의" },
  { name: "연남동", gu: "마포구", stores: "511", closure: "5.5%", status: "활성" },
  { name: "망원시장", gu: "마포구", stores: "388", closure: "7.9%", status: "주의" },
];

const sources = [
  { name: "서울 열린데이터광장", note: "상권·점포 현황", state: "동기화됨" },
  { name: "소상공인시장진흥공단", note: "상가업소 데이터", state: "동기화됨" },
  { name: "추정매출 파이프라인", note: "85,732행", state: "동기화됨" },
  { name: "국토부 실거래가", note: "임대료 추정", state: "대기" },
];

const activity = [
  { who: "추천엔진", what: "‘성수동 카페거리’ 추천 124건 생성", when: "방금" },
  { who: "데이터봇", what: "추정매출 파이프라인 동기화 완료", when: "12분 전" },
  { who: "김지은", what: "신규 회원 가입 (카카오)", when: "31분 전" },
  { who: "운영자", what: "‘망원시장’ 상태를 주의로 변경", when: "1시간 전" },
];

/* ────────────────────────── 작은 차트 ────────────────────────── */

function Ring({ pct }: { pct: number }) {
  const r = 18;
  const c = 2 * Math.PI * r;
  return (
    <svg viewBox="0 0 44 44" className="w-11 h-11 -rotate-90">
      <circle cx="22" cy="22" r={r} fill="none" stroke="currentColor" strokeWidth="4" className="text-brand/10" />
      <circle
        cx="22"
        cy="22"
        r={r}
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={c * (1 - pct / 100)}
        className="text-brand"
      />
    </svg>
  );
}

function AreaTrend() {
  const w = 560;
  const h = 180;
  const pad = 8;
  const max = Math.max(...trend);
  const min = Math.min(...trend);
  const xs = (i: number) => pad + (i * (w - pad * 2)) / (trend.length - 1);
  const ys = (v: number) => h - pad - ((v - min) / (max - min)) * (h - pad * 2);
  const line = trend.map((v, i) => `${i === 0 ? "M" : "L"}${xs(i)},${ys(v)}`).join(" ");
  const fill = `${line} L${xs(trend.length - 1)},${h} L${xs(0)},${h} Z`;

  return (
    <div>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-44" preserveAspectRatio="none">
        <defs>
          <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#991B1B" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#991B1B" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={fill} fill="url(#trendFill)" />
        <path d={line} fill="none" stroke="#991B1B" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
        {trend.map((v, i) => (
          <circle key={i} cx={xs(i)} cy={ys(v)} r="2.5" fill="#991B1B" />
        ))}
      </svg>
      <div className="mt-2 flex justify-between text-[11px] text-foreground-muted">
        {trendMonths.map((m) => (
          <span key={m}>{m}월</span>
        ))}
      </div>
    </div>
  );
}

/* ────────────────────────── 페이지 ────────────────────────── */

export default function AdminDashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-5">
      {/* 헤더 */}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">대시보드</h1>
          <p className="mt-1 text-sm text-foreground-muted">
            서울 상권 분석 서비스 현황 · 2026년 6월
          </p>
        </div>
        <button
          type="button"
          className="hidden sm:inline-flex items-center px-4 h-10 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors"
        >
          리포트 내보내기
        </button>
      </div>

      {/* KPI 카드 — 모바일 2열 → lg 4열 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {kpis.map(({ icon: Icon, label, value, ring, delta, up }) => (
          <div key={label} className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <div className="flex items-start justify-between">
              <span className="grid place-items-center w-9 h-9 rounded-xl bg-brand/10 text-brand">
                <Icon size={17} strokeWidth={1.9} />
              </span>
              <Ring pct={ring} />
            </div>
            <p className="mt-3 text-2xl font-bold tracking-tight">{value}</p>
            <div className="mt-0.5 flex items-center gap-1.5 text-xs">
              <span className="text-foreground-muted">{label}</span>
              <span className={`ml-auto inline-flex items-center gap-0.5 font-medium ${up ? "text-emerald-600" : "text-foreground-muted"}`}>
                {up ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {delta}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 메인 그리드 — 모바일 1열 → lg 3열(2:1) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5">
        {/* 좌측 2/3 */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-5">
          {/* 추천 추이 */}
          <section className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold">추천 추이</h2>
                <p className="text-xs text-foreground-muted mt-0.5">최근 12개월 AI 추천 건수</p>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-full bg-brand/5 text-brand font-medium">+33.4%</span>
            </div>
            <div className="mt-4">
              <AreaTrend />
            </div>
          </section>

          {/* 인기 업종 분포 */}
          <section className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <h2 className="font-semibold">인기 업종 분포</h2>
            <p className="text-xs text-foreground-muted mt-0.5">추천된 상권의 주력 업종</p>
            <div className="mt-4 space-y-3">
              {categories.map((c) => (
                <div key={c.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-foreground/80">{c.name}</span>
                    <span className="font-medium tabular-nums">{c.pct}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-brand/10 overflow-hidden">
                    <div className="h-full rounded-full bg-brand" style={{ width: `${c.pct * 2.6}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 상권 목록 */}
          <section className="rounded-2xl bg-surface border border-border overflow-hidden">
            <div className="p-4 sm:p-5 flex items-center justify-between">
              <h2 className="font-semibold">상권 현황</h2>
              <Link href="/admin/areas" className="text-xs text-brand font-medium hover:underline">전체 보기</Link>
            </div>
            {/* 모바일: 카드형 / 데스크톱: 테이블 */}
            <div className="hidden sm:block">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-foreground-muted border-y border-border bg-background/60">
                    <th className="font-medium px-5 py-2.5">상권</th>
                    <th className="font-medium px-5 py-2.5">자치구</th>
                    <th className="font-medium px-5 py-2.5 text-right">점포수</th>
                    <th className="font-medium px-5 py-2.5 text-right">폐업률</th>
                    <th className="font-medium px-5 py-2.5 text-right">상태</th>
                  </tr>
                </thead>
                <tbody>
                  {areas.map((a) => (
                    <tr key={a.name} className="border-b border-border last:border-0">
                      <td className="px-5 py-3 font-medium">{a.name}</td>
                      <td className="px-5 py-3 text-foreground-muted">{a.gu}</td>
                      <td className="px-5 py-3 text-right tabular-nums">{a.stores}</td>
                      <td className="px-5 py-3 text-right tabular-nums">{a.closure}</td>
                      <td className="px-5 py-3 text-right">
                        <StatusBadge status={a.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="sm:hidden divide-y divide-border border-t border-border">
              {areas.map((a) => (
                <div key={a.name} className="px-4 py-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{a.name}</p>
                    <p className="text-xs text-foreground-muted mt-0.5">
                      {a.gu} · 점포 {a.stores} · 폐업 {a.closure}
                    </p>
                  </div>
                  <StatusBadge status={a.status} />
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* 우측 1/3 */}
        <div className="space-y-4 sm:space-y-5">
          {/* 데이터 소스 현황 */}
          <section className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <h2 className="font-semibold">데이터 소스</h2>
            <div className="mt-4 space-y-3">
              {sources.map((s) => (
                <div key={s.name} className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full shrink-0 ${s.state === "동기화됨" ? "bg-emerald-500" : "bg-amber-400"}`} />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{s.name}</p>
                    <p className="text-xs text-foreground-muted">{s.note}</p>
                  </div>
                  <span className={`text-xs font-medium ${s.state === "동기화됨" ? "text-emerald-600" : "text-amber-600"}`}>
                    {s.state}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* 최근 활동 */}
          <section className="rounded-2xl bg-surface border border-border p-4 sm:p-5">
            <h2 className="font-semibold">최근 활동</h2>
            <ol className="mt-4 space-y-4">
              {activity.map((a, i) => (
                <li key={i} className="relative flex gap-3">
                  <span className="grid place-items-center w-8 h-8 rounded-full bg-brand/10 text-brand text-xs font-semibold shrink-0">
                    {a.who[0]}
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm leading-snug">{a.what}</p>
                    <p className="text-xs text-foreground-muted mt-0.5">{a.who} · {a.when}</p>
                  </div>
                </li>
              ))}
            </ol>
          </section>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const active = status === "활성";
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
        active ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
      }`}
    >
      {status}
    </span>
  );
}
