"use client";

import { useEffect } from "react";
import { useUIStore } from "@/lib/uiStore";
import { apiMe, apiRefresh } from "@/lib/authApi";
import {
  clearStoredToken,
  getStoredRefreshToken,
  getStoredToken,
  setStoredRefreshToken,
  setStoredToken,
} from "@/lib/tokenStorage";

export default function AuthProvider() {
  const setUser = useUIStore((s) => s.setUser);
  const setToken = useUIStore((s) => s.setToken);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    setToken(token);
    apiMe(token)
      .then((user) => setUser(user))
      .catch(async () => {
        // 액세스 토큰 만료 → 리프레시 회전으로 재발급 시도
        const refresh = getStoredRefreshToken();
        if (refresh) {
          try {
            const renewed = await apiRefresh(refresh);
            setStoredToken(renewed.access_token);
            setStoredRefreshToken(renewed.refresh_token);
            setToken(renewed.access_token);
            const user = await apiMe(renewed.access_token);
            setUser(user);
            return;
          } catch {
            // 갱신 실패 — 아래에서 정리
          }
        }
        clearStoredToken();
        setToken(null);
      });
  }, []);

  return null;
}
