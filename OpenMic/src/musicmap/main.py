#!/usr/bin/env python3
"""
MusicMap CLI - Find open mic events near you.
"""

import argparse
import json
from pathlib import Path

from .aggregator import OpenMicAggregator, display_events


def main():
    parser = argparse.ArgumentParser(
        description="Find open mic events from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.musicmap.main                    # Search with default config
  python -m src.musicmap.main --radius 50        # Search within 50 miles
  python -m src.musicmap.main --city Tallahassee --state FL
  python -m src.musicmap.main --group distance   # Sort by distance instead of day
        """
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

    # Build cities list if specified on command line
    cities = None
    if args.city:
        cities = []
        states = args.state or []
        for i, city in enumerate(args.city):
            state = states[i] if i < len(states) else ""
            cities.append({"city": city, "state": state})

    # Initialize aggregator
    aggregator = OpenMicAggregator(config_path=args.config)

    # Search
    events = aggregator.search(cities=cities, max_distance=args.radius)

    # Output
    if args.json:
        output = [e.to_dict() for e in events]
        print(json.dumps(output, indent=2, default=str))
    else:
        display_events(events, group_by=args.group)


if __name__ == "__main__":
    main()
