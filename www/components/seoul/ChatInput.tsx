"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { Plus, ChevronDown, ArrowRight } from "lucide-react";

type Props = {
  onSubmit: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
};

export default function ChatInput({
  onSubmit,
  disabled,
  placeholder = "예산이랑 하고 싶은 업종을 알려주세요",
}: Props) {
  const [text, setText] = useState("");

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setText("");
  };

  const handleFormSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const canSend = text.trim().length > 0 && !disabled;

  return (
    <form
      onSubmit={handleFormSubmit}
      className="bg-surface border border-border rounded-2xl shadow-sm"
    >
      <textarea
        aria-label="질문 입력"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={2}
        className="w-full resize-none bg-transparent px-5 pt-5 pb-2 outline-none text-base placeholder:text-foreground-muted"
      />
      <div className="flex items-center justify-between px-3 pb-3">
        <button
          type="button"
          aria-label="첨부"
          className="w-9 h-9 grid place-items-center rounded-full text-foreground-muted hover:bg-black/5"
        >
          <Plus size={18} strokeWidth={1.75} />
        </button>
        <div className="flex items-center gap-1 text-sm text-foreground-muted">
          <button
            type="button"
            className="flex items-center gap-1 px-2 py-1 rounded-md hover:bg-black/5"
          >
            ROM 1.0 <ChevronDown size={14} />
          </button>
          <button
            type="submit"
            aria-label="보내기"
            disabled={!canSend}
            className="ml-1 w-9 h-9 grid place-items-center rounded-full bg-brand text-white hover:bg-brand-deep transition-colors disabled:bg-border disabled:text-foreground-muted disabled:cursor-not-allowed"
          >
            <ArrowRight size={16} strokeWidth={2.25} />
          </button>
        </div>
      </div>
    </form>
  );
}
