import {
  getStoredRefreshToken,
  setStoredRefreshToken,
  setStoredToken,
} from "./tokenStorage";

// 브라우저에서 실행되므로 same-origin /api/backend(next.config rewrites)로 프록시한다 —
// NEXT_PUBLIC_API_URL은 컨테이너 내부 호스트명(backend:8000)일 수 있어 브라우저가 해석 못 한다.
const API_BASE = "/api/backend";

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  name: string;
  email: string;
};

export async function apiRefresh(refreshToken: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "토큰 갱신에 실패했습니다.");
  return data;
}

export async function apiLogin(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "로그인에 실패했습니다.");
  return data;
}

export async function apiRegister(
  email: string,
  password: string,
  name: string,
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "회원가입에 실패했습니다.");
  return data;
}

/** 리프레시 토큰 회전으로 액세스 토큰 재발급 — 성공 시 저장까지 마치고 true. */
export async function tryRefreshToken(): Promise<boolean> {
  const refresh = getStoredRefreshToken();
  if (!refresh) return false;
  try {
    const renewed = await apiRefresh(refresh);
    setStoredToken(renewed.access_token);
    setStoredRefreshToken(renewed.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function apiMe(token: string): Promise<{ id: number; email: string; name: string }> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("인증이 만료되었습니다.");
  return res.json();
}
