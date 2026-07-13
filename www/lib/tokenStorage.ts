const KEY = "redocean-token";
const REFRESH_KEY = "redocean-refresh-token";

export const getStoredToken = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem(KEY) : null;

export const setStoredToken = (token: string): void =>
  localStorage.setItem(KEY, token);

export const getStoredRefreshToken = (): string | null =>
  typeof window !== "undefined" ? localStorage.getItem(REFRESH_KEY) : null;

export const setStoredRefreshToken = (token: string): void =>
  localStorage.setItem(REFRESH_KEY, token);

export const clearStoredToken = (): void => {
  localStorage.removeItem(KEY);
  localStorage.removeItem(REFRESH_KEY);
};

export const authHeader = (): Record<string, string> => {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};
