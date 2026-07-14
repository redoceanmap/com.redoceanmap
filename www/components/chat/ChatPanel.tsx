"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { ArrowUpRight, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { useChatStore } from "@/lib/store";
import type { Area, StockAnalysis } from "@/lib/types";
import ChatInput from "@/components/seoul/ChatInput";

const DIRECTION_META = {
  UP: { label: "상승 신호", icon: TrendingUp, className: "text-red-600 bg-red-50 border-red-200" },
  DOWN: { label: "하락 신호", icon: TrendingDown, className: "text-blue-600 bg-blue-50 border-blue-200" },
  NEUTRAL: { label: "중립", icon: Minus, className: "text-foreground-muted bg-surface border-border" },
} as const;

function PinMark({ size = 13 }: { size?: number }) {
  return (
    <svg width={size} height={Math.round((size * 20) / 16)} viewBox="0 0 16 20" aria-hidden>
      <path d="M8 0C3.6 0 0 3.6 0 8c0 6 8 12 8 12s8-6 8-12c0-4.4-3.6-8-8-8z" fill="#991B1B" />
      <circle cx="8" cy="8" r="2.5" fill="#FFFFFF" />
    </svg>
  );
}

type ChatPanelProps = {
  workspace: "stock" | "market";
  placeholder: string;
  emptyPrompts: string[]; // 빈 대화 상태에서 보여줄 예시 질문
  onSelectStock?: (stock: StockAnalysis) => void; // stock 워크스페이스: 카드 클릭 → ?symbol 갱신
  onSelectArea?: (area: Area) => void; // market 워크스페이스: 카드 클릭 → 핀 포커스
};

// 워크스페이스 공용 채팅 패널 — 메시지 리스트 + 입력창.
// 현재 워크스페이스와 같은 도메인 카드는 스테이지 조작(onSelect*),
// 다른 도메인 카드는 해당 워크스페이스로 가는 링크 칩만 렌더한다(자동 이동 금지).
export default function ChatPanel({
  workspace,
  placeholder,
  emptyPrompts,
  onSelectStock,
  onSelectArea,
}: ChatPanelProps) {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const conversationId = useChatStore((s) => s.conversationId);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const cParam = conversationId ? `&c=${conversationId}` : "";

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 flex flex-col gap-5" aria-live="polite">
        {messages.length === 0 && !isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center px-2">
            <PinMark size={18} />
            <p className="text-sm text-foreground-muted">
              {workspace === "stock"
                ? "종목에 대해 무엇이든 물어보세요"
                : "동네·업종·예산으로 물어보세요"}
            </p>
            <div className="flex flex-col gap-2 w-full">
              {emptyPrompts.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => void sendMessage(p)}
                  className="w-full text-left text-sm px-3.5 py-2.5 rounded-xl border border-border bg-surface hover:border-brand/40 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => {
          if (m.role === "user") {
            return (
              <div key={m.id} className="flex justify-end animate-fade-in-up">
                <div className="max-w-[85%] bg-surface border border-border rounded-2xl px-3.5 py-2.5 text-sm text-foreground whitespace-pre-wrap">
                  {m.content}
                </div>
              </div>
            );
          }
          return (
            <div key={m.id} className="flex gap-2.5 animate-fade-in-up">
              <div className="shrink-0 w-5 grid place-items-start pt-1">
                <PinMark />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                  {m.content}
                </p>

                {m.stock && (
                  workspace === "stock" ? (
                    <StockSummaryCard stock={m.stock} onClick={() => onSelectStock?.(m.stock!)} />
                  ) : (
                    <Link
                      href={`/stock?symbol=${encodeURIComponent(m.stock.symbol)}${cParam}`}
                      className="mt-3 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-brand text-white text-xs font-medium hover:bg-brand-deep transition-colors"
                    >
                      {m.stock.symbol} 주식 워크스페이스에서 열기
                      <ArrowUpRight size={13} strokeWidth={2.25} />
                    </Link>
                  )
                )}

                {m.recommendations && m.recommendations.length > 0 && (
                  workspace === "market" ? (
                    <div className="mt-3 flex flex-col gap-2">
                      {m.recommendations.map((r) => (
                        <button
                          key={r.id}
                          type="button"
                          onClick={() => onSelectArea?.(r)}
                          className="w-full text-left bg-surface border border-border rounded-xl p-3 hover:border-brand/40 transition-colors"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-semibold">{r.name}</span>
                            <span className="text-[11px] text-foreground-muted shrink-0">{r.category}</span>
                          </div>
                          <p className="text-xs mt-1.5 text-foreground/80 leading-snug">{r.reason}</p>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <Link
                      href={`/market?trdar=${m.recommendations[0].id}${cParam}`}
                      className="mt-3 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-brand text-white text-xs font-medium hover:bg-brand-deep transition-colors"
                    >
                      추천 상권 {m.recommendations.length}곳 지도에서 열기
                      <ArrowUpRight size={13} strokeWidth={2.25} />
                    </Link>
                  )
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-2.5 animate-fade-in-up" role="status" aria-label="응답 생성 중">
            <div className="shrink-0 w-5 grid place-items-start pt-1">
              <PinMark />
            </div>
            <div className="flex-1 flex flex-col gap-2">
              <div className="skeleton h-3.5 rounded-md w-[85%]" />
              <div className="skeleton h-3.5 rounded-md w-[65%]" />
              <div className="skeleton h-3.5 rounded-md w-[45%]" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 px-3 pb-3 pt-1">
        <ChatInput
          onSubmit={(text) => void sendMessage(text)}
          disabled={isLoading}
          placeholder={placeholder}
        />
      </div>
    </div>
  );
}

function StockSummaryCard({ stock, onClick }: { stock: StockAnalysis; onClick: () => void }) {
  const meta = DIRECTION_META[stock.direction] ?? DIRECTION_META.NEUTRAL;
  const DirectionIcon = meta.icon;
  return (
    <button
      type="button"
      onClick={onClick}
      className="mt-3 w-full text-left bg-surface border border-border rounded-xl p-3 hover:border-brand/40 transition-colors"
    >
      <div className="flex items-center justify-between gap-2">
        <div>
          <div className="text-sm font-semibold">{stock.symbol}</div>
          <div className="text-base font-bold mt-0.5">
            {stock.price.toLocaleString("ko-KR", { maximumFractionDigits: 2 })}
          </div>
        </div>
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border text-[11px] font-medium ${meta.className}`}>
          <DirectionIcon size={12} strokeWidth={2} />
          {meta.label} {Math.round(stock.confidence * 100)}%
        </span>
      </div>
      <p className="mt-2 text-[11px] text-foreground-muted">차트에 반영하려면 클릭</p>
    </button>
  );
}
