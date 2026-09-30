from app.domain.order import OrderStatus
from app.events.event_bus import InMemoryEventBus
from app.events.order_events import OrderApproved
from app.repositories.order_repository import InMemoryOrderRepository
from app.services.order_service import OrderService


class RecordingConsumer:
    def __init__(self) -> None:
        self.events: list[OrderApproved] = []

    def __call__(self, event: OrderApproved) -> None:
        self.events.append(event)


def test_new_loyalty_consumer_can_be_added_without_changing_producer() -> None:
    repository = InMemoryOrderRepository()
    event_bus = InMemoryEventBus()

    notification_consumer = RecordingConsumer()
    analytics_consumer = RecordingConsumer()
    loyalty_consumer = RecordingConsumer()

    event_bus.subscribe(OrderApproved, notification_consumer)
    event_bus.subscribe(OrderApproved, analytics_consumer)
    event_bus.subscribe(OrderApproved, loyalty_consumer)

    service = OrderService(
        repository=repository,
        event_bus=event_bus,
    )

    order = service.create_order("C001")
    service.add_item(order.id, "P001", 2, 25.5)
    approved = service.approve_order(order.id)

    assert approved.status is OrderStatus.APPROVED

    for consumer in (
        notification_consumer,
        analytics_consumer,
        loyalty_consumer,
    ):
        assert len(consumer.events) == 1
        assert consumer.events[0].order_id == order.id
        assert consumer.events[0].total == 51.0


def test_failed_approval_does_not_publish_order_approved() -> None:
    repository = InMemoryOrderRepository()
    event_bus = InMemoryEventBus()
    consumer = RecordingConsumer()
    event_bus.subscribe(OrderApproved, consumer)

    service = OrderService(
        repository=repository,
        event_bus=event_bus,
    )

    order = service.create_order("C001")

    try:
        service.approve_order(order.id)
    except Exception:
        pass

    assert consumer.events == []
