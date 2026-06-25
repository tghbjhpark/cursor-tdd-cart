"""UC-1, UC-2, UE-1 — Flask 주문 폼 Boundary 계약 (Track A)."""

import pytest

from src.app import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.mark.boundary
def test_uc_1_get_root_shows_qty_input(client):
    """UC-1: GET / → 200, 본문에 name=\"qty\" 입력이 있다."""
    response = client.get("/")
    assert response.status_code == 200
    assert 'name="qty"' in response.get_data(as_text=True)


@pytest.mark.boundary
def test_uc_2_post_calc_shows_final_total(client):
    """UC-2: POST /calc (price·qty·vip) → 본문에 final_total 결과가 있다."""
    response = client.post(
        "/calc",
        data={"price": "60000", "qty": "1", "vip": "on"},
    )
    assert "51300" in response.get_data(as_text=True)


@pytest.mark.boundary
def test_ue_1_post_calc_rejects_non_numeric_qty(client):
    """UE-1: qty가 숫자가 아니면 400 을 반환한다."""
    response = client.post(
        "/calc",
        data={"price": "60000", "qty": "abc"},
    )
    assert response.status_code == 400
