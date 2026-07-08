"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Store,
  Users,
  Sparkles,
  Database,
  Settings,
  Search,
  Bell,
} from "lucide-react";

const nav = [
  { icon: LayoutDashboard, label: "대시보드", href: "/admin" },
  { icon: Store, label: "상권 관리", href: "/admin/areas" },
  { icon: Users, label: "회원 관리", href: "/admin/members" },
  { icon: Sparkles, label: "추천 기록", href: "/admin/recommendations" },
  { icon: Database, label: "데이터 소스", href: "/admin/data-sources" },
  { icon: Settings, label: "설정", href: "/admin/settings" },
];

// 모바일 하단 탭 (주요 5개)
const mobileTabs = nav.slice(0, 5);

export default function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = (href: string) =>
    href === "/admin" ? pathname === "/admin" : pathname.startsWith(href);

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      {/* 데스크톱 사이드바 */}
      <aside className="hidden lg:flex flex-col w-60 shrink-0 border-r border-border bg-surface">
        <div className="h-16 flex items-center gap-2 px-5 border-b border-border">
          <span className="grid place-items-center w-7 h-7 rounded-lg bg-brand text-white">
            <Store size={15} strokeWidth={2} />
          </span>
          <span className="font-semibold tracking-tight">redocean 어드민</span>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {nav.map(({ icon: Icon, label, href }) => (
            <Link
              key={label}
              href={href}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors ${
                isActive(href)
                  ? "bg-brand text-white shadow-sm"
                  : "text-foreground/70 hover:bg-black/5 hover:text-foreground"
              }`}
            >
              <Icon size={17} strokeWidth={1.9} />
              {label}
            </Link>
          ))}
        </nav>

        <div className="m-3 p-4 rounded-2xl bg-brand/5 border border-brand/10">
          <p className="text-sm font-semibold text-brand">데이터 파이프라인</p>
          <p className="mt-1 text-xs text-foreground-muted leading-relaxed">
            추정매출 85,732행 동기화 완료. 다음 갱신까지 6일.
          </p>
        </div>
      </aside>

      {/* 본문 컬럼 */}
      <div className="flex-1 min-w-0 flex flex-col">
        {/* 상단바 */}
        <header className="sticky top-0 z-30 h-16 flex items-center gap-3 px-4 sm:px-6 border-b border-border bg-surface/90 backdrop-blur-md">
          <div className="lg:hidden flex items-center gap-2">
            <span className="grid place-items-center w-7 h-7 rounded-lg bg-brand text-white">
              <Store size={15} strokeWidth={2} />
            </span>
            <span className="font-semibold tracking-tight text-[15px]">어드민</span>
          </div>

          <label className="hidden sm:flex items-center gap-2 flex-1 max-w-md ml-1 px-3.5 h-10 rounded-full bg-background border border-border text-sm">
            <Search size={16} className="text-foreground-muted shrink-0" />
            <input
              name="search"
              placeholder="상권, 회원, 업종 검색"
              className="bg-transparent outline-none flex-1 placeholder:text-foreground-muted"
            />
          </label>

          <div className="ml-auto flex items-center gap-2 sm:gap-3">
            <button
              type="button"
              className="relative grid place-items-center w-10 h-10 rounded-full hover:bg-black/5 transition-colors"
            >
              <Bell size={18} strokeWidth={1.8} />
              <span className="absolute top-2.5 right-2.5 w-1.5 h-1.5 rounded-full bg-brand" />
            </button>
            <div className="flex items-center gap-2.5">
              <span className="grid place-items-center w-9 h-9 rounded-full bg-brand/10 text-brand text-sm font-semibold">
                장
              </span>
              <div className="hidden sm:block leading-tight">
                <p className="text-sm font-medium">장민석</p>
                <p className="text-xs text-foreground-muted">운영자</p>
              </div>
            </div>
          </div>
        </header>

        {/* 페이지 콘텐츠 */}
        <main className="flex-1 p-4 sm:p-6 pb-24 lg:pb-8">{children}</main>
      </div>

      {/* 모바일 하단 탭 */}
      <nav
        className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-border"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        <div className="flex items-center h-16">
          {mobileTabs.map(({ icon: Icon, label, href }) => {
            const active = isActive(href);
            return (
              <Link
                key={label}
                href={href}
                className={`flex-1 flex flex-col items-center justify-center gap-1 py-2 transition-colors ${
                  active ? "text-brand" : "text-foreground-muted"
                }`}
              >
                <Icon size={21} strokeWidth={active ? 2.2 : 1.75} />
                <span className="text-[10px] font-medium">{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
