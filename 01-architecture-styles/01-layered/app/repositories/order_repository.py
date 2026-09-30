from app.domain.order import Order


class InMemoryOrderRepository:
    """Simple persistence implementation used to keep the lesson focused."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def save(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

    def find_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def clear(self) -> None:
        """Utility used by tests so each scenario starts with empty storage."""
        self._orders.clear()
