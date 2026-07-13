import { create } from "zustand";
import type { Area } from "./mockApi";
import { authHeader } from "./tokenStorage";


export type StockAnalysis = {
  symbol: string;
  price: number;
  direction: "UP" | "DOWN" | "NEUTRAL";
  confidence: number;
  rsi: number;
  ma20: number;
  ma50: number;
  support: number;
  resistance: number;
  sentimentLabel: string;
  headlines: string[];
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  recommendations?: Area[];
  stock?: StockAnalysis;
};

type ChatState = {
  messages: Message[];
  recommendations: Area[];
  conversationId: number | null;
  isLoading: boolean;
  sendMessage: (prompt: string) => Promise<void>;
  reset: () => void;
};

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  recommendations: [],
  conversationId: null,
  isLoading: false,
  sendMessage: async (prompt) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: prompt,
    };
    set((s) => ({ messages: [...s.messages, userMsg], isLoading: true }));

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeader() },
        body: JSON.stringify({ prompt, conversationId: get().conversationId }),
      });

      if (!res.ok) throw new Error("AI 응답 오류");

      const data: {
        text: string;
        recommendations: Area[];
        conversationId: number;
        stock?: StockAnalysis | null;
      } = await res.json();

      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.text,
        recommendations: data.recommendations,
        stock: data.stock ?? undefined,
      };
      set((s) => ({
        messages: [...s.messages, aiMsg],
        recommendations: data.recommendations,
        conversationId: data.conversationId,
        isLoading: false,
      }));
    } catch {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "죄송해요, 일시적인 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
      };
      set((s) => ({ messages: [...s.messages, errMsg], isLoading: false }));
    }
  },
  reset: () =>
    set({ messages: [], recommendations: [], conversationId: null, isLoading: false }),
}));
