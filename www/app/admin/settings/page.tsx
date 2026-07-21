"use client";

import { useQuery } from "@tanstack/react-query";
import { ShieldCheck, KeyRound } from "lucide-react";
import { fetchAdminRoles } from "@/lib/adminApi";

// permission 코드 → 설명 (백엔드 alembic 시드와 동일한 6종)
const PERMISSION_DESC: Record<string, string> = {
  "dashboard:read": "대시보드 KPI 조회",
  "areas:read": "상권 목록 조회",
  "members:read": "회원·역할 구성 조회",
  "members:write": "회원 역할 부여/회수",
  "recommendations:read": "추천 기록 조회",
  "datasources:read": "데이터셋 현황 조회",
};

export default function SettingsPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: fetchAdminRoles,
  });

  const roles = data?.roles ?? [];

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">설정</h1>
        <p className="mt-1 text-sm text-foreground-muted">
          역할·권한(RBAC) 구성 — 읽기 전용, 역할 부여는 회원 관리에서
        </p>
      </div>

      {isPending && <Empty msg="RBAC 구성을 불러오는 중…" />}
      {isError && <Empty msg="RBAC 구성을 불러오지 못했습니다." />}

      {roles.map((role) => (
        <section key={role.code} className="rounded-2xl bg-surface border border-border p-5">
          <div className="flex items-center gap-2.5">
            <span className="grid place-items-center w-9 h-9 rounded-xl bg-brand/10 text-brand">
              <ShieldCheck size={17} strokeWidth={1.9} />
            </span>
            <div>
              <h2 className="font-semibold">{role.name}</h2>
              <p className="text-xs text-foreground-muted font-mono">{role.code}</p>
            </div>
          </div>

          <div className="mt-4 divide-y divide-border">
            {role.permissions.length === 0 && (
              <p className="py-3 text-sm text-foreground-muted">부여된 권한이 없습니다.</p>
            )}
            {role.permissions.map((code) => (
              <div key={code} className="flex items-center gap-3 py-3">
                <KeyRound size={14} className="text-foreground-muted shrink-0" />
                <span className="text-sm font-mono">{code}</span>
                <span className="ml-auto text-xs text-foreground-muted">
                  {PERMISSION_DESC[code] ?? ""}
                </span>
              </div>
            ))}
          </div>
        </section>
      ))}

      {!isPending && !isError && (
        <p className="text-xs text-foreground-muted leading-relaxed">
          권한 검사는 백엔드가 매 요청 DB 조회로 수행하므로 역할 회수는 즉시 반영됩니다. 최초 관리자
          부여는 서버에서 <code className="font-mono">python scripts/grant_admin.py &lt;email&gt;</code>로
          실행합니다.
        </p>
      )}
    </div>
  );
}

function Empty({ msg }: { msg: string }) {
  return <p className="p-8 text-center text-sm text-foreground-muted">{msg}</p>;
}
