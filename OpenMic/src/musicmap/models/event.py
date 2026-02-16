#!/usr/bin/env python3
"""
Unified event model for all open mic sources.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date


@dataclass
class OpenMicEvent:
    """Unified open mic event from any source."""
    venue_name: str
    city: str
    state: str
    source: str  # e.g., "openmic.us", "eventbrite"

    address: Optional[str] = None
    day_of_week: Optional[str] = None
    time: Optional[str] = None
    phone: Optional[str] = None
    genre: Optional[str] = None
    details: Optional[str] = None
    url: Optional[str] = None

    # Location data for distance filtering
    lat: Optional[float] = None
    lon: Optional[float] = None
    distance_miles: Optional[float] = None

    # Event-specific (for Eventbrite-style sources)
    event_date: Optional[date] = None
    event_name: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"{self.venue_name}"]
        if self.event_name and self.event_name != self.venue_name:
            parts[0] = f"{self.event_name} @ {self.venue_name}"
        if self.day_of_week:
            parts.append(f"{self.day_of_week}")
        if self.time:
            parts.append(f"{self.time}")
        if self.distance_miles is not None:
            parts.append(f"{self.distance_miles:.1f} mi")
        return " | ".join(parts)

    def to_dict(self) -> dict:
        return {
            "venue_name": self.venue_name,
            "event_name": self.event_name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "day_of_week": self.day_of_week,
            "time": self.time,
            "phone": self.phone,
            "genre": self.genre,
            "details": self.details,
            "url": self.url,
            "lat": self.lat,
            "lon": self.lon,
            "distance_miles": self.distance_miles,
            "source": self.source,
        }
