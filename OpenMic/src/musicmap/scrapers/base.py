#!/usr/bin/env python3
"""
Base scraper class with shared utilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path

from ..models.event import OpenMicEvent


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    SOURCE_NAME = "base"

    def __init__(self, config_path: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load configuration from JSON file."""
        if config_path is None:
            # Default config path
            config_path = Path(__file__).parent.parent / "config" / "credentials.json"
        else:
            config_path = Path(config_path)

        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}

    def fetch_page(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """Fetch and parse a page."""
        try:
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_json(self, url: str, **kwargs) -> Optional[dict]:
        """Fetch JSON data from URL."""
        try:
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error fetching JSON from {url}: {e}")
            return None

    @abstractmethod
    def scrape(self, city: str, state: str) -> List[OpenMicEvent]:
        """Scrape events for a given city/state. Must be implemented by subclasses."""
        pass

    # --- Shared parsing utilities ---

    @staticmethod
    def parse_phone(text: str) -> Optional[str]:
        """Extract phone number from text."""
        match = re.search(r'(\+?1?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})', text)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def parse_time(text: str) -> Optional[str]:
        """Extract time from text."""
        match = re.search(r'(\d{1,2}:\d{2}\s*[APap][Mm]|\d{1,2}\s*[APap][Mm])', text)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def parse_address(text: str) -> Optional[str]:
        """Extract address from text."""
        match = re.search(
            r'(\d+\s+[A-Za-z0-9\s\.]{3,30}(?:St|Dr|Rd|Ave|Blvd|Ln|Way|Ct|Pl)[\.]*,?\s+[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})',
            text
        )
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean up extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
