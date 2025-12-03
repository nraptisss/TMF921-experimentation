"""
Intent Common Model (ICM) support for TMF921.

This module provides TM Forum Intent Common Model v3.6.0 compatibility,
enabling conversion between our simplified JSON format and TMF Forum's
ICM/TIO-based JSON-LD format.

Option B: Pragmatic Hybrid approach
- Keep current simple JSON as default format
- Provide ICM converter for TM Forum compliance
- Support dual output formats
"""

from .models import (
    ICMIntent,
    PropertyExpectation,
    DeliveryExpectation,
    ReportingExpectation,
    Target,
    Condition,
)
from .converter import SimpleToICMConverter, ICMToSimpleConverter

__all__ = [
    "ICMIntent",
    "PropertyExpectation",
    "DeliveryExpectation",
    "ReportingExpectation",
    "Target",
    "Condition",
    "SimpleToICMConverter",
    "ICMToSimpleConverter",
]
