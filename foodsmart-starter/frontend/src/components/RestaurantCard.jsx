function priceSymbols(level) {
  return '$'.repeat(level)
}

export default function RestaurantCard({ item, onSave, saved }) {
  return (
    <article className="restaurant-card">
      <img src={item.image_url} alt={item.name} className="restaurant-image" />
      <div className="restaurant-body">
        <div className="restaurant-topline">
          <div>
            <h3>{item.name}</h3>
            <p className="muted">{item.area} · {item.cuisine}</p>
          </div>
          <button className={`save-btn ${saved ? 'saved' : ''}`} onClick={() => onSave(item)}>
            {saved ? 'Saved' : 'Save'}
          </button>
        </div>

        <div className="pill-row">
          <span className="pill">⭐ {item.rating}</span>
          <span className="pill">{priceSymbols(item.price_level)}</span>
          <span className="pill">{item.distance_km} km</span>
          <span className={`pill ${item.is_open_now ? 'open' : 'closed'}`}>
            {item.is_open_now ? 'Open now' : 'Closed'}
          </span>
        </div>

        <p className="address">{item.address}</p>
        <p className="score-copy">Smart score: <strong>{item.score}</strong> · Avg spend ~ S${item.avg_price_sgd}</p>

        <div className="tag-row">
          {item.tags?.map((tag) => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      </div>
    </article>
  )
}
