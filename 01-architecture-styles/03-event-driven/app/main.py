from fastapi import FastAPI

from app.api.orders import create_orders_router
from app.consumers.analytics import AnalyticsConsumer
from app.consumers.notification import NotificationConsumer
from app.events.event_bus import InMemoryEventBus
from app.events.order_events import OrderApproved
from app.repositories.order_repository import InMemoryOrderRepository
from app.services.order_service import OrderService


repository = InMemoryOrderRepository()
event_bus = InMemoryEventBus()

event_bus.subscribe(OrderApproved, NotificationConsumer())
event_bus.subscribe(OrderApproved, AnalyticsConsumer())

order_service = OrderService(
    repository=repository,
    event_bus=event_bus,
)

app = FastAPI(
    title="Software Architecture Lab - Event-Driven Architecture",
    version="1.0.0",
    description=(
        "Order Management implemented with publish/subscribe business events. "
        "The HTTP contract is intentionally equivalent to the previous examples."
    ),
)

app.include_router(create_orders_router(order_service))


@app.get("/")
def root() -> dict[str, str]:
    return {
        "architecture": "event-driven",
        "message": "Open /docs to explore the Order Management API.",
    }
