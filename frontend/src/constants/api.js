export const API_BASE =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

export const API = {
  BASE: API_BASE,

  CHAT: `${API_BASE}/chat`,
  CHAT_STREAM: `${API_BASE}/chat/stream`,

  BROWSER: `${API_BASE}/browser/search`,

  SYSTEM: `${API_BASE}/`,
};