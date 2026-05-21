"""Shared :class:`Jinja2Templates` instance.

Lives in its own module so routers and tests can import the same engine
without pulling in the whole ``main`` module (which would create an
import cycle once protected routers wire ``current_active_user``).
"""

from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

templates: Jinja2Templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
