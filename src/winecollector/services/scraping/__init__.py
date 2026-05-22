"""Scraping helpers — pure functions and the live scraper module.

This package intentionally has no imports from ``winecollector.models`` or
``winecollector.schemas`` so the helpers stay testable in isolation and
free of database/HTTP side effects.
"""

from __future__ import annotations

from winecollector.services.scraping.normalize import normalize_wine_url
from winecollector.services.scraping.parsers import parse_aging_potential

__all__ = ["normalize_wine_url", "parse_aging_potential"]
