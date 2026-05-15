/**
 * 登录/注册页面 — 必须先登录才能使用聊天功能
 */
import { useState } from "react";
import { api, setToken } from "../api/client";

export default function LoginPage({ onLogin }) {
  const [tab, setTab] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let result;
      if (tab === "register") {
        result = await api.register(username, password, nickname || username);
      } else {
        result = await api.login(username, password);
      }

      const token = result.access_token || result.data?.access_token;
      const userId = result.user_id || result.data?.user_id;
      const nick = result.nickname || result.data?.nickname || username;

      setToken(token);
      onLogin({ userId, nickname: nick, token });
    } catch (err) {
      setError(err.message || "操作失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  const isLogin = tab === "login";

  return (
    <div className="login-overlay">
      <div className="login-card">
        {/* Header */}
        <div className="login-header">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="#2563eb">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
          <h1>智慧旅行助手</h1>
          <p>登录后开始规划您的旅行</p>
        </div>

        {/* Tabs */}
        <div className="login-tabs">
          <button
            className={isLogin ? "active" : ""}
            onClick={() => setTab("login")}
          >
            登录
          </button>
          <button
            className={!isLogin ? "active" : ""}
            onClick={() => setTab("register")}
          >
            注册
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="field">
            <label>用户名</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="输入用户名或昵称"
              required
              autoFocus
            />
          </div>

          {!isLogin && (
            <div className="field">
              <label>昵称（选填）</label>
              <input
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="显示名称"
              />
            </div>
          )}

          <div className="field">
            <label>密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isLogin ? "输入密码" : "设置密码"}
              required
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? (
              <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
            ) : isLogin ? (
              "登 录"
            ) : (
              "注 册"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
