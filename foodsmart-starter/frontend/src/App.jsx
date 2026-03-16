import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function ResultCard({ item }) {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <div>
          <h3>{item.business_name || "Unnamed Establishment"}</h3>
          <div className="badge-row">
            <span className="category-badge">
              {item.category || "Food Establishment"}
            </span>
          </div>
        </div>
        <div className="score-badge">Score: {item.score}</div>
      </div>

      <p><strong>Address:</strong> {item.address || "N/A"}</p>
      <p><strong>Licence Name:</strong> {item.licence_name || "N/A"}</p>
      <p><strong>Licence No:</strong> {item.licence_no || "N/A"}</p>
      <p><strong>Postcode:</strong> {item.postcode || "N/A"}</p>

      <div className="meta-row">
        <span>⭐ Rating: {item.rating}</span>
        <span>💲 Price Level: {item.price_level}</span>
        <span>
          📍 Distance:{" "}
          {item.distance_km !== null && item.distance_km !== undefined
            ? `${item.distance_km} km`
            : "N/A"}
        </span>
      </div>
    </div>
  );
}

function SavedCard({ item, onRemove }) {
  return (
    <div className="result-card">
      <div className="result-card-header">
        <div>
          <h3>
            {item.business_name && item.business_name.trim() !== "."
            ? item.business_name
            : item.licence_name || "Unnamed Establishment"}
          </h3>
          <p className="muted">{item.category || "Food Establishment"}</p>
        </div>
        <button className="secondary-btn" onClick={() => onRemove(item.id)}>
          Remove
        </button>
      </div>

      <p><strong>Address:</strong> {item.address || "N/A"}</p>
      <div className="meta-row">
        <span>⭐ Rating: {item.rating}</span>
        <span>💲 Price Level: {item.price_level}</span>
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState("find");
  const [categories, setCategories] = useState([]);
  const [results, setResults] = useState([]);
  const [saved, setSaved] = useState(() => {
    const existing = localStorage.getItem("foodsmart_saved");
    return existing ? JSON.parse(existing) : [];
  });

  const [form, setForm] = useState({
    q: "",
    postcode: "",
    category: "",
    mode: "balanced",
    max_distance_km: "",
    user_lat: "",
    user_lon: "",
    limit: 20,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState("Checking backend...");

  useEffect(() => {
    localStorage.setItem("foodsmart_saved", JSON.stringify(saved));
  }, [saved]);

  useEffect(() => {
    checkBackend();
    fetchCategories();
  }, []);

  const savedIds = useMemo(() => new Set(saved.map((item) => item.id)), [saved]);

  async function checkBackend() {
    try {
      const response = await fetch(`${API_BASE}/`);
      if (!response.ok) {
        throw new Error("Backend not reachable.");
      }

      const data = await response.json();
      setApiStatus(
        `Backend connected. ${data.records_loaded ?? 0} records loaded.`
      );
    } catch (err) {
      setApiStatus("Backend not connected.");
    }
  }

  async function fetchCategories() {
    try {
      const response = await fetch(`${API_BASE}/categories`);
      if (!response.ok) {
        throw new Error("Failed to fetch categories.");
      }

      const data = await response.json();
      setCategories(data.categories || []);
    } catch (err) {
      console.error(err);
    }
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  async function handleSearch(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();

      if (form.q.trim()) params.append("q", form.q.trim());
      if (form.postcode.trim()) params.append("postcode", form.postcode.trim());
      if (form.category.trim()) params.append("category", form.category.trim());
      if (form.mode.trim()) params.append("mode", form.mode.trim());
      if (form.max_distance_km !== "") {
        params.append("max_distance_km", form.max_distance_km);
      }
      if (form.user_lat !== "") params.append("user_lat", form.user_lat);
      if (form.user_lon !== "") params.append("user_lon", form.user_lon);
      if (form.limit) params.append("limit", form.limit);

      const response = await fetch(
        `${API_BASE}/recommendations?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch recommendations.");
      }

      const data = await response.json();
      setResults(data.results || []);
      setActiveTab("find");
    } catch (err) {
      console.error(err);
      setError("Could not load recommendations. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  function savePlace(item) {
    if (savedIds.has(item.id)) return;
    setSaved((prev) => [item, ...prev]);
  }

  function removeSaved(id) {
    setSaved((prev) => prev.filter((item) => item.id !== id));
  }

  function useMyLocation() {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported in this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setForm((prev) => ({
          ...prev,
          user_lat: position.coords.latitude.toFixed(6),
          user_lon: position.coords.longitude.toFixed(6),
        }));
        setError("");
      },
      () => {
        setError("Could not get your location.");
      }
    );
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">FoodSmart Singapore</p>
          <h1>Find food places smarter</h1>
          <p className="hero-text">
            Search licensed food establishments in Singapore by name, category,
            postcode, and recommendation mode.
          </p>
        </div>
        <div className="status-box">{apiStatus}</div>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === "find" ? "tab active" : "tab"}
          onClick={() => setActiveTab("find")}
        >
          Find
        </button>
        <button
          className={activeTab === "saved" ? "tab active" : "tab"}
          onClick={() => setActiveTab("saved")}
        >
          Saved ({saved.length})
        </button>
        <button
          className={activeTab === "tracker" ? "tab active" : "tab"}
          onClick={() => setActiveTab("tracker")}
        >
          Tracker
        </button>
      </nav>

      <main className="main-grid">
        <section className="search-panel">
          <h2>Search Filters</h2>

          <form onSubmit={handleSearch} className="search-form">
            <label>
              Search
              <input
                type="text"
                name="q"
                value={form.q}
                onChange={updateField}
                placeholder="e.g. OMU, 7 Eleven, Temasek"
              />
            </label>

            <label>
              Postcode
              <input
                type="text"
                name="postcode"
                value={form.postcode}
                onChange={updateField}
                placeholder="e.g. 38983"
              />
            </label>

            <label>
              Category
              <select
                name="category"
                value={form.category}
                onChange={updateField}
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Mode
              <select name="mode" value={form.mode} onChange={updateField}>
                <option value="balanced">Balanced</option>
                <option value="cheapest">Cheapest</option>
                <option value="closest">Closest</option>
                <option value="best_value">Best Value</option>
              </select>
            </label>

            <label>
              Max Distance (km)
              <input
                type="number"
                step="0.1"
                name="max_distance_km"
                value={form.max_distance_km}
                onChange={updateField}
                placeholder="Optional"
              />
            </label>

            <div className="location-row">
              <label>
                User Latitude
                <input
                  type="number"
                  step="any"
                  name="user_lat"
                  value={form.user_lat}
                  onChange={updateField}
                  placeholder="e.g. 1.2948"
                />
              </label>

              <label>
                User Longitude
                <input
                  type="number"
                  step="any"
                  name="user_lon"
                  value={form.user_lon}
                  onChange={updateField}
                  placeholder="e.g. 103.8576"
                />
              </label>
            </div>

            <button
              type="button"
              className="secondary-btn"
              onClick={useMyLocation}
            >
              Use My Location
            </button>

            <label>
              Result Limit
              <input
                type="number"
                name="limit"
                min="1"
                max="100"
                value={form.limit}
                onChange={updateField}
              />
            </label>

            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? "Loading..." : "Find Recommendations"}
            </button>
          </form>

          {error && <p className="error-text">{error}</p>}
        </section>

        <section className="results-panel">
          {activeTab === "find" && (
            <>
              <div className="section-header">
                <h2>Recommendations</h2>
                <p className="muted">{results.length} results shown</p>
              </div>

              {results.length === 0 ? (
                <div className="empty-state">
                  <p>No recommendations yet.</p>
                  <p className="muted">
                    Run a search to see food places from your dataset.
                  </p>
                </div>
              ) : (
                <div className="results-list">
                  {results.map((item) => (
                    <div key={item.id} className="card-wrapper">
                      <ResultCard item={item} />
                      <div className="card-actions">
                        <button
                          className="primary-btn"
                          disabled={savedIds.has(item.id)}
                          onClick={() => savePlace(item)}
                        >
                          {savedIds.has(item.id) ? "Saved" : "Save"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === "saved" && (
            <>
              <div className="section-header">
                <h2>Saved Places</h2>
                <p className="muted">{saved.length} saved</p>
              </div>

              {saved.length === 0 ? (
                <div className="empty-state">
                  <p>No saved places yet.</p>
                </div>
              ) : (
                <div className="results-list">
                  {saved.map((item) => (
                    <SavedCard key={item.id} item={item} onRemove={removeSaved} />
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === "tracker" && (
            <>
              <div className="section-header">
                <h2>Tracker</h2>
              </div>
              <div className="empty-state">
                <p>Tracker coming next.</p>
                <p className="muted">
                  Later, you can store visited places, preferences, and food history here.
                </p>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}