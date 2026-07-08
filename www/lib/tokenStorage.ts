const KEY = "redocean-token";

export const getStoredToken = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem(KEY) : null;

export const setStoredToken = (token: string): void =>
  localStorage.setItem(KEY, token);

export const clearStoredToken = (): void =>
  localStorage.removeItem(KEY);
