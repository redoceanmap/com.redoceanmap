"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchAdminMe } from "@/lib/adminApi";

/**
 * /admin 클라이언트 가드 — 실보안 경계는 백엔드 require_permission(403)이고,
 * 여기서는 비인가자에게 콘솔 껍데기조차 보여주지 않는 UX 장치다.
 * 판정 전에는 아무것도 렌더하지 않고, 미인증·비관리자(permissions 빈 배열)는 /로 보낸다.
 */
export default function AdminGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data, isError, isPending } = useQuery({
    queryKey: ["admin-me"],
    queryFn: fetchAdminMe,
    retry: false,
    staleTime: 0,
  });

  const denied = isError || (data != null && data.permissions.length === 0);

  useEffect(() => {
    if (denied) router.replace("/");
  }, [denied, router]);

  if (isPending || denied) return null;
  return <>{children}</>;
}
