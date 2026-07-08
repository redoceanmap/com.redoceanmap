import { create } from "zustand";

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
