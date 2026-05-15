import { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import LoginPage from "./components/LoginPage";
import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import RouteMap from "./components/RouteMap";
import { api, getToken, setToken } from "./api/client";

const WELCOME_MESSAGE = {
  role: "assistant",
  content: `您好！我是智慧旅行助手 \u{1F5FA}\u{FE0F}

我可以帮您：
- \u{1F4CD} 规划旅游路线
- \u{2600}\u{FE0F} 查询天气预报
- \u{1F686} 查询火车票和航班
- \u{1F5D3}\u{FE0F} 查看黄历吉日
- \u{1F3E8} 推荐酒店住宿
- \u{1F5BC}\u{FE0F} 展示景点图片

请告诉我您的旅行需求吧！`,
  spotCards: [],
};

export default function App() {
  // ── Auth ──
  const [user, setUser] = useState(null);

  // ── Chat ──
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => uuidv4().slice(0, 8));
  const [maxIterations, setMaxIterations] = useState(30);
  const [scenarioTypes, setScenarioTypes] = useState({});
  const [useStream, setUseStream] = useState(false);
  const [routeData, setRouteData] = useState(null);
  const chatRef = useRef(null);

  // ── Restore session on mount ──
  useEffect(() => {
    const saved = localStorage.getItem("jwt");
    if (saved) {
      setToken(saved);
      api.me().then((r) => {
        const u = r.data || r;
        if (u.user_id) {
          setUser({ userId: u.user_id, nickname: u.openid || `User ${u.user_id}` });
        }
      }).catch(() => localStorage.removeItem("jwt"));
    }
  }, []);

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages]);

  // ── Login / Logout ──
  const handleLogin = (userData) => {
    setUser(userData);
    setMessages([WELCOME_MESSAGE]);
    setSessionId(`u${userData.userId}_${uuidv4().slice(0, 4)}`);
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("jwt");
    setUser(null);
    setMessages([WELCOME_MESSAGE]);
    setSessionId(uuidv4().slice(0, 8));
    setScenarioTypes({});
    setRouteData(null);
  };

  // ── New Session (clear messages) ──
  const handleNewSession = async () => {
    const r = await api.newSession();
    const newSid = r.session_id || r.data?.session_id || uuidv4().slice(0, 8);
    setSessionId(newSid);
    setMessages([WELCOME_MESSAGE]);
    setScenarioTypes({});
    setRouteData(null);
  };

  // ── Send Message ──
  const handleSend = async (query) => {
    const userMsg = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setRouteData(null);

    try {
      const res = await api.chat(query, sessionId, user?.userId);
      const data = res.data || res;
      const spotCards = data.spot_cards || [];

      const assistantMsg = {
        role: "assistant",
        content: data.answer || "抱歉，无法生成回答。",
        spotCards: spotCards,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      if (data.scenario_type) {
        setScenarioTypes((prev) => ({ ...prev, [assistantMsg.content]: data.scenario_type }));
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `错误: ${err.message}`, spotCards: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    await api.clearSession(sessionId);
    setMessages([WELCOME_MESSAGE]);
    setScenarioTypes({});
    setRouteData(null);
  };

  const handleSelectSession = async (sid) => {
    setSessionId(sid);
    try {
      const res = await api.getMessages(sid);
      const msgs = (res.messages || []).map((m) => ({
        role: m.role,
        content: m.content,
        spotCards: [],
      }));
      setMessages([WELCOME_MESSAGE, ...msgs]);
      setRouteData(null);
    } catch (e) { /* ignore */ }
    // 刷新历史列表（Sidebar 会检测 sessionId 变化自动刷新）
  };

  // ── Auth Gate ──
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <>
      <Sidebar
        maxIterations={maxIterations}
        setMaxIterations={setMaxIterations}
        sessionId={sessionId}
        onNewSession={handleNewSession}
        onClear={handleClear}
        useStream={useStream}
        setUseStream={setUseStream}
        user={user}
        onLogout={handleLogout}
        onSelectSession={handleSelectSession}
      />
      <div className="main">
        <div className="header">
          <h1>{'\u{1F5FA}\u{FE0F}'} 智慧旅行助手</h1>
          <p>基于 LangGraph + MCP 的多 Agent 旅行规划系统 | Pexels 图片支持</p>
        </div>
        <div className="chat-container" ref={chatRef}>
          {messages.map((msg, i) => (
            <ChatMessage
              key={i}
              role={msg.role}
              content={msg.content}
              scenarioType={scenarioTypes[msg.content]}
              spotCards={msg.spotCards}
            />
          ))}
          {routeData && <RouteMap routeData={routeData} />}
          {loading && (
            <div className="message assistant">
              <div className="avatar">{"\u{1F5FA}\u{FE0F}"}</div>
              <div className="message-body">
                <div className="bubble">
                  <div className="typing-indicator">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </>
  );
}
