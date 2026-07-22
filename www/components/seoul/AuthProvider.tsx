"use client";

import { useEffect } from "react";
import { useUIStore } from "@/lib/uiStore";
import { apiMe, tryRefreshSession } from "@/lib/authApi";

// 구(localStorage 토큰) 시대의 잔존 키 — BFF 전환(httpOnly 쿠키) 후 1회 정리
const LEGACY_KEYS = ["redocean-token", "redocean-refresh-token"];

export default function AuthProvider() {
  const setUser = useUIStore((s) => s.setUser);

  useEffect(() => {
    for (const key of LEGACY_KEYS) localStorage.removeItem(key);

    // 세션 복원 — 쿠키가 유효하면 me, 만료면 리프레시 회전 후 1회 재시도
    apiMe()
      .then((user) => setUser(user))
      .catch(async () => {
        if (await tryRefreshSession()) {
          try {
            setUser(await apiMe());
            return;
          } catch {
            // 아래에서 비로그인 확정
          }
        }
        setUser(null);
      });
  }, []);

  return null;
}
