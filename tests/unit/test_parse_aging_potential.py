"""Table-driven tests for ``parse_aging_potential``."""

from __future__ import annotations

from winecollector.services.scraping.parsers import parse_aging_potential


def test_single_integer_returns_it() -> None:
    assert parse_aging_potential("5 anos") == 5


def test_range_returns_upper_bound() -> None:
    assert parse_aging_potential("10 a 15 anos") == 15


def test_dash_range_returns_upper_bound() -> None:
    assert parse_aging_potential("5-8 anos") == 8


def test_ate_n_anos_returns_n() -> None:
    assert parse_aging_potential("Até 8 anos") == 8


def test_non_numeric_returns_none() -> None:
    assert parse_aging_potential("Pronto para beber") is None


def test_consumir_jovem_returns_none() -> None:
    assert parse_aging_potential("Consumir jovem") is None


def test_none_input_returns_none() -> None:
    assert parse_aging_potential(None) is None


def test_empty_string_returns_none() -> None:
    assert parse_aging_potential("") is None


def test_whitespace_only_returns_none() -> None:
    assert parse_aging_potential("   ") is None


def test_handles_leading_text() -> None:
    assert parse_aging_potential("Potencial de guarda: 12 anos") == 12


def test_three_integers_returns_maximum() -> None:
    assert parse_aging_potential("entre 3, 5 ou 7 anos") == 7


def test_zero_is_a_valid_value() -> None:
    # Treat 0 as a legitimate integer extraction (caller decides semantics).
    assert parse_aging_potential("0 anos") == 0
