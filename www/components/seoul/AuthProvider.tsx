"use client";

import { useEffect } from "react";
import { useUIStore } from "@/lib/uiStore";
import { apiMe } from "@/lib/authApi";
import { getStoredToken, clearStoredToken } from "@/lib/tokenStorage";

export default function AuthProvider() {
  const setUser = useUIStore((s) => s.setUser);
  const setToken = useUIStore((s) => s.setToken);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    setToken(token);
    apiMe(token)
      .then((user) => setUser(user))
      .catch(() => {
        clearStoredToken();
        setToken(null);
      });
  }, []);

  return null;
}
