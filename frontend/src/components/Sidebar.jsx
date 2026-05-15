import { useState, useEffect } from "react";
import { api } from "../api/client";
import HistoryList from "./HistoryList";

export default function Sidebar({
  maxIterations, setMaxIterations,
  sessionId, onNewSession, onClear,
  useStream, setUseStream,
  user, onLogout,
  onSelectSession,
}) {
  const [tools, setTools] = useState([]);
  const [servers, setServers] = useState([]);

  useEffect(() => {
    api.getTools().then((r) => setTools(r.data?.tools || r.tools || []));
    api.health().then((r) => setServers(r.data?.mcp_servers || r.mcp_servers || []));
  }, []);

  const historyKey = `${user?.userId || 0}_${sessionId}`;

  return (
    <aside className="sidebar">
      {/* 用户信息 */}
      <div className="sidebar-section">
        <h2>账户信息</h2>
        <div className="user-info">
          <div className="user-avatar">{"\u{1F464}"}</div>
          <div className="user-details">
            <div className="user-name">{user?.nickname || "未登录"}</div>
            <div className="user-id">ID: {user?.userId || "-"}</div>
          </div>
        </div>
        <button className="btn btn-logout" onClick={onLogout} style={{ marginTop: 8 }}>
          退出登录
        </button>
      </div>

      {/* 历史会话 */}
      <div className="sidebar-section">
        <h2>历史会话</h2>
        {user?.userId ? (
          <HistoryList
            key={historyKey}
            userId={user.userId}
            activeSession={sessionId}
            onSelect={onSelectSession}
          />
        ) : (
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            登录后可查看历史会话
          </p>
        )}
      </div>

      {/* 当前会话 */}
      <div className="sidebar-section">
        <h2>当前会话</h2>
        <div className="session-id-display">
          <code>{sessionId}</code>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn" onClick={onNewSession} style={{ flex: 1 }}>
            + 新会话
          </button>
          <button className="btn btn-danger" onClick={onClear} style={{ flex: 1 }}>
            清空
          </button>
        </div>
      </div>

      {/* 系统配置 */}
      <div className="sidebar-section">
        <h2>系统配置</h2>
        <label>最大迭代次数</label>
        <input
          type="range" min={10} max={100}
          value={maxIterations}
          onChange={(e) => setMaxIterations(Number(e.target.value))}
        />
        <div className="range-value">{maxIterations}</div>
      </div>

      {/* MCP 状态 */}
      <div className="sidebar-section">
        <h2>MCP 服务器</h2>
        <ul className="tool-list">
          {servers.map((s) => (
            <li key={s}><span className="status-dot" /> {s}</li>
          ))}
          {servers.length === 0 && <li style={{ color: "#f59e0b" }}>连接中...</li>}
        </ul>
      </div>

      {/* 工具列表 */}
      <div className="sidebar-section">
        <h2>可用工具 ({tools.length})</h2>
        <ul className="tool-list">
          {tools.map((t) => (
            <li key={t.name}>{t.name}</li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
