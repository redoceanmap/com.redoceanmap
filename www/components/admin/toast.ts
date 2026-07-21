import { create } from "zustand";

type ToastState = {
  message: string | null;
  type: "success" | "error";
  show: (message: string, type?: "success" | "error") => void;
  clear: () => void;
};

export const useAdminToast = create<ToastState>((set) => ({
  message: null,
  type: "success",
  show: (message, type = "success") => set({ message, type }),
  clear: () => set({ message: null }),
}));

export const showToast = (message: string, type: "success" | "error" = "success") =>
  useAdminToast.getState().show(message, type);
