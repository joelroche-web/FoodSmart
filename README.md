# FoodSmart Singapore 🍜

FoodSmart is a web application that recommends licensed food establishments in Singapore. It allows users to search food places by name, postcode, category, and recommendation mode.
The application uses Singapore government open data to provide searchable and ranked food establishments.

---

# Features

* Search food establishments by name or location
* Filter by category (Cafe, Bakery, Food Court, etc.)
* Recommendation ranking system
* Location-based distance filtering
* Uses real Singapore licensed food establishment dataset
* Clean web interface with recommendation cards

---

# Dataset

This project uses the **Licensed Eating Establishments dataset** from Singapore's open data portal.

Source:
[https://data.gov.sg](https://data.gov.sg)

The dataset contains:

* Business name
* Licence name
* Address
* Postcode
* Licence information
* Geographic coordinates

Total records: **34,000+ establishments**

---

# Tech Stack

Backend

* Python
* FastAPI
* GeoJSON dataset processing

Frontend

* React
* Vite
* CSS

Other

* Git
* GitHub

---

# How Recommendations Work

Each food establishment is assigned:

* Estimated rating
* Estimated price level
* Category classification
* Optional distance from user location

A recommendation score is calculated using:

```
Score = rating × weight + price factor − distance penalty
```

Users can choose different modes:

* Balanced
* Cheapest
* Closest
* Best Value

---

# Running the Project

## Backend

Navigate to backend folder:

```
cd backend
```

Create virtual environment:

```
python -m venv venv
```

Activate environment:

Windows:

```
venv\Scripts\activate
```

Install dependencies:

```
pip install fastapi uvicorn
```

Run server:

```
uvicorn app.main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

## Frontend

Navigate to frontend folder:

```
cd frontend
```

Install dependencies:

```
npm install
```

Run development server:

```
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

# Example API Endpoint

Example request:

```
GET /recommendations?q=ang mo kio&mode=balanced
```

Returns ranked food establishments matching the search query.

---

# Future Improvements

* Map view for restaurant locations
* Real Google ratings integration
* Machine learning recommendation engine
* User favourites and history
* Mobile responsive design improvements

---

# Author

Joel Roche

---

# License

This project is for personal purposes.
