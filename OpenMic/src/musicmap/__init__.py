"""
MusicMap - Multi-source open mic event aggregator.
"""

from .models.event import OpenMicEvent
from .aggregator import OpenMicAggregator

__all__ = ["OpenMicEvent", "OpenMicAggregator"]
__version__ = "0.1.0"
