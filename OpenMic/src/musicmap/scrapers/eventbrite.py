#!/usr/bin/env python3
"""
Eventbrite scraper for open mic events.
"""

from typing import List, Optional
from datetime import datetime
import re
import json

from .base import BaseScraper
from ..models.event import OpenMicEvent


class EventbriteScraper(BaseScraper):
    """Scraper for Eventbrite open mic events."""

    SOURCE_NAME = "eventbrite"
    BASE_URL = "https://www.eventbrite.com"

    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)

        # Apply session token if available
        eb_config = self.config.get("eventbrite", {})
        if eb_config.get("session_token"):
            self.session.cookies.set("SS", eb_config["session_token"])

    # Keywords that indicate an open mic event
    OPEN_MIC_KEYWORDS = [
        "open mic", "open-mic", "openmic",
        "poetry slam", "spoken word", "comedy night",
        "songwriter night", "acoustic night", "jam session",
        "karaoke", "talent show", "open stage"
    ]

    def search_url(self, city: str, state: str, query: str = "open-mic") -> str:
        """Build Eventbrite search URL."""
        # Eventbrite URL format: /d/state--city/query/
        state_lower = state.lower()
        city_lower = city.lower().replace(" ", "-")
        return f"{self.BASE_URL}/d/{state_lower}--{city_lower}/{query}/"

    def _is_open_mic_event(self, name: str) -> bool:
        """Check if event name suggests an open mic event."""
        name_lower = name.lower()
        return any(kw in name_lower for kw in self.OPEN_MIC_KEYWORDS)

    def scrape(self, city: str, state: str) -> List[OpenMicEvent]:
        """Scrape open mic events from Eventbrite for a city."""
        url = self.search_url(city, state)
        print(f"  Eventbrite: searching {city}, {state}...")

        soup = self.fetch_page(url)
        if not soup:
            return []

        events = []

        # Find event cards - Eventbrite uses various structures
        # Look for event links with data or structured content
        for card in soup.find_all("div", class_=re.compile(r"event-card|search-event-card", re.I)):
            event = self._parse_event_card(card, city, state)
            if event:
                events.append(event)

        # Also try finding events in script tags (JSON-LD)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        event = self._parse_jsonld_event(item, city, state)
                        if event:
                            events.append(event)
                elif isinstance(data, dict):
                    event = self._parse_jsonld_event(data, city, state)
                    if event:
                        events.append(event)
            except (json.JSONDecodeError, TypeError):
                continue

        # Try parsing from the main content area
        if not events:
            events = self._parse_search_results(soup, city, state)

        return events

    def _parse_event_card(self, card, city: str, state: str) -> Optional[OpenMicEvent]:
        """Parse an event card element."""
        # Try to find event name
        name_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"event-title|card-title", re.I))
        if not name_elem:
            name_elem = card.find(["h2", "h3"])

        if not name_elem:
            return None

        event_name = name_elem.get_text(strip=True)
        if not event_name or len(event_name) < 3:
            return None

        # Filter for open mic related events
        if not self._is_open_mic_event(event_name):
            return None

        # Get event URL
        url = None
        link = card.find("a", href=True)
        if link:
            href = link.get("href", "")
            if href.startswith("/"):
                url = f"{self.BASE_URL}{href}"
            elif href.startswith("http"):
                url = href

        # Try to find venue
        venue_name = event_name  # Default to event name
        venue_elem = card.find(class_=re.compile(r"venue|location", re.I))
        if venue_elem:
            venue_name = venue_elem.get_text(strip=True)

        # Try to find date/time
        date_elem = card.find(class_=re.compile(r"date|time|when", re.I))
        time_str = None
        day_of_week = None
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            time_str = self.parse_time(date_text)
            # Try to extract day
            day_match = re.search(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', date_text, re.I)
            if day_match:
                day_abbrev = day_match.group(1).lower()
                day_map = {
                    "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
                    "thu": "Thursday", "fri": "Friday", "sat": "Saturday", "sun": "Sunday"
                }
                day_of_week = day_map.get(day_abbrev)

        # Try to find address
        address = None
        addr_elem = card.find(class_=re.compile(r"address|location-address", re.I))
        if addr_elem:
            address = addr_elem.get_text(strip=True)

        return OpenMicEvent(
            venue_name=venue_name,
            event_name=event_name,
            city=city,
            state=state,
            source=self.SOURCE_NAME,
            day_of_week=day_of_week,
            time=time_str,
            address=address,
            url=url,
        )

    def _parse_jsonld_event(self, data: dict, city: str, state: str) -> Optional[OpenMicEvent]:
        """Parse JSON-LD structured event data."""
        if data.get("@type") != "Event":
            return None

        event_name = data.get("name", "")
        if not event_name:
            return None

        # Filter for open mic related events
        if not self._is_open_mic_event(event_name):
            return None

        # Get venue info
        location = data.get("location", {})
        venue_name = location.get("name", event_name)
        address_data = location.get("address", {})

        address = None
        if isinstance(address_data, dict):
            parts = [
                address_data.get("streetAddress", ""),
                address_data.get("addressLocality", ""),
                address_data.get("addressRegion", ""),
                address_data.get("postalCode", ""),
            ]
            address = ", ".join(p for p in parts if p)
        elif isinstance(address_data, str):
            address = address_data

        # Get coordinates
        geo = location.get("geo", {})
        lat = geo.get("latitude")
        lon = geo.get("longitude")

        # Get date/time
        start_date = data.get("startDate", "")
        time_str = None
        day_of_week = None
        event_date = None

        if start_date:
            try:
                dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                time_str = dt.strftime("%I:%M %p").lstrip("0")
                day_of_week = dt.strftime("%A")
                event_date = dt.date()
            except ValueError:
                pass

        return OpenMicEvent(
            venue_name=venue_name,
            event_name=event_name,
            city=city,
            state=state,
            source=self.SOURCE_NAME,
            address=address,
            day_of_week=day_of_week,
            time=time_str,
            event_date=event_date,
            url=data.get("url"),
            lat=lat,
            lon=lon,
        )

    def _parse_search_results(self, soup, city: str, state: str) -> List[OpenMicEvent]:
        """Fallback parser for search results page."""
        events = []

        # Look for any links that look like events
        for link in soup.find_all("a", href=re.compile(r"/e/", re.I)):
            event_name = link.get_text(strip=True)
            if not event_name or len(event_name) < 5:
                continue

            # Filter for open mic related events
            if not self._is_open_mic_event(event_name):
                continue

            href = link.get("href", "")
            url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

            # Try to get surrounding context for time/venue
            parent = link.find_parent(["div", "li", "article"])
            time_str = None
            if parent:
                text = parent.get_text(" ", strip=True)
                time_str = self.parse_time(text)

            events.append(OpenMicEvent(
                venue_name=event_name,
                event_name=event_name,
                city=city,
                state=state,
                source=self.SOURCE_NAME,
                time=time_str,
                url=url,
            ))

        return events


def main():
    """Test the Eventbrite scraper."""
    scraper = EventbriteScraper()

    print("Eventbrite Open Mic Scraper")
    print("=" * 50)

    # Test with Tallahassee (closest to Bainbridge)
    events = scraper.scrape("Tallahassee", "FL")

    print(f"\nFound {len(events)} events:")
    for event in events[:10]:  # Show first 10
        print(f"  - {event}")


if __name__ == "__main__":
    main()
