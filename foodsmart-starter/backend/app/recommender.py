from __future__ import annotations

from math import inf
from typing import Any


def normalize(value: float, lower: float, upper: float) -> float:
    if upper == lower:
        return 1.0
    return (value - lower) / (upper - lower)


def compute_score(item: dict[str, Any], mode: str) -> float:
    rating_score = item["rating"] / 5
    price_score = 1 - normalize(item["price_level"], 1, 4)
    distance_score = 1 - normalize(min(item["distance_km"], 15), 0, 15)
    popularity_score = min(item["review_count"] / 1000, 1)
    open_bonus = 0.08 if item["is_open_now"] else -0.12

    cuisine_match = 0.1 if item.get("cuisine_match", False) else 0
    dietary_match = 0.07 if item.get("dietary_match", False) else 0

    weights = {
        "cheapest": {
            "rating": 0.20,
            "price": 0.45,
            "distance": 0.18,
            "popularity": 0.07,
        },
        "closest": {
            "rating": 0.18,
            "price": 0.12,
            "distance": 0.50,
            "popularity": 0.10,
        },
        "balanced": {
            "rating": 0.32,
            "price": 0.20,
            "distance": 0.24,
            "popularity": 0.14,
        },
        "best_value": {
            "rating": 0.35,
            "price": 0.28,
            "distance": 0.14,
            "popularity": 0.13,
        },
    }

    selected = weights.get(mode, weights["balanced"])
    score = (
        rating_score * selected["rating"]
        + price_score * selected["price"]
        + distance_score * selected["distance"]
        + popularity_score * selected["popularity"]
        + cuisine_match
        + dietary_match
        + open_bonus
    )
    return round(score, 4)


def apply_filters(
    restaurants: list[dict[str, Any]],
    query: str,
    area: str | None,
    cuisine: str | None,
    budget: int | None,
    max_distance_km: float | None,
    dietary: list[str],
) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    chosen_area = (area or "").strip().lower()
    chosen_cuisine = (cuisine or "").strip().lower()
    chosen_dietary = {item.lower() for item in dietary}

    results: list[dict[str, Any]] = []
    for restaurant in restaurants:
        haystack = " ".join(
            [
                restaurant["name"],
                restaurant["area"],
                restaurant["address"],
                restaurant["cuisine"],
                " ".join(restaurant.get("tags", [])),
            ]
        ).lower()

        if q and q not in haystack:
            continue
        if chosen_area and restaurant["area"].lower() != chosen_area:
            continue
        if chosen_cuisine and restaurant["cuisine"].lower() != chosen_cuisine:
            continue
        if budget is not None and restaurant["price_level"] > budget:
            continue
        if max_distance_km is not None and restaurant["distance_km"] > max_distance_km:
            continue

        restaurant = dict(restaurant)
        restaurant["cuisine_match"] = bool(chosen_cuisine) and restaurant["cuisine"].lower() == chosen_cuisine
        dietary_tags = {tag.lower() for tag in restaurant.get("dietary", [])}
        restaurant["dietary_match"] = bool(chosen_dietary) and chosen_dietary.issubset(dietary_tags)
        if chosen_dietary and not chosen_dietary.issubset(dietary_tags):
            continue
        results.append(restaurant)
    return results


def rank_restaurants(restaurants: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    ranked = []
    for restaurant in restaurants:
        enriched = dict(restaurant)
        enriched["score"] = compute_score(enriched, mode)
        ranked.append(enriched)
    ranked.sort(key=lambda item: (-item["score"], item["distance_km"], item["price_level"]))
    return ranked
