"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { apiSocialConsent, apiSocialLogin, type AuthResponse } from "@/lib/authApi";
import { consumeSocialState, socialRedirectUri, type SocialProvider } from "@/lib/socialAuth";
import { setStoredRefreshToken, setStoredToken } from "@/lib/tokenStorage";
import { useUIStore } from "@/lib/uiStore";

const CONSENT_TERMS = [
  { name: "age", label: "(필수) 만 14세 이상입니다.", required: true },
  { name: "terms", label: "(필수) 이용약관 동의", required: true, href: "/terms" },
  { name: "privacy", label: "(필수) 개인정보 수집 및 이용 동의", required: true, href: "/privacy" },
  { name: "marketing", label: "(선택) 마케팅 정보 수신 동의", required: false },
];

function OauthCallback() {
  const { provider } = useParams<{ provider: SocialProvider }>();
  const search = useSearchParams();
  const router = useRouter();
  const setUser = useUIStore((s) => s.setUser);
  const setToken = useUIStore((s) => s.setToken);
  // 단일 객체 상태 — phase에 따라 로딩 / 약관 동의 / 에러 화면으로 분기한다.
  const [state, setState] = useState<{
    phase: "loading" | "consent" | "error";
    error: string;
    loading: boolean;
    consent: { token: string; name: string; email: string } | null;
    returnTo: string;
  }>({ phase: "loading", error: "", loading: false, consent: null, returnTo: "/" });
  const started = useRef(false); // StrictMode 이중 실행 방지 — 인가 코드는 일회용

  const finishLogin = (res: AuthResponse, returnTo: string) => {
    setStoredToken(res.access_token);
    setStoredRefreshToken(res.refresh_token);
    setToken(res.access_token);
    setUser({ id: 0, name: res.name, email: res.email });
    router.replace(returnTo);
  };

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const code = search.get("code");
    const returnedState = search.get("state");
    const { state: savedState, returnTo } = consumeSocialState();
    if (!code || !returnedState || returnedState !== savedState) {
      setState((prev) => ({ ...prev, phase: "error", error: "잘못된 접근입니다. 다시 로그인해 주세요." }));
      return;
    }
    apiSocialLogin(provider, code, socialRedirectUri(provider))
      .then((res) => {
        if (res.status === "consent_required") {
          // 신규 유저 — 약관 동의를 마쳐야 가입·로그인이 완료된다.
          setState((prev) => ({
            ...prev,
            phase: "consent",
            consent: { token: res.consent_token, name: res.name, email: res.email },
            returnTo,
          }));
          return;
        }
        finishLogin(res, returnTo);
      })
      .catch((err) => {
        setState((prev) => ({
          ...prev,
          phase: "error",
          error: err instanceof Error ? err.message : "소셜 로그인에 실패했습니다.",
        }));
      });
  }, [provider, search, router, setToken, setUser]);

  // FormData 패턴 — 체크박스는 uncontrolled, 제출 시점에 일괄 수집한다.
  const handleConsentSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!state.consent) return;
    const formData = new FormData(e.currentTarget);
    setState((prev) => ({ ...prev, error: "", loading: true }));
    try {
      const res = await apiSocialConsent(state.consent.token, formData.get("marketing") === "on");
      finishLogin(res, state.returnTo);
    } catch (err) {
      setState((prev) => ({
        ...prev,
        error: err instanceof Error ? err.message : "약관 동의 처리에 실패했습니다.",
        loading: false,
      }));
    }
  };

  const toggleAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    const form = e.currentTarget.form;
    if (!form) return;
    for (const t of CONSENT_TERMS) {
      const box = form.elements.namedItem(t.name);
      if (box instanceof HTMLInputElement) box.checked = e.currentTarget.checked;
    }
  };

  if (state.phase === "consent" && state.consent) {
    return (
      <div className="min-h-screen grid place-items-center px-4">
        <div className="w-full max-w-md bg-surface rounded-2xl shadow-xl p-8">
          <h1 className="text-xl font-bold text-center">redoceanmap</h1>
          <p className="mt-3 text-sm text-foreground-muted text-center">
            {state.consent.name}님({state.consent.email}), 처음 오셨네요.
            <br />
            서비스 이용을 위해 약관 동의가 필요합니다.
          </p>
          <form onSubmit={handleConsentSubmit} className="mt-6 flex flex-col gap-2 text-sm">
            <label className="flex items-center gap-2 font-semibold cursor-pointer">
              <input type="checkbox" className="accent-brand" onChange={toggleAll} />
              전체 동의합니다.
            </label>
            {CONSENT_TERMS.map((t) => (
              <label
                key={t.name}
                className="flex items-center gap-2 text-foreground-muted cursor-pointer pl-5"
              >
                <input type="checkbox" name={t.name} required={t.required} className="accent-brand" />
                {t.href ? (
                  <span>
                    {t.label.replace(" 동의", "")}{" "}
                    <a
                      href={t.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-foreground"
                    >
                      보기
                    </a>
                  </span>
                ) : (
                  t.label
                )}
              </label>
            ))}
            {state.error && <p className="text-sm text-red-500 text-center">{state.error}</p>}
            <button
              type="submit"
              disabled={state.loading}
              className="mt-4 w-full bg-brand text-white py-3 rounded-xl font-medium hover:bg-brand-deep transition-colors disabled:opacity-60"
            >
              {state.loading ? "처리 중..." : "동의하고 시작하기"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <div className="text-center">
        {state.phase === "error" ? (
          <>
            <p className="text-sm text-red-500">{state.error}</p>
            <button
              type="button"
              onClick={() => router.replace("/")}
              className="mt-4 text-sm underline text-foreground-muted hover:text-foreground"
            >
              홈으로 돌아가기
            </button>
          </>
        ) : (
          <p className="text-sm text-foreground-muted">로그인 처리 중...</p>
        )}
      </div>
    </div>
  );
}

export default function OauthCallbackPage() {
  return (
    <Suspense fallback={null}>
      <OauthCallback />
    </Suspense>
  );
}
