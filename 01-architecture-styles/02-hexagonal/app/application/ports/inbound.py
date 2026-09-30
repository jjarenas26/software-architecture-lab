from typing import Protocol

from app.domain.order import Order


class OrderUseCases(Protocol):
    """Inbound port exposed by the application core."""

    def create_order(self, customer_id: str) -> Order: ...
    def get_order(self, order_id: str) -> Order: ...

    def add_item(
        self,
        order_id: str,
        product_id: str,
        quantity: int,
        unit_price: float,
    ) -> Order: ...

    def approve_order(self, order_id: str) -> Order: ...
    def cancel_order(self, order_id: str) -> Order: ...
