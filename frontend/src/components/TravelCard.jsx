/**
 * 旅行景点卡片 — 图片左侧 + 介绍右侧 的横向布局
 *
 * spot: {
 *   name: string,
 *   images: [{url, url_small, photographer, alt, source}, ...],
 *   description: string,
 * }
 */
export default function TravelCard({ spot }) {
  if (!spot) return null;

  const mainImage = spot.images?.[0];
  const thumbs = spot.images?.slice(1, 4) || [];

  return (
    <div className="travel-card">
      {/* 左侧: 图片区域 */}
      <div className="travel-card-images">
        {/* 主图 */}
        {mainImage?.url && (
          <div className="travel-card-main-image">
            <img
              src={mainImage.url}
              alt={mainImage.alt || spot.name}
              loading="lazy"
            />
            {mainImage.photographer && (
              <span className="image-credit">
                Photo by {mainImage.photographer}
                {mainImage.source ? ` (${mainImage.source})` : ""}
              </span>
            )}
          </div>
        )}

        {/* 缩略图 */}
        {thumbs.length > 0 && (
          <div className="travel-card-thumbs">
            {thumbs.map((img, i) => (
              <img
                key={i}
                src={img.url_small || img.url_medium || img.url}
                alt={img.alt || `${spot.name} ${i + 2}`}
                loading="lazy"
              />
            ))}
          </div>
        )}
      </div>

      {/* 右侧: 介绍与安排 */}
      <div className="travel-card-info">
        <h3>{spot.name}</h3>
        <p className="travel-card-desc">{spot.description}</p>

        {spot.travel_tips && (
          <div className="travel-card-tips">
            <h4>旅行小贴士</h4>
            <p>{spot.travel_tips}</p>
          </div>
        )}

        {spot.best_time && (
          <div className="travel-card-meta">
            <span>🕐 最佳时间: {spot.best_time}</span>
          </div>
        )}
      </div>
    </div>
  );
}
