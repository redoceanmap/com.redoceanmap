"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ShieldAlert } from "lucide-react";
import { fetchAdminMe } from "@/lib/adminApi";

/**
 * /admin 클라이언트 가드 — 실보안 경계는 백엔드 require_permission(403)이고,
 * 여기서는 비인가자에게 콘솔 껍데기조차 보여주지 않는 UX 장치다.
 * 미인증(401 등 요청 실패)은 /로 리다이렉트, 로그인했지만 권한이 없는 사용자에게는
 * 거부 안내 화면을 보여준다(대중적 어드민의 표준 — 말없는 이동 금지).
 */
export default function AdminGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data, isError, isPending } = useQuery({
    queryKey: ["admin-me"],
    queryFn: fetchAdminMe,
    retry: false,
    staleTime: 0,
  });

  useEffect(() => {
    if (isError) router.replace("/");
  }, [isError, router]);

  if (isPending || isError) return null;

  if (data.permissions.length === 0) {
    return (
      <div className="min-h-screen grid place-items-center bg-background text-foreground p-6">
        <div className="max-w-sm w-full rounded-2xl bg-surface border border-border p-8 text-center">
          <span className="mx-auto grid place-items-center w-12 h-12 rounded-full bg-brand/10 text-brand">
            <ShieldAlert size={22} strokeWidth={1.9} />
          </span>
          <h1 className="mt-4 text-lg font-bold tracking-tight">어드민 권한이 없습니다</h1>
          <p className="mt-2 text-sm text-foreground-muted leading-relaxed">
            이 계정에는 운영 콘솔 접근 권한이 부여되지 않았습니다. 권한이 필요하면 관리자에게
            문의하세요.
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
