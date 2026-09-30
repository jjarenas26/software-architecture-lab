import pytest
from fastapi.testclient import TestClient

from app.main import app, repository


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_repository() -> None:
    repository.clear()


def create_order(customer_id: str = "C001") -> dict:
    response = client.post(
        "/orders",
        json={"customer_id": customer_id},
    )
    assert response.status_code == 201
    return response.json()


def add_item(order_id: str) -> dict:
    response = client.post(
        f"/orders/{order_id}/items",
        json={
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 25.5,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_create_order() -> None:
    order = create_order()
    assert order["customer_id"] == "C001"
    assert order["status"] == "CREATED"
    assert order["items"] == []
    assert order["total"] == 0


def test_add_item_updates_total() -> None:
    order = create_order()
    updated = add_item(order["id"])
    assert len(updated["items"]) == 1
    assert updated["items"][0]["subtotal"] == 51.0
    assert updated["total"] == 51.0


def test_get_order() -> None:
    order = create_order()
    response = client.get(f"/orders/{order['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_unknown_order_returns_404() -> None:
    response = client.get("/orders/does-not-exist")
    assert response.status_code == 404


def test_empty_order_cannot_be_approved() -> None:
    order = create_order()
    response = client.post(f"/orders/{order['id']}/approve")
    assert response.status_code == 409
    assert "empty order" in response.json()["detail"]


def test_order_can_be_approved() -> None:
    order = create_order()
    add_item(order["id"])
    response = client.post(f"/orders/{order['id']}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


def test_approved_order_cannot_receive_more_items() -> None:
    order = create_order()
    add_item(order["id"])
    client.post(f"/orders/{order['id']}/approve")

    response = client.post(
        f"/orders/{order['id']}/items",
        json={"product_id": "P002", "quantity": 1, "unit_price": 10},
    )
    assert response.status_code == 409


def test_order_can_be_cancelled() -> None:
    order = create_order()
    response = client.post(f"/orders/{order['id']}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancelled_order_cannot_be_approved() -> None:
    order = create_order()
    client.post(f"/orders/{order['id']}/cancel")
    response = client.post(f"/orders/{order['id']}/approve")
    assert response.status_code == 409
