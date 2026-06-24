"""INV-1 — subtotal(items) == Σ(price × qty) (Entity, Track B)."""

import pytest

from src.cart import subtotal


@pytest.mark.entity
def test_inv_1_single_item():
    """INV-1: 단일 품목 소계는 price × qty 이다."""
    assert subtotal([(10_000, 2)]) == 20_000


@pytest.mark.entity
def test_inv_1_multiple_items_ac3_subtotal():
    """INV-1: 복수 품목 소계는 각 price × qty 의 합이다 (AC-3 소계)."""
    assert subtotal([(12_000, 3), (30_000, 1)]) == 66_000


@pytest.mark.entity
def test_inv_1_empty_items():
    """INV-1: 빈 목록의 소계는 0 이다."""
    assert subtotal([]) == 0
