#!/usr/bin/env python3
"""
Multi-source open mic aggregator.
Combines events from multiple sources, deduplicates, and filters by distance.
"""

import json
from pathlib import Path
from typing import List, Optional

from .models.event import OpenMicEvent
from .scrapers.openmic_us import OpenMicUSScraper
from .scrapers.eventbrite import EventbriteScraper
from .geo import filter_by_distance, get_city_coords


class OpenMicAggregator:
    """Aggregates open mic events from multiple sources."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "credentials.json"
        else:
            config_path = Path(config_path)

        self.config = {}
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)

        # Initialize scrapers
        self.scrapers = [
            OpenMicUSScraper(str(config_path)),
            EventbriteScraper(str(config_path)),
        ]

    def search(
        self,
        cities: Optional[List[dict]] = None,
        max_distance: Optional[float] = None,
        location: Optional[tuple] = None,
    ) -> List[OpenMicEvent]:
        """
        Search for open mic events.

        Args:
            cities: List of {"city": str, "state": str} dicts to search.
                   If None, uses config's search_cities.
            max_distance: Max distance in miles from home_location.
                         If None, uses config's max_distance_miles.
            location: Optional (city, state, lat, lon) tuple to override home_location.

        Returns:
            List of OpenMicEvent, deduplicated and sorted by distance.
        """
        # Get cities to search
        if cities is None:
            cities = self.config.get("search_cities", [])

        # Get distance filter
        if max_distance is None:
            max_distance = self.config.get("max_distance_miles", 100)

        # Get location (override or from config)
        if location:
            home_city, home_state, home_lat, home_lon = location
        else:
            home = self.config.get("home_location", {})
            home_city = home.get("city", "home")
            home_lat = home.get("lat")
            home_lon = home.get("lon")

        print(f"\nSearching for open mics within {max_distance} miles of {home_city}...\n")

        all_events = []

        # Scrape each city with appropriate scrapers
        for city_info in cities:
            city = city_info.get("city", "")
            state = city_info.get("state", "")

            if not city:
                continue

            for scraper in self.scrapers:
                # Only use openmic.us for cities that have known sites
                if scraper.SOURCE_NAME == "openmic.us":
                    if not city_info.get("openmic_us", False):
                        continue

                try:
                    events = scraper.scrape(city, state)
                    all_events.extend(events)
                except Exception as e:
                    print(f"  Error with {scraper.SOURCE_NAME} for {city}: {e}")

        # Deduplicate by venue name + day
        all_events = self._deduplicate(all_events)

        # Filter by distance
        if home_lat and home_lon:
            all_events = filter_by_distance(all_events, home_lat, home_lon, max_distance)

        print(f"\nFound {len(all_events)} events total after filtering.\n")

        return all_events

    def _deduplicate(self, events: List[OpenMicEvent]) -> List[OpenMicEvent]:
        """Remove duplicate events based on venue name + day."""
        seen = set()
        unique = []

        for event in events:
            # Create a key for deduplication
            key = (
                event.venue_name.lower().strip(),
                event.day_of_week or "",
                event.city.lower().strip(),
            )

            if key not in seen:
                seen.add(key)
                unique.append(event)

        return unique

    def search_nearby(self, radius_miles: float = 100) -> List[OpenMicEvent]:
        """Search for events near the configured home location."""
        return self.search(max_distance=radius_miles)


def display_events(events: List[OpenMicEvent], group_by: str = "day"):
    """Display events in a formatted way."""
    if not events:
        print("No events found.")
        return

    if group_by == "day":
        _display_by_day(events)
    elif group_by == "distance":
        _display_by_distance(events)
    else:
        _display_flat(events)


def _display_by_day(events: List[OpenMicEvent]):
    """Display events grouped by day of week."""
    by_day = {}
    for event in events:
        day = event.day_of_week or "Unknown"
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(event)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Unknown"]

    for day in day_order:
        if day not in by_day:
            continue

        print(f"\n{'=' * 60}")
        print(f"  {day.upper()}")
        print(f"{'=' * 60}")

        # Sort by distance within day
        day_events = sorted(
            by_day[day],
            key=lambda e: e.distance_miles if e.distance_miles is not None else float('inf')
        )

        for event in day_events:
            _print_event(event)


def _display_by_distance(events: List[OpenMicEvent]):
    """Display events sorted by distance."""
    print(f"\n{'=' * 60}")
    print(f"  EVENTS BY DISTANCE")
    print(f"{'=' * 60}")

    for event in events:
        _print_event(event)


def _display_flat(events: List[OpenMicEvent]):
    """Display events in a flat list."""
    for event in events:
        _print_event(event)


def _print_event(event: OpenMicEvent):
    """Print a single event."""
    print(f"\n  {event.venue_name}")
    if event.event_name and event.event_name != event.venue_name:
        print(f"    Event: {event.event_name}")
    if event.day_of_week:
        print(f"    Day: {event.day_of_week}")
    if event.time:
        print(f"    Time: {event.time}")
    if event.address:
        print(f"    Address: {event.address}")
    if event.city and event.state:
        print(f"    Location: {event.city}, {event.state}")
    if event.phone:
        print(f"    Phone: {event.phone}")
    if event.distance_miles is not None:
        print(f"    Distance: {event.distance_miles} mi")
    if event.url:
        print(f"    URL: {event.url}")
    print(f"    Source: {event.source}")


def main():
    """Test the aggregator."""
    aggregator = OpenMicAggregator()

    events = aggregator.search_nearby(radius_miles=150)
    display_events(events, group_by="day")


if __name__ == "__main__":
    main()
