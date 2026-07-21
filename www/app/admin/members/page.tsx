"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, KeyRound, Search, ShieldCheck } from "lucide-react";
import {
  downloadCsv,
  fetchAdminMembers,
  fetchAdminRoles,
  fetchAllAdminMembers,
  grantAdminRole,
  revokeAdminRole,
  formatDate,
  type AdminMember,
} from "@/lib/adminApi";
import BlockSkeleton from "@/components/admin/BlockSkeleton";
import Empty from "@/components/admin/Empty";
import Kpi from "@/components/admin/Kpi";
import { showToast } from "@/components/admin/toast";

const PAGE_SIZE = 20;

// permission 코드 → 설명 (백엔드 alembic 시드와 동일한 7종)
const PERMISSION_DESC: Record<string, string> = {
  "dashboard:read": "대시보드 KPI 조회",
  "areas:read": "상권 목록 조회",
  "members:read": "회원·역할 구성 조회",
  "members:write": "회원 역할 부여/회수",
  "recommendations:read": "추천 기록 조회",
  "datasources:read": "데이터셋 현황 조회",
  "audit:read": "감사 로그 조회",
};

export default function MembersPage() {
  // REACT_RULES 패턴 B: 목록 질의 상태는 단일 객체 useState (검색어 입력은 패턴 A — FormData 제출)
  const [query, setQuery] = useState({ search: "", page: 0 });
  const queryClient = useQueryClient();

  const { data, isPending, isError } = useQuery({
    queryKey: ["admin-members", query],
    queryFn: () => fetchAdminMembers(query.search, PAGE_SIZE, query.page * PAGE_SIZE),
  });
  const { data: rolesData } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: fetchAdminRoles,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["admin-members"] });
  const grant = useMutation({
    mutationFn: ({ userId, roleCode }: { userId: number; roleCode: string }) =>
      grantAdminRole(userId, roleCode),
    onSuccess: (m) => {
      invalidate();
      showToast(`${m.name}에게 역할을 부여했습니다.`);
    },
    onError: (e) => showToast(e instanceof Error ? e.message : "역할 부여에 실패했습니다.", "error"),
  });
  const revoke = useMutation({
    mutationFn: ({ userId, roleCode }: { userId: number; roleCode: string }) =>
      revokeAdminRole(userId, roleCode),
    onSuccess: (m) => {
      invalidate();
      showToast(`${m.name}의 역할을 회수했습니다.`);
    },
    onError: (e) => showToast(e instanceof Error ? e.message : "역할 회수에 실패했습니다.", "error"),
  });

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    setQuery({ search: String(formData.get("q") ?? "").trim(), page: 0 });
  };

  const exportCsv = async () => {
    try {
      const all = await fetchAllAdminMembers(query.search);
      downloadCsv(
        "admin-members.csv",
        ["ID", "이름", "이메일", "가입일", "마케팅 동의", "역할"],
        all.map((m) => [
          m.id,
          m.name,
          m.email,
          formatDate(m.joined_at),
          m.marketing_agreed ? "동의" : "미동의",
          m.roles.join("|"),
        ]),
      );
      showToast(`회원 ${all.length}명을 CSV로 내보냈습니다.`);
    } catch {
      showToast("CSV 내보내기에 실패했습니다.", "error");
    }
  };

  const roles = rolesData?.roles ?? [];
  const total = data?.total ?? 0;
  const lastPage = Math.max(Math.ceil(total / PAGE_SIZE) - 1, 0);
  const mutating = grant.isPending || revoke.isPending;

  const toggleRole = (member: AdminMember, roleCode: string) => {
    if (mutating) return;
    const has = member.roles.includes(roleCode);
    (has ? revoke : grant).mutate({ userId: member.id, roleCode });
  };

  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">회원 관리</h1>
          <p className="mt-1 text-sm text-foreground-muted">가입 회원 조회 및 역할(RBAC) 부여</p>
        </div>
        <button
          type="button"
          onClick={exportCsv}
          disabled={total === 0}
          className="inline-flex items-center gap-1.5 px-4 h-10 rounded-full border border-border bg-surface text-sm font-medium hover:bg-black/5 transition-colors disabled:opacity-40"
        >
          <Download size={15} /> CSV 내보내기
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-md">
        <Kpi
          label={query.search ? "전체 회원 (검색 결과)" : "전체 회원"}
          value={total.toLocaleString()}
        />
        <Kpi label="운영 역할 종류" value={String(roles.length)} />
      </div>

      <form onSubmit={handleSearch}>
        <label className="flex items-center gap-2 px-3.5 h-10 rounded-full bg-surface border border-border text-sm">
          <Search size={16} className="text-foreground-muted shrink-0" />
          <input
            name="q"
            defaultValue={query.search}
            placeholder="이름 또는 이메일 검색 (Enter)"
            className="bg-transparent outline-none flex-1 placeholder:text-foreground-muted"
          />
        </label>
      </form>

      <section className="rounded-2xl bg-surface border border-border overflow-hidden">
        {isPending && <BlockSkeleton rows={5} />}
        {isError && <Empty msg="회원 목록을 불러오지 못했습니다." />}
        {!isPending && !isError && (data?.items.length ?? 0) === 0 && (
          <Empty msg="조건에 맞는 회원이 없습니다." />
        )}
        {(data?.items.length ?? 0) > 0 && (
          <>
            <div className="hidden sm:block">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-foreground-muted border-b border-border bg-background/60">
                    <th className="font-medium px-5 py-2.5">회원</th>
                    <th className="font-medium px-5 py-2.5">가입일</th>
                    <th className="font-medium px-5 py-2.5">마케팅 동의</th>
                    <th className="font-medium px-5 py-2.5 text-right">역할</th>
                  </tr>
                </thead>
                <tbody>
                  {data!.items.map((m) => (
                    <tr key={m.id} className="border-b border-border last:border-0 hover:bg-background/40">
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-3">
                          <span className="grid place-items-center w-8 h-8 rounded-full bg-brand/10 text-brand text-xs font-semibold">
                            {m.name[0] ?? "?"}
                          </span>
                          <div>
                            <p className="font-medium">{m.name}</p>
                            <p className="text-xs text-foreground-muted">{m.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3 text-foreground-muted tabular-nums">{formatDate(m.joined_at)}</td>
                      <td className="px-5 py-3 text-foreground-muted">{m.marketing_agreed ? "동의" : "—"}</td>
                      <td className="px-5 py-3">
                        <div className="flex justify-end gap-1.5 flex-wrap">
                          {roles.map((r) => (
                            <RoleChip
                              key={r.code}
                              label={r.name}
                              active={m.roles.includes(r.code)}
                              disabled={mutating}
                              onClick={() => toggleRole(m, r.code)}
                            />
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="sm:hidden divide-y divide-border">
              {data!.items.map((m) => (
                <div key={m.id} className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span className="grid place-items-center w-9 h-9 rounded-full bg-brand/10 text-brand text-sm font-semibold shrink-0">
                      {m.name[0] ?? "?"}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-medium">{m.name}</p>
                      <p className="text-xs text-foreground-muted truncate">
                        {m.email} · {formatDate(m.joined_at)}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 flex gap-1.5 flex-wrap">
                    {roles.map((r) => (
                      <RoleChip
                        key={r.code}
                        label={r.name}
                        active={m.roles.includes(r.code)}
                        disabled={mutating}
                        onClick={() => toggleRole(m, r.code)}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </section>

      {/* 페이지네이션 */}
      {total > PAGE_SIZE && (
        <div className="flex items-center justify-center gap-3 text-sm">
          <button
            type="button"
            disabled={query.page === 0}
            onClick={() => setQuery((prev) => ({ ...prev, page: prev.page - 1 }))}
            className="px-4 h-9 rounded-full border border-border disabled:opacity-40 hover:bg-black/5 transition-colors"
          >
            이전
          </button>
          <span className="text-foreground-muted tabular-nums">
            {query.page + 1} / {lastPage + 1}
          </span>
          <button
            type="button"
            disabled={query.page >= lastPage}
            onClick={() => setQuery((prev) => ({ ...prev, page: prev.page + 1 }))}
            className="px-4 h-9 rounded-full border border-border disabled:opacity-40 hover:bg-black/5 transition-colors"
          >
            다음
          </button>
        </div>
      )}

      {/* 역할·권한(RBAC) 구성 — 읽기 전용 (구 설정 페이지에서 이동) */}
      <section className="space-y-4 pt-2">
        <div>
          <h2 className="text-lg font-bold tracking-tight">역할·권한 구성</h2>
          <p className="mt-0.5 text-sm text-foreground-muted">
            읽기 전용 — 역할 부여/회수는 위 회원 목록에서, 변경 이력은 감사 로그에서 확인
          </p>
        </div>
        {roles.map((role) => (
          <div key={role.code} className="rounded-2xl bg-surface border border-border p-5">
            <div className="flex items-center gap-2.5">
              <span className="grid place-items-center w-9 h-9 rounded-xl bg-brand/10 text-brand">
                <ShieldCheck size={17} strokeWidth={1.9} />
              </span>
              <div>
                <h3 className="font-semibold">{role.name}</h3>
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
          </div>
        ))}
      </section>
    </div>
  );
}

function RoleChip({
  label,
  active,
  disabled,
  onClick,
}: {
  label: string;
  active: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      title={active ? `${label} 역할 회수` : `${label} 역할 부여`}
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors disabled:opacity-50 ${
        active
          ? "bg-brand text-white border-brand"
          : "bg-surface text-foreground-muted border-border hover:text-foreground"
      }`}
    >
      <ShieldCheck size={12} /> {label}
    </button>
  );
}
