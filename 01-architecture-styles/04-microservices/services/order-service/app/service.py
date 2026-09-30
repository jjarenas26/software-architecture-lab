from app.clients import InventoryClient, NotificationClient
from app.domain import Order
from app.repository import InMemoryOrderRepository


class OrderNotFoundError(Exception):
    pass


class OrderService:
    def __init__(
        self,
        repository: InMemoryOrderRepository,
        inventory_client: InventoryClient,
        notification_client: NotificationClient,
    ) -> None:
        self.repository = repository
        self.inventory_client = inventory_client
        self.notification_client = notification_client

    def create_order(self, customer_id: str) -> Order:
        return self.repository.save(Order(customer_id=customer_id))

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

        # This is now a network-capable collaboration.
        self.inventory_client.ensure_available(product_id, quantity)

        order.add_item(product_id, quantity, unit_price)
        return self.repository.save(order)

    def approve_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        order.approve()
        self.repository.save(order)

        # Deliberately after persistence to expose partial-failure behavior.
        self.notification_client.notify_order_approved(
            order_id=order.id,
            customer_id=order.customer_id,
            total=order.total,
        )

        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        order.cancel()
        return self.repository.save(order)
