#!/usr/bin/env python3
"""
Geographic utilities for distance filtering.
"""

import math
from typing import Optional, Tuple
import re


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    Returns distance in miles.
    """
    R = 3959  # Earth's radius in miles

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# Known city coordinates (expanded for SE US)
CITY_COORDS = {
    # Georgia
    ("bainbridge", "ga"): (30.9038, -84.5755),
    ("albany", "ga"): (31.5785, -84.1557),
    ("atlanta", "ga"): (33.7490, -84.3880),
    ("savannah", "ga"): (32.0809, -81.0912),
    ("valdosta", "ga"): (30.8327, -83.2785),
    ("thomasville", "ga"): (30.8366, -83.9788),

    # Florida
    ("tallahassee", "fl"): (30.4383, -84.2807),
    ("panama city", "fl"): (30.1588, -85.6602),
    ("jacksonville", "fl"): (30.3322, -81.6557),
    ("gainesville", "fl"): (29.6516, -82.3248),
    ("pensacola", "fl"): (30.4213, -87.2169),
    ("destin", "fl"): (30.3935, -86.4958),

    # Alabama
    ("dothan", "al"): (31.2232, -85.3905),
    ("montgomery", "al"): (32.3792, -86.3077),
    ("mobile", "al"): (30.6954, -88.0399),

    # Texas (for openmic.us sources)
    ("austin", "tx"): (30.2672, -97.7431),
    ("houston", "tx"): (29.7604, -95.3698),
    ("dallas", "tx"): (32.7767, -96.7970),
}


def get_city_coords(city: str, state: str) -> Optional[Tuple[float, float]]:
    """Get coordinates for a known city."""
    key = (city.lower().strip(), state.lower().strip())
    return CITY_COORDS.get(key)


def estimate_coords_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Try to extract city/state from address and return known coords.
    Returns None if location cannot be determined.
    """
    if not address:
        return None

    # Try to match "City, ST" or "City, ST ZIP" pattern
    match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})\s*\d*', address)
    if match:
        city = match.group(1).strip()
        state = match.group(2).strip()
        return get_city_coords(city, state)

    return None


def filter_by_distance(
    events: list,
    home_lat: float,
    home_lon: float,
    max_miles: float
) -> list:
    """
    Filter events by distance from home location.
    Updates distance_miles field on each event.
    Returns events within max_miles, sorted by distance.
    """
    filtered = []

    for event in events:
        # Try to get coordinates
        if event.lat and event.lon:
            lat, lon = event.lat, event.lon
        else:
            # Try from city/state
            coords = get_city_coords(event.city, event.state)
            if not coords:
                # Try from address
                coords = estimate_coords_from_address(event.address)
            if coords:
                lat, lon = coords
                event.lat = lat
                event.lon = lon
            else:
                # Can't determine location, include with unknown distance
                event.distance_miles = None
                filtered.append(event)
                continue

        # Calculate distance
        distance = haversine_distance(home_lat, home_lon, lat, lon)
        event.distance_miles = round(distance, 1)

        if distance <= max_miles:
            filtered.append(event)

    # Sort by distance (None values at end)
    filtered.sort(key=lambda e: e.distance_miles if e.distance_miles is not None else float('inf'))

    return filtered
