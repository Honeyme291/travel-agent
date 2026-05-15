/**
 * API 客户端 — 支持 REST + SSE 流式
 */

const BASE = "/api";

let _token = "";
export function setToken(t) { _token = t; localStorage.setItem("jwt", t); }
export function getToken() {
  if (!_token) _token = localStorage.getItem("jwt") || "";
  return _token;
}

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  const t = getToken();
  if (t) opts.headers.Authorization = `Bearer ${t}`;
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`HTTP ${res.status}: ${err}`);
  }
  return res.json();
}

export const api = {
  // ── Chat ──
  chat(query, sessionId = "default", userId = null) {
    const body = { query, session_id: sessionId };
    if (userId) body.user_id = userId;
    return request("POST", "/chat", body);
  },
  spotImages(query) {
    return request("GET", `/spot-images?query=${encodeURIComponent(query)}`);
  },
  getTools() { return request("GET", "/tools"); },
  health() { return request("GET", "/health"); },
  clearSession(sessionId = "default") {
    return request("POST", "/session/clear", { session_id: sessionId });
  },
  newSession() { return request("POST", "/session/new"); },

  // ── Auth ──
  register(username, password, nickname) {
    return request("POST", "/auth/register", { username, password, nickname });
  },
  login(username, password) {
    return request("POST", "/auth/login", { username, password });
  },
  me() {
    return request("GET", `/auth/me?token=${encodeURIComponent(getToken())}`);
  },

  // ── History ──
  getConversations(userId) {
    return request("GET", `/history/conversations?user_id=${userId}`);
  },
  getMessages(sessionId, limit = 50) {
    return request("GET", `/history/messages?session_id=${sessionId}&limit=${limit}`);
  },
  deleteConversation(id) {
    return request("DELETE", `/history/conversations/${id}`);
  },

  // ── SSE Streaming ──
  createChatStream(query, sessionId, onMessage, onDone, onError) {
    const url = `${BASE}/chat/stream?query=${encodeURIComponent(query)}&session_id=${encodeURIComponent(sessionId)}`;
    const es = new EventSource(url);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "done") { es.close(); onDone?.(); return; }
        onMessage?.(data);
      } catch (err) { /* ignore */ }
    };
    es.onerror = (e) => { es.close(); onError?.(e); };
    return es;
  },
};
