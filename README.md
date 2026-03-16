# FoodSmart Starter

A polished starter project for a **Food Recommendation Web App** inspired by the interaction model of ParkSmart's optimizer flow. The source site shows a single-page optimizer with destination, duration, priority modes, and tabs like Find / Parked / Tracker / Saved. This starter adapts that structure into a Singapore-focused food recommendation experience with filters for area, cuisine, budget, dietary preferences, and recommendation modes. citeturn698781view0

## Stack
- **Backend:** FastAPI
- **Frontend:** React + Vite
- **Data:** Seeded JSON dataset for quick prototyping
- **Storage for saves/history:** browser localStorage

## Included features
- Search by keyword, area, and cuisine
- Budget and distance filters
- Dietary preference chips
- Recommendation modes:
  - Cheapest
  - Closest
  - Balanced
  - Best Value
- Saved places tab
- Visit tracker tab
- Weighted recommendation scoring in Python

## Project structure

```text
foodsmart-starter/
├── backend/
│   ├── app/
│   │   ├── data_loader.py
│   │   ├── main.py
│   │   └── recommender.py
│   ├── data/
│   │   └── restaurants.json
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ModeCard.jsx
│   │   │   └── RestaurantCard.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Run locally

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`

## Next upgrades you can add
1. Replace JSON with PostgreSQL or SQLite.
2. Add user accounts and real persistence.
3. Integrate Google Places, Yelp, or OneMap for live restaurant data.
4. Add map view and travel time calculations.
5. Add collaborative filtering or personalized ML recommendations.
6. Add restaurant detail pages and review summaries.

## Recommendation logic summary
The backend computes a weighted score using:
- rating
- price level
- distance
- popularity
- cuisine match
- dietary match
- open-now bonus

Each mode changes the scoring weights so the same data can produce different ranking behavior.
