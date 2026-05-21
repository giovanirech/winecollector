from __future__ import annotations

import importlib

from fastapi import FastAPI


def test_app_imports() -> None:
    module = importlib.import_module("winecollector.main")
    assert isinstance(module.app, FastAPI)
    assert module.app.title == "WineCollector"
