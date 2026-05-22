"""URL canonicalization — the duplicate-detection key for ADR-002.

Two wines sharing the same normalized URL are considered the same SKU
(stock increments instead of creating a new row).
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

_ALLOWED_SCHEMES = frozenset({"http", "https"})
_REQUIRED_HOST_SUFFIX = "wine.com.br"


def normalize_wine_url(url: str) -> str:
    """Canonicalize a wine.com.br product URL.

    Steps (TechSpec "Integration Points → URL normalization"):

    1. Strip surrounding whitespace.
    2. Parse; reject non-http(s) schemes or hosts that don't end in
       ``wine.com.br``.
    3. Lowercase the host.
    4. Drop the query string and fragment.
    5. Strip a trailing slash from the path (but not from the root ``/``).
    6. Force the ``https`` scheme.

    Raises:
        ValueError: when the input is empty, non-string, has the wrong
            scheme, or points outside the ``wine.com.br`` domain.
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
    stripped = url.strip()
    if not stripped:
        raise ValueError("URL must not be empty")

    parts = urlsplit(stripped)

    scheme = parts.scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"unsupported URL scheme: {parts.scheme!r}")

    netloc = parts.netloc.lower()
    if not netloc:
        raise ValueError("URL is missing a host")

    host_only = netloc.split(":", 1)[0]
    if not (
        host_only == _REQUIRED_HOST_SUFFIX
        or host_only.endswith("." + _REQUIRED_HOST_SUFFIX)
    ):
        raise ValueError(f"host {host_only!r} is not on wine.com.br")

    path = parts.path
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    # Drop query and fragment by passing empty strings into urlunsplit.
    return urlunsplit(("https", netloc, path, "", ""))
