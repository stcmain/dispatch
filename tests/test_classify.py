"""Unit tests for dispatch.core.classify."""

from __future__ import annotations

import pytest

from dispatch.core.classify import classify, load_keywords


pytestmark = pytest.mark.unit


def test_exact_match_single_category(sample_routes: dict[str, dict]) -> None:
    keywords = load_keywords(sample_routes)
    assert classify("draft a post for tomorrow", keywords) == "CONTENT"


def test_multi_match_highest_score_wins(sample_routes: dict[str, dict]) -> None:
    keywords = load_keywords(sample_routes)
    # "fix" + "build" + "site" → CODE gets 3 hits, CONTENT/OPS get 0
    assert classify("fix build the site right now", keywords) == "CODE"


def test_fallback_to_code(sample_routes: dict[str, dict]) -> None:
    keywords: dict[str, list[str]] = {cat: [] for cat in sample_routes}
    # No keywords present; fallback heuristic detects "run"
    assert classify("please run the thing", keywords) == "CODE"


def test_fallback_to_content(sample_routes: dict[str, dict]) -> None:
    keywords: dict[str, list[str]] = {cat: [] for cat in sample_routes}
    assert classify("please draft something", keywords) == "CONTENT"


def test_fallback_to_ops(sample_routes: dict[str, dict]) -> None:
    keywords: dict[str, list[str]] = {cat: [] for cat in sample_routes}
    assert classify("hello there friend", keywords) == "OPS"


def test_returns_uppercase_category() -> None:
    keywords = {"code": ["fix"], "content": ["draft"]}
    assert classify("fix it", keywords) == "CODE"
