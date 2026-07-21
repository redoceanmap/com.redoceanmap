"use client";

import Link from "next/link";
import { Lock } from "lucide-react";
import { useVisibleTabs, type TabKey } from "@/lib/useVisibleTabs";

/**
 * 등급 게이팅 라우트 가드 — 탭을 숨겨도 URL 직접 접근이 가능하므로 안내 카드로 막는다.
 * 실보안 경계가 아니라 UX 장치다(AdminGuard와 동일한 원칙 — 데이터 API는 기존 인증 유지).
 */
export default function TabGuard({ tab, children }: { tab: TabKey; children: React.ReactNode }) {
  const tabs = useVisibleTabs();

  if (tabs === null) return null; // 로딩 중 — 콘텐츠 깜빡임 방지

  if (!tabs.has(tab)) {
    return (
      <div className="min-h-[60vh] grid place-items-center p-6">
        <div className="max-w-sm w-full rounded-2xl bg-surface border border-border p-8 text-center">
          <span className="mx-auto grid place-items-center w-12 h-12 rounded-full bg-brand/10 text-brand">
            <Lock size={22} strokeWidth={1.9} />
          </span>
          <h1 className="mt-4 text-lg font-bold tracking-tight">
            현재 등급에서는 이용할 수 없는 기능입니다
          </h1>
          <p className="mt-2 text-sm text-foreground-muted leading-relaxed">
            이 기능은 다른 등급에서 제공됩니다. 이용이 필요하면 관리자에게 문의하세요.
          </p>
          <Link
            href="/"
            className="mt-6 inline-flex items-center px-5 h-10 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors"
          >
            홈으로 가기
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
