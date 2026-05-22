"""Exhaustive tests for ``normalize_wine_url`` — duplicate-detection key."""

from __future__ import annotations

import pytest

from winecollector.services.scraping.normalize import normalize_wine_url


def test_lowercases_host() -> None:
    assert (
        normalize_wine_url("https://WWW.WINE.COM.BR/x/prod1.html")
        == "https://www.wine.com.br/x/prod1.html"
    )


def test_strips_query_and_fragment() -> None:
    assert (
        normalize_wine_url(
            "https://www.wine.com.br/x/prod1.html?utm=email&ref=a#section"
        )
        == "https://www.wine.com.br/x/prod1.html"
    )


def test_strips_trailing_slash() -> None:
    assert (
        normalize_wine_url("https://www.wine.com.br/x/") == "https://www.wine.com.br/x"
    )


def test_preserves_root_path_slash() -> None:
    # The bare root ``/`` is kept; only path trailing slashes are stripped.
    assert normalize_wine_url("https://www.wine.com.br/") == "https://www.wine.com.br/"


def test_strips_surrounding_whitespace() -> None:
    assert (
        normalize_wine_url("   https://www.wine.com.br/x/prod1   ")
        == "https://www.wine.com.br/x/prod1"
    )


def test_forces_https_when_input_is_http() -> None:
    assert (
        normalize_wine_url("http://www.wine.com.br/x/prod1")
        == "https://www.wine.com.br/x/prod1"
    )


def test_accepts_apex_domain() -> None:
    assert (
        normalize_wine_url("https://wine.com.br/x/prod1")
        == "https://wine.com.br/x/prod1"
    )


def test_accepts_subdomain_under_wine_com_br() -> None:
    assert (
        normalize_wine_url("https://shop.wine.com.br/x/prod1")
        == "https://shop.wine.com.br/x/prod1"
    )


def test_round_trips_already_canonical_url() -> None:
    canonical = "https://www.wine.com.br/vinhos/casillero/prod16104.html"
    assert normalize_wine_url(canonical) == canonical


@pytest.mark.parametrize(
    "bad_url",
    [
        "https://example.com/x",
        "https://wine.com/x",
        "https://wine.com.br.evil.com/x",
        "https://faux-wine.com.br/x",  # dot-prefixed suffix check rejects
    ],
)
def test_rejects_non_wine_com_br_host(bad_url: str) -> None:
    with pytest.raises(ValueError, match="wine.com.br"):
        normalize_wine_url(bad_url)


@pytest.mark.parametrize(
    "bad_url",
    [
        "ftp://www.wine.com.br/x",
        "file:///etc/passwd",
        "javascript:alert(1)",
    ],
)
def test_rejects_non_http_scheme(bad_url: str) -> None:
    with pytest.raises(ValueError, match="scheme"):
        normalize_wine_url(bad_url)


def test_rejects_empty_string() -> None:
    with pytest.raises(ValueError, match="empty"):
        normalize_wine_url("   ")


def test_rejects_non_string_input() -> None:
    with pytest.raises(ValueError, match="string"):
        normalize_wine_url(None)  # type: ignore[arg-type]


def test_rejects_missing_host() -> None:
    with pytest.raises(ValueError):
        normalize_wine_url("https:///x/prod1")
