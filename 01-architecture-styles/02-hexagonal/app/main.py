from fastapi import FastAPI

from app.adapters.inbound.http.orders import create_orders_router
from app.adapters.outbound.analytics import ConsoleAnalyticsAdapter
from app.adapters.outbound.notification import ConsoleNotificationAdapter
from app.adapters.outbound.persistence import InMemoryOrderRepository
from app.application.services.order_service import OrderService


# Composition root: the only place where concrete adapters are wired.
repository = InMemoryOrderRepository()
notification_adapter = ConsoleNotificationAdapter()
analytics_adapter = ConsoleAnalyticsAdapter()

order_service = OrderService(
    repository=repository,
    notification_port=notification_adapter,
    analytics_port=analytics_adapter,
)

app = FastAPI(
    title="Software Architecture Lab - Hexagonal Architecture",
    version="1.0.0",
    description=(
        "Order Management implemented with Ports & Adapters. "
        "The HTTP contract is intentionally equivalent to the layered example."
    ),
)

app.include_router(create_orders_router(order_service))


@app.get("/")
def root() -> dict[str, str]:
    return {
        "architecture": "hexagonal",
        "message": "Open /docs to explore the Order Management API.",
    }
