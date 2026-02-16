#!/usr/bin/env python3
"""
MusicMap CLI - Find open mic events near you.
"""

import argparse
import json
from pathlib import Path

from .aggregator import OpenMicAggregator, display_events
from .geo import parse_location


def main():
    parser = argparse.ArgumentParser(
        description="Find open mic events from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.musicmap.main                              # Prompts for location
  python -m src.musicmap.main -l "Chattahoochee, FL"       # Search from location
  python -m src.musicmap.main -l "Marianna, FL" -r 50      # Within 50 miles
  python -m src.musicmap.main -l "Dothan, AL" --group distance
        """
    )

    parser.add_argument(
        "--location", "-l",
        type=str,
        default=None,
        help="Your current location as 'City, ST' (e.g., 'Chattahoochee, FL')"
    )

    parser.add_argument(
        "--radius", "-r",
        type=float,
        default=None,
        help="Search radius in miles (default: from config or 100)"
    )

    parser.add_argument(
        "--city", "-c",
        type=str,
        action="append",
        help="City to search (can be specified multiple times)"
    )

    parser.add_argument(
        "--state", "-s",
        type=str,
        action="append",
        help="State for corresponding city (use with --city)"
    )

    parser.add_argument(
        "--group", "-g",
        type=str,
        choices=["day", "distance", "flat"],
        default="day",
        help="How to group results (default: day)"
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Location is required - prompt if not provided
    location_str = args.location
    if not location_str:
        location_str = input("Where are you? (City, ST): ").strip()

    location = parse_location(location_str)
    if not location:
        print(f"Error: Could not resolve location '{location_str}'")
        print("Format should be 'City, ST' (e.g., 'Chattahoochee, FL')")
        print("\nKnown locations: Chattahoochee FL, Tallahassee FL, Marianna FL,")
        print("  Panama City FL, Dothan AL, Bainbridge GA, Albany GA, Atlanta GA")
        return

    # Initialize aggregator
    aggregator = OpenMicAggregator(config_path=args.config)

    # Build cities list if specified on command line
    cities = None
    if args.city:
        cities = []
        states = args.state or []
        for i, city in enumerate(args.city):
            state = states[i] if i < len(states) else ""
            cities.append({"city": city, "state": state})

    # Search with location override if provided
    events = aggregator.search(cities=cities, max_distance=args.radius, location=location)

    # Output
    if args.json:
        output = [e.to_dict() for e in events]
        print(json.dumps(output, indent=2, default=str))
    else:
        display_events(events, group_by=args.group)


if __name__ == "__main__":
    main()
