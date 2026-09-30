from app.domain.order import Order
from app.events.event_bus import InMemoryEventBus
from app.events.order_events import OrderApproved
from app.repositories.order_repository import InMemoryOrderRepository


class OrderNotFoundError(Exception):
    """Raised when a requested order does not exist."""


class OrderService:
    """Coordinates order use cases and emits business events."""

    def __init__(
        self,
        repository: InMemoryOrderRepository,
        event_bus: InMemoryEventBus,
    ) -> None:
        self.repository = repository
        self.event_bus = event_bus

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

        self.event_bus.publish(
            OrderApproved.create(
                order_id=order.id,
                customer_id=order.customer_id,
                total=order.total,
            )
        )

        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        order.cancel()
        return self.repository.save(order)
