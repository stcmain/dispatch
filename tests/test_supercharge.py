"""Unit tests for dispatch.core.supercharge."""

from __future__ import annotations

import pytest

from dispatch.core.supercharge import supercharge


pytestmark = pytest.mark.unit


_EXPECTED_STATS_KEYS = {
    "raw_input_tokens",
    "supercharged_tokens",
    "full_context_tokens",
    "tokens_saved",
    "savings_pct",
}


def test_output_shape(sample_routes: dict[str, dict], sample_cache: dict) -> None:
    result = supercharge("fix the site", "CODE", sample_routes, sample_cache)
    assert set(result.keys()) >= {
        "category",
        "raw_message",
        "supercharged_prompt",
        "agent",
        "cwd",
        "token_stats",
    }
    assert result["category"] == "CODE"
    assert result["raw_message"] == "fix the site"
    assert result["agent"] == sample_routes["CODE"]["agent"]
    assert "TASK" in result["supercharged_prompt"]


def test_token_stats_keys(sample_routes: dict[str, dict], sample_cache: dict) -> None:
    result = supercharge("draft caption", "CONTENT", sample_routes, sample_cache)
    stats = result["token_stats"]
    assert set(stats.keys()) == _EXPECTED_STATS_KEYS
    assert stats["raw_input_tokens"] >= 0
    assert stats["supercharged_tokens"] > 0
    assert stats["savings_pct"] >= 0


def test_unknown_category_falls_back_to_ops(
    sample_routes: dict[str, dict],
    sample_cache: dict,
) -> None:
    result = supercharge("ping", "NOT_A_CATEGORY", sample_routes, sample_cache)
    assert result["category"] == "OPS"
    assert result["agent"] == sample_routes["OPS"]["agent"]


def test_empty_cache_still_renders(sample_routes: dict[str, dict]) -> None:
    result = supercharge("hello", "OPS", sample_routes, {})
    assert "TASK" in result["supercharged_prompt"]
    assert result["token_stats"]["full_context_tokens"] >= 0
