// 소셜 로그인 시작 — 각 사 인가 페이지로 리다이렉트하고, 복귀는 /oauth/[provider] 콜백 페이지가 받는다.

export type SocialProvider = "google" | "kakao" | "naver";

// NEXT_PUBLIC_*은 빌드 시 정적 치환되므로 process.env를 직접 나열한다.
const CLIENT_IDS: Record<SocialProvider, string | undefined> = {
  google: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
  kakao: process.env.NEXT_PUBLIC_KAKAO_CLIENT_ID,
  naver: process.env.NEXT_PUBLIC_NAVER_CLIENT_ID,
};

const AUTHORIZE_URLS: Record<SocialProvider, string> = {
  google: "https://accounts.google.com/o/oauth2/v2/auth",
  kakao: "https://kauth.kakao.com/oauth/authorize",
  naver: "https://nid.naver.com/oauth2.0/authorize",
};

const PROVIDER_LABELS: Record<SocialProvider, string> = {
  google: "구글",
  kakao: "카카오",
  naver: "네이버",
};

const STATE_KEY = "social-oauth-state";
const RETURN_TO_KEY = "social-oauth-return-to";

export const socialRedirectUri = (provider: SocialProvider): string =>
  `${window.location.origin}/oauth/${provider}`;

/** 인가 페이지로 이동. 클라이언트 ID 미설정 시 throw — 호출부가 사용자에게 알린다. */
export function startSocialLogin(provider: SocialProvider): void {
  const clientId = CLIENT_IDS[provider];
  if (!clientId) {
    throw new Error(`${PROVIDER_LABELS[provider]} 로그인이 아직 설정되지 않았습니다.`);
  }
  const state = crypto.randomUUID();
  sessionStorage.setItem(STATE_KEY, state);
  sessionStorage.setItem(RETURN_TO_KEY, window.location.pathname + window.location.search);

  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: socialRedirectUri(provider),
    response_type: "code",
    state,
  });
  if (provider === "google") params.set("scope", "openid email profile");
  // 프로바이더에 세션이 남아 있어도 자동 통과시키지 않고 항상 계정 로그인 화면을 띄운다.
  if (provider === "kakao") params.set("prompt", "login");
  if (provider === "naver") params.set("auth_type", "reauthenticate");
  window.location.href = `${AUTHORIZE_URLS[provider]}?${params.toString()}`;
}

/** 콜백 페이지에서 state 검증 + 복귀 경로 회수 (일회용 — 읽으면서 지운다). */
export function consumeSocialState(): { state: string | null; returnTo: string } {
  const state = sessionStorage.getItem(STATE_KEY);
  const returnTo = sessionStorage.getItem(RETURN_TO_KEY) ?? "/";
  sessionStorage.removeItem(STATE_KEY);
  sessionStorage.removeItem(RETURN_TO_KEY);
  return { state, returnTo };
}
