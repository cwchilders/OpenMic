#!/usr/bin/env python3
"""
Scraper for openmic.us - a directory of open mic events across the US.
"""

from typing import Optional, List
import re

from .base import BaseScraper
from ..models.event import OpenMicEvent


class OpenMicUSScraper(BaseScraper):
    """Scraper for openmic.us network of sites."""

    SOURCE_NAME = "openmic.us"
    BASE_URL = "https://www.openmic.us"

    CITY_DOMAINS = {
        "boston": "https://www.openmicboston.com",
        "newyork": "https://www.openmicnewyork.com",
        "chicago": "https://www.openmicchicago.com",
        "la": "https://www.openmicla.net",
        "austin": "https://www.openmicaustin.com",
        "nashville": "https://www.openmicnashville.com",
        "denver": "https://www.openmicdenver.com",
        "seattle": "https://www.openmicseattle.com",
        "portland": "https://www.openmicportland.com",
        "atlanta": "https://www.openmicatlanta.com",
        "panhandle": "https://www.openmicpanhandle.com",
        "jacksonville": "https://www.openmicjacksonville.com",
        "savannah": "https://www.openmicsavannah.com",
        "tallahassee": "https://www.openmictallahassee.com",
    }

    STATE_MAP = {
        "boston": "MA", "newyork": "NY", "chicago": "IL", "la": "CA",
        "austin": "TX", "nashville": "TN", "denver": "CO", "seattle": "WA",
        "portland": "OR", "atlanta": "GA", "phoenix": "AZ",
        "dallas": "TX", "houston": "TX", "miami": "FL",
        "panhandle": "FL", "jacksonville": "FL", "savannah": "GA",
        "tallahassee": "FL",
    }

    def get_main_page_links(self) -> dict:
        """Get all city/state links from the main page."""
        soup = self.fetch_page(self.BASE_URL)
        if not soup:
            return {}

        links = {}
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if text and ("openmic" in href.lower() or "open-mic" in href.lower()):
                links[text] = href

        return links

    def scrape(self, city: str, state: str = "") -> List[OpenMicEvent]:
        """Scrape events for a specific city (implements BaseScraper interface)."""
        return self.scrape_city(city)

    def scrape_city(self, city: str) -> List[OpenMicEvent]:
        """Scrape events for a specific city using AJAX endpoints."""
        city_lower = city.lower().replace(" ", "")

        if city_lower in self.CITY_DOMAINS:
            base_url = self.CITY_DOMAINS[city_lower]
        else:
            base_url = f"https://www.openmic{city_lower}.com"

        state = self.STATE_MAP.get(city_lower, "")

        # Day mapping for AJAX endpoints
        days = [
            (1, "mondiv", "Monday"),
            (2, "tuediv", "Tuesday"),
            (3, "weddiv", "Wednesday"),
            (4, "thudiv", "Thursday"),
            (5, "fridiv", "Friday"),
            (6, "satdiv", "Saturday"),
            (7, "sundiv", "Sunday"),
        ]

        all_events = []
        print(f"  OpenMic.US: scraping {city.title()}...")

        for day_num, day_div, day_name in days:
            url = f"{base_url}/events/frontlisting/{day_num}/{day_div}/1-2-3"
            soup = self.fetch_page(url)
            if not soup:
                continue

            events = self._parse_ajax_listings(soup, city.title(), state, day_name)
            all_events.extend(events)

        return all_events

    def _parse_ajax_listings(self, soup, city: str, state: str, day: str) -> List[OpenMicEvent]:
        """Parse venue listings from AJAX response HTML."""
        events = []

        # Navigation/junk items to skip
        skip_names = {
            "home", "austin", "open mic austin", "beatbuddy", "albuquerque",
            "alaska", "auckland, new zealand", "related links:", "traveling?",
            "open mics by u.s. cities:", "open mics by u.s. states:",
            "open mics by international cities:", "paid gigs for party bands",
            "corporate event bands, solo musicians, and djs"
        }

        # Find listing items - look for elements with time/phone patterns
        for container in soup.find_all(["div", "tr", "td"]):
            text = container.get_text(separator=" ", strip=True)

            # Must have a time pattern to be a valid venue listing
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[APap][Mm]|\d{1,2}\s*[APap][Mm])', text)
            if not time_match:
                continue

            # Look for venue name (bold/strong text or link)
            venue_name = None
            name_elem = container.find(["strong", "b"])
            if name_elem:
                venue_name = name_elem.get_text(strip=True)

            # Also check for links that might be venue names
            if not venue_name:
                link = container.find("a")
                if link:
                    venue_name = link.get_text(strip=True)

            if not venue_name or len(venue_name) < 3:
                continue

            # Skip navigation items
            if venue_name.lower() in skip_names:
                continue

            # Skip if name looks like a city/state
            if venue_name.lower() in self.CITY_DOMAINS:
                continue

            # Extract address
            address = self.parse_address(text)

            # Extract phone
            phone = self.parse_phone(text)

            time_str = time_match.group(1)

            # Avoid duplicates
            if not any(e.venue_name == venue_name for e in events):
                events.append(OpenMicEvent(
                    venue_name=venue_name,
                    city=city,
                    state=state,
                    source=self.SOURCE_NAME,
                    address=address,
                    day_of_week=day,
                    time=time_str,
                    phone=phone
                ))

        return events


def display_events(events: List[OpenMicEvent]):
    """Display events grouped by day of week."""
    if not events:
        print("No events found.")
        return

    # Group by day
    by_day = {}
    for event in events:
        day = event.day_of_week or "Unknown"
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(event)

    # Display in day order
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Unknown"]

    print(f"\nFound {len(events)} open mic events:\n")

    for day in day_order:
        if day not in by_day:
            continue
        print(f"{'=' * 50}")
        print(f"  {day.upper()}")
        print(f"{'=' * 50}")

        for event in by_day[day]:
            print(f"\n  {event.venue_name}")
            if event.time:
                print(f"    Time: {event.time}")
            if event.address:
                print(f"    Address: {event.address}")
            if event.phone:
                print(f"    Phone: {event.phone}")
            if event.distance_miles is not None:
                print(f"    Distance: {event.distance_miles} mi")
        print()


def main(city: str = "panhandle"):
    scraper = OpenMicUSScraper()

    print("OpenMic.US Scraper")
    print("=" * 50)

    events = scraper.scrape_city(city)
    display_events(events)


if __name__ == "__main__":
    import sys
    city = sys.argv[1] if len(sys.argv) > 1 else "panhandle"
    main(city)
