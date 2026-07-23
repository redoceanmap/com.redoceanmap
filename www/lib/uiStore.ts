import { create } from "zustand";
import { persist } from "zustand/middleware";

export type AuthMode = "login" | "signup";

export type User = {
  id: number;
  name: string;
  email: string;
};

type UIState = {
  authOpen: boolean;
  authMode: AuthMode;
  user: User | null;
  token: string | null;
  openAuth: (mode: AuthMode) => void;
  closeAuth: () => void;
  setAuthMode: (mode: AuthMode) => void;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
};

export const useUIStore = create<UIState>((set) => ({
  authOpen: false,
  authMode: "login",
  user: null,
  token: null,
  openAuth: (mode) => set({ authOpen: true, authMode: mode }),
  closeAuth: () => set({ authOpen: false }),
  setAuthMode: (mode) => set({ authMode: mode }),
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  logout: () => set({ user: null, token: null }),
}));

// 표시 밀도 — 기본은 초보(결론 위주). 전문가는 원 수치·표본·전체 지표까지 펼친다.
// 매 방문마다 다시 켜게 하면 전문가에게 성가시므로 이 값만 로컬에 남긴다(민감정보 아님).
type DensityState = {
  expert: boolean;
  toggleExpert: () => void;
};

export const useDensityStore = create<DensityState>()(
  persist(
    (set) => ({
      expert: false,
      toggleExpert: () => set((s) => ({ expert: !s.expert })),
    }),
    { name: "rom-display-density" },
  ),
);
