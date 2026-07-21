"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";

/**
 * 어드민 확인 모달 — 무상태(REACT_RULES). 사유 입력은 uncontrolled(FormData 패턴 A).
 * danger면 확인 버튼이 붉은색(비가역 행위 — 탈퇴 등).
 */
export default function ConfirmDialog({
  title,
  message,
  confirmLabel,
  danger = false,
  withReason = false,
  onConfirm,
  onClose,
}: {
  title: string;
  message: string;
  confirmLabel: string;
  danger?: boolean;
  withReason?: boolean;
  onConfirm: (reason: string) => void;
  onClose: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    onConfirm(String(formData.get("reason") ?? "").trim());
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4"
      // mousedown이 오버레이 자신에서 시작한 경우에만 닫는다 —
      // 입력란에서 드래그해 오버레이에서 떼는 동작이 오닫힘을 일으키지 않도록(click 대신).
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-2xl bg-surface border border-border p-6"
      >
        <div className="flex items-center gap-2.5">
          <span
            className={`grid place-items-center w-10 h-10 rounded-full shrink-0 ${
              danger ? "bg-red-50 text-red-600" : "bg-brand/10 text-brand"
            }`}
          >
            <AlertTriangle size={18} strokeWidth={1.9} />
          </span>
          <h2 className="font-bold tracking-tight">{title}</h2>
        </div>
        <p className="mt-3 text-sm text-foreground-muted leading-relaxed whitespace-pre-line">
          {message}
        </p>
        {withReason && (
          <input
            name="reason"
            autoFocus
            maxLength={200}
            placeholder="사유 (선택, 200자 이내)"
            className="mt-4 w-full h-11 px-3.5 rounded-xl bg-background border border-border text-sm outline-none focus:border-brand"
          />
        )}
        <div className="mt-6 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 h-10 rounded-full border border-border text-sm font-medium hover:bg-black/5 transition-colors"
          >
            취소
          </button>
          <button
            type="submit"
            className={`px-5 h-10 rounded-full text-white text-sm font-medium transition-colors ${
              danger ? "bg-red-600 hover:bg-red-700" : "bg-brand hover:bg-brand-deep"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </form>
    </div>
  );
}
