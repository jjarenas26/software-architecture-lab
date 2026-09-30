from typing import Protocol

from app.domain.order import Order


class OrderRepository(Protocol):
    """Persistence capability required by the application."""

    def save(self, order: Order) -> Order: ...
    def find_by_id(self, order_id: str) -> Order | None: ...


class NotificationPort(Protocol):
    """Notification capability required by the application."""

    def notify_order_approved(self, order: Order) -> None: ...


class AnalyticsPort(Protocol):
    """Analytics capability required by the application."""

    def track_order_approved(self, order: Order) -> None: ...
