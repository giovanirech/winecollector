"""Pure parsers for free-text fields on wine.com.br pages."""

from __future__ import annotations

import re

_INTEGER_PATTERN = re.compile(r"\d+")


def parse_aging_potential(text: str | None) -> int | None:
    """Extract the integer to store in ``Wine.aging_potential_years``.

    Heuristics (TechSpec "Integration Points → Aging-potential parser"):

    - ``None`` or empty → ``None``.
    - No digits in the string → ``None``.
    - Single integer → return it.
    - Two or more integers → return the maximum (so ``"10 a 15 anos"`` →
      ``15`` and ``"5-8 anos"`` → ``8``).
    """
    if text is None:
        return None

    matches = _INTEGER_PATTERN.findall(text)
    if not matches:
        return None

    integers = [int(m) for m in matches]
    return max(integers)
