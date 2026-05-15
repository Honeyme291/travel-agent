/**
 * 路线地图组件 — 展示高德静态地图
 */
export default function RouteMap({ routeData }) {
  if (!routeData || !routeData.static_url) {
    return (
      <div style={{
        height: 300, background: "#f1f5f9", borderRadius: 12,
        display: "flex", alignItems: "center", justifyContent: "center",
        color: "#94a3b8", fontSize: 14,
      }}>
        路线地图加载中...
      </div>
    );
  }

  return (
    <div style={{ marginBottom: 12, borderRadius: 12, overflow: "hidden", border: "1px solid var(--border)" }}>
      <img
        src={routeData.static_url}
        alt="Travel Route Map"
        style={{ width: "100%", height: "auto", display: "block" }}
      />
      <div style={{
        padding: "8px 12px", fontSize: 12, color: "var(--text-secondary)",
        background: "#fff", display: "flex", justifyContent: "space-between",
      }}>
        <span>起点: {routeData.origin}</span>
        <span>→</span>
        <span>终点: {routeData.destination}</span>
      </div>
    </div>
  );
}
