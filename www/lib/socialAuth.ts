// 소셜 로그인 시작 — BFF(패턴 A): 인가 URL 조립·state·redirect_uri는 전부 auth 서버 몫.
// 브라우저는 서버의 start 엔드포인트로 이동만 한다(클라이언트 ID·state가 JS에 없음).

import { AUTH_BASE } from "./authApi";

export type SocialProvider = "google" | "kakao" | "naver";

/** 인가 절차 시작 — 완료 후 서버가 현재 경로(return_to)로 302 복귀시킨다. */
export function startSocialLogin(provider: SocialProvider): void {
  const returnTo = window.location.pathname + window.location.search;
  window.location.href =
    `${AUTH_BASE}/social/${provider}/start?return_to=${encodeURIComponent(returnTo)}`;
}
