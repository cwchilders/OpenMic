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

    @staticmethod
    def extract_area_code(phone: str) -> str:
        """Extract 3-digit area code from phone number."""
        if not phone:
            return ""
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        # Handle +1 prefix
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        # Return first 3 digits
        return digits[:3] if len(digits) >= 3 else ""

    def is_local_area_code(self, phone: str) -> bool:
        """Check if phone number has a local area code per config."""
        filter_mode = self.config.get("filter_mode", "none")
        if filter_mode != "area_code":
            return True  # No filtering

        local_codes = self.config.get("local_area_codes", [])
        if not local_codes:
            return True  # No codes configured, allow all

        area_code = self.extract_area_code(phone)
        return area_code in local_codes

    def get_site_config(self, city: str) -> dict:
        """Get site URL and state from config for a city."""
        city_lower = city.lower().replace(" ", "")
        sites = self.config.get("openmic_us_sites", {})
        return sites.get(city_lower, {})

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
        site_config = self.get_site_config(city)

        if site_config:
            base_url = site_config.get("url")
            state = site_config.get("state", "")
        else:
            # Fallback for unknown cities
            city_lower = city.lower().replace(" ", "")
            base_url = f"https://www.openmic{city_lower}.com"
            state = ""

        if not base_url:
            print(f"  OpenMic.US: no site configured for {city}")
            return []

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

        # Filter by area code if configured
        filter_mode = self.config.get("filter_mode", "none")
        if filter_mode == "area_code":
            before_count = len(all_events)
            all_events = [e for e in all_events if self.is_local_area_code(e.phone)]
            filtered = before_count - len(all_events)
            if filtered > 0:
                print(f"    (filtered {filtered} non-local area codes)")

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

            # Skip if name looks like a configured city
            configured_sites = self.config.get("openmic_us_sites", {})
            if venue_name.lower() in configured_sites:
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
