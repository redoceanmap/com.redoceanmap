"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { apiSocialLogin } from "@/lib/authApi";
import { consumeSocialState, socialRedirectUri, type SocialProvider } from "@/lib/socialAuth";
import { setStoredRefreshToken, setStoredToken } from "@/lib/tokenStorage";
import { useUIStore } from "@/lib/uiStore";

function OauthCallback() {
  const { provider } = useParams<{ provider: SocialProvider }>();
  const search = useSearchParams();
  const router = useRouter();
  const setUser = useUIStore((s) => s.setUser);
  const setToken = useUIStore((s) => s.setToken);
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false); // StrictMode 이중 실행 방지 — 인가 코드는 일회용

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const code = search.get("code");
    const state = search.get("state");
    const { state: savedState, returnTo } = consumeSocialState();
    if (!code || !state || state !== savedState) {
      setError("잘못된 접근입니다. 다시 로그인해 주세요.");
      return;
    }
    apiSocialLogin(provider, code, socialRedirectUri(provider))
      .then((res) => {
        setStoredToken(res.access_token);
        setStoredRefreshToken(res.refresh_token);
        setToken(res.access_token);
        setUser({ id: 0, name: res.name, email: res.email });
        router.replace(returnTo);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "소셜 로그인에 실패했습니다.");
      });
  }, [provider, search, router, setToken, setUser]);

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <div className="text-center">
        {error ? (
          <>
            <p className="text-sm text-red-500">{error}</p>
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
