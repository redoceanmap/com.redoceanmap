"use client";

import { useEffect } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { useAdminToast } from "./toast";

// 어드민 전용 경량 토스트 호스트 — layout에 1개만 렌더, 3초 후 자동 소멸.
export default function AdminToast() {
  const { message, type, clear } = useAdminToast();

  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(clear, 3000);
    return () => clearTimeout(timer);
  }, [message, clear]);

  if (!message) return null;
  const error = type === "error";
  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-20 lg:bottom-6 right-4 sm:right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg border border-border text-sm font-medium bg-surface animate-fade-in-up"
    >
      {error ? (
        <XCircle size={16} className="text-red-600 shrink-0" />
      ) : (
        <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
      )}
      <span className={error ? "text-red-700" : "text-foreground"}>{message}</span>
    </div>
  );
}
