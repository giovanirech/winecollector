"""Shared test fixtures and environment setup."""

from __future__ import annotations

import os

# Ensure required settings exist before any test module imports
# winecollector.config or winecollector.database. The value below is a
# test-only placeholder that satisfies the SECRET_KEY length validator.
os.environ.setdefault("SECRET_KEY", "x" * 64)
os.environ.setdefault("ENVIRONMENT", "development")
