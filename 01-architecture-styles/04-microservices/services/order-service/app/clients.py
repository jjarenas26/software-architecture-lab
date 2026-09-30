from typing import Protocol

import httpx


class ServiceUnavailableError(Exception):
    """Raised when a required remote service cannot complete a request."""


class ProductUnavailableError(Exception):
    """Raised when inventory cannot satisfy an item request."""


class InventoryClient(Protocol):
    def ensure_available(self, product_id: str, quantity: int) -> None: ...


class NotificationClient(Protocol):
    def notify_order_approved(
        self,
        order_id: str,
        customer_id: str,
        total: float,
    ) -> None: ...


class HttpInventoryClient:
    def __init__(self, base_url: str, timeout_seconds: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def ensure_available(self, product_id: str, quantity: int) -> None:
        try:
            response = httpx.get(
                f"{self.base_url}/inventory/{product_id}",
                params={"quantity": quantity},
                timeout=self.timeout_seconds,
            )
        except httpx.RequestError as error:
            raise ServiceUnavailableError(
                "inventory-service is unavailable"
            ) from error

        if response.status_code == 404:
            raise ProductUnavailableError(
                f"product {product_id} does not exist in inventory"
            )

        if response.status_code >= 500:
            raise ServiceUnavailableError(
                "inventory-service failed while checking stock"
            )

        response.raise_for_status()
        payload = response.json()

        if not payload["available"]:
            raise ProductUnavailableError(
                f"insufficient stock for product {product_id}"
            )


class HttpNotificationClient:
    def __init__(self, base_url: str, timeout_seconds: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def notify_order_approved(
        self,
        order_id: str,
        customer_id: str,
        total: float,
    ) -> None:
        try:
            response = httpx.post(
                f"{self.base_url}/notifications/order-approved",
                json={
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "total": total,
                },
                timeout=self.timeout_seconds,
            )
        except httpx.RequestError as error:
            raise ServiceUnavailableError(
                "notification-service is unavailable"
            ) from error

        if response.status_code >= 500:
            raise ServiceUnavailableError(
                "notification-service failed while sending notification"
            )

        response.raise_for_status()
