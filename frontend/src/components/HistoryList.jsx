/**
 * 历史会话列表
 */
import { useState, useEffect } from "react";
import { api } from "../api/client";

export default function HistoryList({ userId, onSelect, activeSession }) {
  const [convs, setConvs] = useState([]);

  useEffect(() => {
    if (userId) {
      api.getConversations(userId).then((r) => setConvs(r.conversations || r.data?.conversations || []));
    }
  }, [userId]);

  if (!convs.length) return <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>暂无历史会话</p>;

  return (
    <ul style={{ listStyle: "none", fontSize: 13 }}>
      {convs.map((c) => (
        <li
          key={c.id}
          onClick={() => onSelect(c.session_id)}
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            borderRadius: 8,
            marginBottom: 4,
            background: activeSession === c.session_id ? "#dbeafe" : "transparent",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <span>{c.title || c.session_id}</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              api.deleteConversation(c.id).then(() =>
                setConvs((prev) => prev.filter((x) => x.id !== c.id))
              );
            }}
            style={{
              background: "none", border: "none", cursor: "pointer",
              color: "#94a3b8", fontSize: 12,
            }}
          >
            ✕
          </button>
        </li>
      ))}
    </ul>
  );
}
