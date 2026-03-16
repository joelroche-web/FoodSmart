import json
import math
import re
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FoodSmart API", version="1.0.0")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load GeoJSON dataset
# -----------------------------
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "EatingEstablishments.geojson"

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset file not found: {DATA_FILE}")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

features = geojson_data.get("features", [])


# -----------------------------
# Helpers
# -----------------------------
def parse_description_table(description: str) -> Dict[str, str]:
    if not description:
        return {}

    text = unescape(description)

    pattern = re.compile(r"<th>(.*?)</th>\s*<td>(.*?)</td>", re.IGNORECASE | re.DOTALL)
    matches = pattern.findall(text)

    data = {}
    for key, value in matches:
        clean_key = re.sub(r"<.*?>", "", key).strip()
        clean_value = re.sub(r"<.*?>", "", value).strip()
        data[clean_key] = clean_value

    return data


def build_address(block: str, street: str, unit: str, postcode: str) -> str:
    parts = []

    if block:
        parts.append(block)
    if street:
        parts.append(street)
    if unit:
        parts.append(f"#{unit}")
    if postcode:
        parts.append(f"Singapore {postcode}")

    return " ".join(parts)


def safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


# -----------------------------
# Category detection
# -----------------------------
def infer_category(name: str, licence_name: str, street_name: str) -> str:
    text = f"{name} {licence_name} {street_name}".lower()

    if any(word in text for word in ["7 eleven", "seven eleven", "cheers", "mart", "mini mart"]):
        return "Convenience"

    if any(word in text for word in ["cafe", "coffee", "kopi", "toast"]):
        return "Cafe"

    if any(word in text for word in ["bakery", "bread", "cake", "pastry", "bengawan"]):
        return "Bakery"

    if any(word in text for word in ["sushi", "ramen", "ippudo"]):
        return "Japanese"

    if any(word in text for word in ["kimchi", "korean", "bbq"]):
        return "Korean"

    if any(word in text for word in ["biryani", "naan", "prata", "indian"]):
        return "Indian"

    if any(word in text for word in ["burger", "steak", "pasta", "western"]):
        return "Western"

    if any(word in text for word in ["laksa", "chicken rice", "nasi lemak"]):
        return "Local"

    if any(word in text for word in ["food court", "hawker", "koufu", "kopitiam", "kimly"]):
        return "Food Court"

    return "Food Establishment"


# -----------------------------
# Rating + price estimation
# -----------------------------
def stable_number_from_text(text: str) -> int:
    return sum((i + 1) * ord(c) for i, c in enumerate(text.lower()))


def estimate_price_level(category: str, business_name: str) -> int:
    seed = stable_number_from_text(f"{business_name}|{category}")

    if category in ["Convenience", "Food Court"]:
        return 1

    if category in ["Cafe", "Bakery", "Local"]:
        return 1 + (seed % 2)

    if category in ["Japanese", "Korean", "Western", "Indian"]:
        return 2 + (seed % 2)

    return 1 + (seed % 3)


def estimate_rating(category: str, business_name: str) -> float:
    seed = stable_number_from_text(f"{category}|{business_name}")

    if category in ["Japanese", "Cafe", "Bakery"]:
        base = 3.9
    elif category in ["Food Court", "Convenience"]:
        base = 3.5
    else:
        base = 3.7

    adjustment = (seed % 10) / 10
    return round(min(base + adjustment, 4.8), 1)


# -----------------------------
# Score calculation
# -----------------------------
def compute_score(rating: float, price_level: int, distance_km, mode: str) -> float:
    distance_penalty = distance_km if distance_km else 0

    if mode == "cheapest":
        return (5 - price_level) * 2.8 + rating * 1.4 - distance_penalty * 0.3

    if mode == "closest":
        return rating * 1.2 + (5 - price_level) * 0.6 - distance_penalty * 2

    if mode == "best_value":
        return rating * 2.2 + (5 - price_level) * 1.8 - distance_penalty * 0.5

    return rating * 2 + (5 - price_level) * 1.2 - distance_penalty * 0.8


# -----------------------------
# Data cleaning
# -----------------------------
def is_bad_business_name(name: str) -> bool:
    cleaned = (name or "").strip().lower()
    return cleaned in {"", ".", "-", "food", "nil", "n/a"}


# -----------------------------
# Transform dataset
# -----------------------------
restaurants: List[Dict[str, Any]] = []

for feature in features:

    props = feature.get("properties", {})
    description = props.get("Description", "")
    parsed = parse_description_table(description)

    coords = feature.get("geometry", {}).get("coordinates", [None, None])

    longitude = safe_float(coords[0])
    latitude = safe_float(coords[1])

    business_name = parsed.get("BUSINESS_NAME", "").strip()
    licence_name = parsed.get("LIC_NAME", "").strip()

    # CLEAN BAD BUSINESS NAMES
    if is_bad_business_name(business_name):
        business_name = licence_name if licence_name else "Unnamed Establishment"

    block_house = parsed.get("BLK_HOUSE", "").strip()
    street_name = parsed.get("STR_NAME", "").strip()
    unit_no = parsed.get("UNIT_NO", "").strip()
    postcode = parsed.get("POSTCODE", "").strip()

    category = infer_category(business_name, licence_name, street_name)

    price_level = estimate_price_level(category, business_name)
    rating = estimate_rating(category, business_name)

    restaurants.append(
        {
            "id": parsed.get("LIC_NO", "").strip(),
            "business_name": business_name,
            "licence_name": licence_name,
            "licence_no": parsed.get("LIC_NO", "").strip(),
            "block_house": block_house,
            "street_name": street_name,
            "unit_no": unit_no,
            "postcode": postcode,
            "address": build_address(block_house, street_name, unit_no, postcode),
            "latitude": latitude,
            "longitude": longitude,
            "category": category,
            "price_level": price_level,
            "rating": rating,
        }
    )


# -----------------------------
# API routes
# -----------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "records_loaded": len(restaurants)
    }


@app.get("/dataset-preview")
def dataset_preview(limit: int = 5):
    return {
        "count": len(restaurants),
        "sample": restaurants[:limit]
    }


@app.get("/categories")
def get_categories():
    categories = sorted({r["category"] for r in restaurants})
    return {"categories": categories}


@app.get("/recommendations")
def get_recommendations(
    q: str = "",
    postcode: str = "",
    category: str = "",
    mode: str = "balanced",
    max_distance_km: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    limit: int = 20,
):

    results = restaurants.copy()

    if q:
        q = q.lower()
        results = [
            r for r in results
            if q in r["business_name"].lower()
            or q in r["street_name"].lower()
            or q in r["address"].lower()
        ]

    if postcode:
        results = [r for r in results if r["postcode"] == postcode]

    if category:
        results = [r for r in results if category.lower() in r["category"].lower()]

    enriched = []

    for r in results:

        distance = None

        if user_lat and user_lon and r["latitude"] and r["longitude"]:
            distance = round(
                haversine(user_lat, user_lon, r["latitude"], r["longitude"]),
                2
            )

        record = r.copy()

        record["distance_km"] = distance

        record["score"] = round(
            compute_score(
                r["rating"],
                r["price_level"],
                distance,
                mode
            ),
            2
        )

        enriched.append(record)

    if max_distance_km:
        enriched = [
            r for r in enriched
            if r["distance_km"] and r["distance_km"] <= max_distance_km
        ]

    enriched.sort(key=lambda x: x["score"], reverse=True)

    return {
        "count": len(enriched),
        "mode": mode,
        "results": enriched[:limit]
    }