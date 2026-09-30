from app.application.ports.outbound import (
    AnalyticsPort,
    NotificationPort,
    OrderRepository,
)
from app.domain.order import Order


class OrderNotFoundError(Exception):
    """Raised when a requested order does not exist."""


class OrderService:
    """Application service implementing the OrderUseCases inbound port."""

    def __init__(
        self,
        repository: OrderRepository,
        notification_port: NotificationPort,
        analytics_port: AnalyticsPort,
    ) -> None:
        self.repository = repository
        self.notification_port = notification_port
        self.analytics_port = analytics_port

    def create_order(self, customer_id: str) -> Order:
        order = Order(customer_id=customer_id)
        return self.repository.save(order)

    def get_order(self, order_id: str) -> Order:
        order = self.repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"order {order_id} was not found")
        return order

    def add_item(
        self,
        order_id: str,
        product_id: str,
        quantity: int,
        unit_price: float,
    ) -> Order:
        order = self.get_order(order_id)
        order.add_item(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        return self.repository.save(order)

    def approve_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        order.approve()
        self.repository.save(order)

        self.notification_port.notify_order_approved(order)
        self.analytics_port.track_order_approved(order)

        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        order.cancel()
        return self.repository.save(order)
