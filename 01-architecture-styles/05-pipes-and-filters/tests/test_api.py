import pytest
from fastapi.testclient import TestClient

from app.main import app, repository


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository() -> None:
    repository.clear()


def test_pipeline_definition_is_visible() -> None:
    response = client.get("/pipeline")

    assert response.status_code == 200
    assert response.json()["filters"] == [
        "validate",
        "normalize",
        "calculate_total",
        "persist",
    ]


def test_order_draft_flows_through_filters_in_order() -> None:
    response = client.post(
        "/orders/process",
        json={
            "customer_id": " c001 ",
            "items": [
                {
                    "product_id": " p001 ",
                    "quantity": 2,
                    "unit_price": 25.5,
                }
            ],
        },
    )

    assert response.status_code == 201

    order = response.json()

    assert order["customer_id"] == "C001"
    assert order["items"][0]["product_id"] == "P001"
    assert order["total"] == 51.0
    assert order["status"] == "PROCESSED"
    assert order["trace"] == [
        "validate",
        "normalize",
        "calculate_total",
        "persist",
    ]


def test_processed_order_can_be_retrieved() -> None:
    processed = client.post(
        "/orders/process",
        json={
            "customer_id": "C001",
            "items": [
                {
                    "product_id": "P001",
                    "quantity": 1,
                    "unit_price": 10.0,
                }
            ],
        },
    ).json()

    response = client.get(f"/orders/{processed['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == processed["id"]


def test_invalid_draft_stops_pipeline_before_persistence() -> None:
    response = client.post(
        "/orders/process",
        json={
            "customer_id": "C001",
            "items": [],
        },
    )

    assert response.status_code == 422
    assert "at least one item" in response.json()["detail"]


def test_unknown_processed_order_returns_404() -> None:
    response = client.get("/orders/does-not-exist")

    assert response.status_code == 404
