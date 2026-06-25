"""INV-2 — amount ≥ 50000 → round(amount×0.9) / < 50000 → 그대로 (Entity, Track B)."""

import pytest

from src.cart import apply_threshold_discount


@pytest.mark.entity
def test_inv_2_threshold_inclusive():
    """INV-2: 50,000원 경계 포함 — 10% 할인 적용."""
    assert apply_threshold_discount(50_000) == 45_000


@pytest.mark.entity
def test_inv_2_below_threshold_no_discount():
    """INV-2: 50,000원 미만 — 할인 없음."""
    assert apply_threshold_discount(49_999) == 49_999
