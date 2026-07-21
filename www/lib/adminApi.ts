import { ApiError } from "./api";
import { authHeader } from "./tokenStorage";

/* ── 타입 (백엔드 admin 스키마 1:1) ── */

export type AdminMe = { user_id: number; permissions: string[] };

export type AdminMonthCount = { month: string; count: number };
export type AdminCategoryCount = { category: string; count: number };
export type AdminRecentRecommendation = {
  id: number;
  trdar_code: number;
  trdar_name: string;
  district_name: string;
  category: string;
  created_at: string;
};

export type AdminDashboard = {
  member_total: number;
  member_new_this_month: number;
  area_count: number;
  latest_quarter: string | null;
  recommendation_total: number;
  recommendation_today: number;
  monthly: AdminMonthCount[];
  top_categories: AdminCategoryCount[];
  recent: AdminRecentRecommendation[];
};

export type AdminAreaRow = {
  trdar_code: number;
  trdar_name: string;
  gu_name: string;
  dong_name: string;
  store_count: number | null;
  closure_rate: number | null;
  monthly_sales: number | null;
};

export type AdminMember = {
  id: number;
  email: string;
  name: string;
  joined_at: string | null;
  marketing_agreed: boolean;
  roles: string[];
};

export type AdminMembersPage = { total: number; items: AdminMember[] };

export type AdminRole = { code: string; name: string; permissions: string[] };

export type AdminRecommendationLog = {
  id: number;
  trdar_code: number;
  trdar_name: string;
  district_name: string;
  category: string;
  reason: string;
  created_at: string;
};

export type AdminRecommendationLogs = {
  total: number;
  today: number;
  items: AdminRecommendationLog[];
};

export type AdminDatasetStat = {
  key: string;
  name: string;
  row_count: number;
  latest_label: string | null;
};

export type AdminAuditEntry = {
  id: number;
  actor_id: number;
  action: string;
  detail: string;
  created_at: string;
};

/* ── 요청 헬퍼 — lib/api.ts의 getJson 패턴 + 쓰기 메서드 ── */

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api/backend${path}`, {
    ...init,
    headers: { ...authHeader(), ...(init?.body ? { "Content-Type": "application/json" } : {}) },
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new ApiError(res.status, detail?.detail ?? "요청에 실패했습니다.");
  }
  return res.json();
}

/* ── fetcher ── */

export const fetchAdminMe = (): Promise<AdminMe> => request("/admin/me");

export const fetchAdminDashboard = (): Promise<AdminDashboard> => request("/admin/dashboard");

export const fetchAdminAreas = (): Promise<{ areas: AdminAreaRow[] }> => request("/admin/areas");

export const fetchAdminMembers = (
  search: string,
  limit: number,
  offset: number,
): Promise<AdminMembersPage> => {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (search) params.set("search", search);
  return request(`/admin/members?${params}`);
};

export const fetchAdminRoles = (): Promise<{ roles: AdminRole[] }> =>
  request("/admin/members/roles");

export const grantAdminRole = (userId: number, roleCode: string): Promise<AdminMember> =>
  request(`/admin/members/${userId}/roles`, {
    method: "POST",
    body: JSON.stringify({ role_code: roleCode }),
  });

export const revokeAdminRole = (userId: number, roleCode: string): Promise<AdminMember> =>
  request(`/admin/members/${userId}/roles/${encodeURIComponent(roleCode)}`, {
    method: "DELETE",
  });

export const fetchAdminRecommendations = (limit = 50): Promise<AdminRecommendationLogs> =>
  request(`/admin/recommendations?limit=${limit}`);

export const fetchAdminDataSources = (): Promise<{ datasets: AdminDatasetStat[] }> =>
  request("/admin/data-sources");

export const fetchAdminAudit = (limit = 50): Promise<{ items: AdminAuditEntry[] }> =>
  request(`/admin/audit?limit=${limit}`);

// CSV 내보내기용 — 서버 limit 상한(100)에 맞춰 offset 순회로 전량 수집
export const fetchAllAdminMembers = async (search: string): Promise<AdminMember[]> => {
  const all: AdminMember[] = [];
  let offset = 0;
  for (;;) {
    const page = await fetchAdminMembers(search, 100, offset);
    all.push(...page.items);
    offset += 100;
    if (all.length >= page.total || page.items.length === 0) return all;
  }
};

// BOM 포함 CSV 다운로드 (엑셀 한글 호환)
export const downloadCsv = (filename: string, header: string[], rows: (string | number)[][]) => {
  const escape = (v: string | number) => {
    const s = String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const csv = [header, ...rows].map((r) => r.map(escape).join(",")).join("\n");
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

/* ── 표시 헬퍼 ── */

// "20251" → "2025년 1분기", ISO 문자열 → "YYYY-MM-DD"
export const formatLatestLabel = (label: string | null): string => {
  if (!label) return "—";
  if (/^\d{5}$/.test(label)) return `${label.slice(0, 4)}년 ${label.slice(4)}분기`;
  return label.slice(0, 10);
};

export const formatDate = (iso: string | null): string => (iso ? iso.slice(0, 10) : "—");

// 원 단위 월매출 → "8,420만" 표기
export const formatSalesMan = (won: number | null): string =>
  won == null ? "—" : `${Math.round(won / 10_000).toLocaleString()}만`;
