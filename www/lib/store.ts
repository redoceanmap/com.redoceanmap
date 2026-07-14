import { create } from "zustand";
import type { Area, ConversationMessage, StockAnalysis } from "./types";
import { fetchConversationMessages } from "./api";
import { authHeader } from "./tokenStorage";

export type { StockAnalysis } from "./types"; // 기존 임포트 호환 재수출

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
  loadConversation: (id: number) => Promise<ConversationMessage[]>;
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
  // 지난 대화 복원 — payload(추천/종목 카드)까지 되살린다. 원본 목록을 반환해
  // 호출부(히스토리 페이지)가 이동할 워크스페이스를 결정하게 한다.
  loadConversation: async (id) => {
    set({ isLoading: true });
    try {
      const raw = await fetchConversationMessages(id);
      const messages: Message[] = raw.map((m) => ({
        id: crypto.randomUUID(),
        role: m.role,
        content: m.content,
        recommendations: m.payload?.recommendations,
        stock: m.payload?.stock,
      }));
      const lastRecommendations =
        [...raw].reverse().find((m) => m.payload?.recommendations?.length)?.payload
          ?.recommendations ?? [];
      set({
        messages,
        recommendations: lastRecommendations,
        conversationId: id,
        isLoading: false,
      });
      return raw;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  reset: () =>
    set({ messages: [], recommendations: [], conversationId: null, isLoading: false }),
}));
