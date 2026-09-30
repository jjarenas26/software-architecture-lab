from app.application.services.order_service import OrderService
from app.domain.order import Order, OrderStatus


class FakeRepository:
    def __init__(self) -> None:
        self.orders: dict[str, Order] = {}

    def save(self, order: Order) -> Order:
        self.orders[order.id] = order
        return order

    def find_by_id(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)


class RecordingNotificationAdapter:
    def __init__(self) -> None:
        self.approved_order_ids: list[str] = []

    def notify_order_approved(self, order: Order) -> None:
        self.approved_order_ids.append(order.id)


class RecordingAnalyticsAdapter:
    def __init__(self) -> None:
        self.events: list[tuple[str, float]] = []

    def track_order_approved(self, order: Order) -> None:
        self.events.append((order.id, order.total))


def test_application_core_accepts_alternative_adapters() -> None:
    repository = FakeRepository()
    notifications = RecordingNotificationAdapter()
    analytics = RecordingAnalyticsAdapter()

    service = OrderService(
        repository=repository,
        notification_port=notifications,
        analytics_port=analytics,
    )

    order = service.create_order("C001")
    service.add_item(order.id, "P001", 2, 25.5)
    approved = service.approve_order(order.id)

    assert approved.status is OrderStatus.APPROVED
    assert notifications.approved_order_ids == [order.id]
    assert analytics.events == [(order.id, 51.0)]
