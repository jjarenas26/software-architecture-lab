from fastapi.testclient import TestClient

from app.clients import (
    ProductUnavailableError,
    ServiceUnavailableError,
)
from app.main import create_app
from app.repository import InMemoryOrderRepository


class FakeInventoryClient:
    def __init__(
        self,
        unavailable: bool = False,
        insufficient: bool = False,
    ) -> None:
        self.unavailable = unavailable
        self.insufficient = insufficient
        self.checks: list[tuple[str, int]] = []

    def ensure_available(self, product_id: str, quantity: int) -> None:
        self.checks.append((product_id, quantity))

        if self.unavailable:
            raise ServiceUnavailableError("inventory-service is unavailable")

        if self.insufficient:
            raise ProductUnavailableError(
                f"insufficient stock for product {product_id}"
            )


class FakeNotificationClient:
    def __init__(self, unavailable: bool = False) -> None:
        self.unavailable = unavailable
        self.notifications: list[tuple[str, str, float]] = []

    def notify_order_approved(
        self,
        order_id: str,
        customer_id: str,
        total: float,
    ) -> None:
        if self.unavailable:
            raise ServiceUnavailableError(
                "notification-service is unavailable"
            )

        self.notifications.append((order_id, customer_id, total))


def build_client(
    inventory: FakeInventoryClient | None = None,
    notification: FakeNotificationClient | None = None,
) -> tuple[TestClient, FakeInventoryClient, FakeNotificationClient]:
    inventory = inventory or FakeInventoryClient()
    notification = notification or FakeNotificationClient()
    repository = InMemoryOrderRepository()

    app = create_app(
        inventory_client=inventory,
        notification_client=notification,
        repository=repository,
    )

    return TestClient(app), inventory, notification


def create_order(client: TestClient, customer_id: str = "C001") -> dict:
    response = client.post(
        "/orders",
        json={"customer_id": customer_id},
    )
    assert response.status_code == 201
    return response.json()


def add_item(client: TestClient, order_id: str) -> dict:
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
    client, _, _ = build_client()
    order = create_order(client)

    assert order["customer_id"] == "C001"
    assert order["status"] == "CREATED"
    assert order["items"] == []
    assert order["total"] == 0


def test_add_item_checks_inventory_and_updates_total() -> None:
    client, inventory, _ = build_client()
    order = create_order(client)
    updated = add_item(client, order["id"])

    assert inventory.checks == [("P001", 2)]
    assert updated["items"][0]["subtotal"] == 51.0
    assert updated["total"] == 51.0


def test_get_order() -> None:
    client, _, _ = build_client()
    order = create_order(client)

    response = client.get(f"/orders/{order['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_unknown_order_returns_404() -> None:
    client, _, _ = build_client()

    response = client.get("/orders/does-not-exist")

    assert response.status_code == 404


def test_empty_order_cannot_be_approved() -> None:
    client, _, _ = build_client()
    order = create_order(client)

    response = client.post(f"/orders/{order['id']}/approve")

    assert response.status_code == 409


def test_order_can_be_approved_and_notifies_remote_service() -> None:
    client, _, notification = build_client()
    order = create_order(client)
    add_item(client, order["id"])

    response = client.post(f"/orders/{order['id']}/approve")

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
    assert notification.notifications == [
        (order["id"], "C001", 51.0)
    ]


def test_approved_order_cannot_receive_more_items() -> None:
    client, _, _ = build_client()
    order = create_order(client)
    add_item(client, order["id"])
    client.post(f"/orders/{order['id']}/approve")

    response = client.post(
        f"/orders/{order['id']}/items",
        json={
            "product_id": "P002",
            "quantity": 1,
            "unit_price": 10,
        },
    )

    assert response.status_code == 409


def test_order_can_be_cancelled() -> None:
    client, _, _ = build_client()
    order = create_order(client)

    response = client.post(f"/orders/{order['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancelled_order_cannot_be_approved() -> None:
    client, _, _ = build_client()
    order = create_order(client)
    client.post(f"/orders/{order['id']}/cancel")

    response = client.post(f"/orders/{order['id']}/approve")

    assert response.status_code == 409


def test_inventory_network_failure_becomes_503() -> None:
    inventory = FakeInventoryClient(unavailable=True)
    client, _, _ = build_client(inventory=inventory)
    order = create_order(client)

    response = client.post(
        f"/orders/{order['id']}/items",
        json={
            "product_id": "P001",
            "quantity": 2,
            "unit_price": 25.5,
        },
    )

    assert response.status_code == 503


def test_insufficient_inventory_becomes_409() -> None:
    inventory = FakeInventoryClient(insufficient=True)
    client, _, _ = build_client(inventory=inventory)
    order = create_order(client)

    response = client.post(
        f"/orders/{order['id']}/items",
        json={
            "product_id": "P001",
            "quantity": 200,
            "unit_price": 25.5,
        },
    )

    assert response.status_code == 409


def test_notification_failure_can_leave_order_approved() -> None:
    notification = FakeNotificationClient(unavailable=True)
    client, _, _ = build_client(notification=notification)

    order = create_order(client)
    add_item(client, order["id"])

    approval = client.post(f"/orders/{order['id']}/approve")

    assert approval.status_code == 503

    # The local transaction already committed before the network call failed.
    retrieved = client.get(f"/orders/{order['id']}")

    assert retrieved.status_code == 200
    assert retrieved.json()["status"] == "APPROVED"
