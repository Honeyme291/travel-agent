import ReactMarkdown from "react-markdown";

/**
 * 聊天消息 — 每个景点独立一个卡片单元
 * spotCards: [{name, images:[{url,url_small,url_medium,photographer,alt,source}], description}, ...]
 */
export default function ChatMessage({ role, content, scenarioType, spotCards }) {
  const isUser = role === "user";
  const hasCards = !isUser && spotCards && spotCards.length > 0;

  return (
    <div className={`message ${role}`}>
      <div className="avatar">{isUser ? "\u{1F464}" : "\u{1F5FA}\u{FE0F}"}</div>
      <div className="message-body">
        {!isUser && scenarioType && scenarioType !== "simple" && (
          <span className={`scenario-badge ${scenarioType}`}>
            {scenarioType === "multi_destination" ? "多目的地" : "复杂场景"}
          </span>
        )}

        {/* 文本回复 */}
        <div className="bubble">
          {isUser ? content : <ReactMarkdown>{content}</ReactMarkdown>}
        </div>

        {/* 每个景点独立一个卡片: 图片左 + 介绍右 */}
        {hasCards && (
          <div className="spot-cards-stack">
            {spotCards.map((spot, idx) => (
              <div key={idx} className="spot-card">
                {/* 左侧图片 */}
                <div className="spot-card-images">
                  {spot.images && spot.images.length > 0 ? (
                    <>
                      {/* 主图 */}
                      <img
                        className="spot-main-img"
                        src={spot.images[0].url}
                        alt={spot.images[0].alt || spot.name}
                      />
                      {/* 缩略图行 */}
                      {spot.images.length > 1 && (
                        <div className="spot-thumb-row">
                          {spot.images.slice(1, 4).map((img, i) => (
                            <img
                              key={i}
                              className="spot-thumb"
                              src={img.url_small || img.url_medium || img.url}
                              alt={img.alt || `${spot.name} ${i + 2}`}
                            />
                          ))}
                        </div>
                      )}
                      {/* 图片来源 */}
                      {spot.images[0].photographer && (
                        <span className="spot-image-credit">
                          {spot.images[0].source === "pexels" ? "Pexels" : ""}  {spot.images[0].photographer}
                        </span>
                      )}
                    </>
                  ) : (
                    <div className="spot-no-image">暂无图片</div>
                  )}
                </div>

                {/* 右侧介绍 */}
                <div className="spot-card-info">
                  <h4 className="spot-name">{spot.name}</h4>
                  <p className="spot-desc">{spot.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
