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
  marketingAgreed: boolean,
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // terms_agreed: 필수 약관 체크를 통과해야만 제출되므로 항상 true
    body: JSON.stringify({ email, password, name, terms_agreed: true, marketing_agreed: marketingAgreed }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "회원가입에 실패했습니다.");
  return data;
}

/** 소셜 로그인 응답 — 기존 유저면 토큰, 신규 유저면 약관 동의 요구. */
export type SocialLoginResponse =
  | ({ status: "ok" } & AuthResponse)
  | { status: "consent_required"; consent_token: string; name: string; email: string };

export async function apiSocialLogin(
  provider: string,
  code: string,
  redirectUri: string,
): Promise<SocialLoginResponse> {
  const res = await fetch(`${API_BASE}/auth/social/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, code, redirect_uri: redirectUri }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "소셜 로그인에 실패했습니다.");
  return data;
}

/** 신규 소셜 유저의 약관 동의 완료 — 이 시점에 가입되고 토큰이 발급된다. */
export async function apiSocialConsent(
  consentToken: string,
  marketingAgreed: boolean,
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/social/consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ consent_token: consentToken, marketing_agreed: marketingAgreed }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "약관 동의 처리에 실패했습니다.");
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

/** 보이는 탭 키 목록 — 등급(역할) 합집합. 비로그인(token null)은 기본 등급 구성. */
export async function apiTabs(token: string | null): Promise<{ tabs: string[] }> {
  const res = await fetch(`${API_BASE}/auth/tabs`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error("탭 구성을 불러오지 못했습니다.");
  return res.json();
}
