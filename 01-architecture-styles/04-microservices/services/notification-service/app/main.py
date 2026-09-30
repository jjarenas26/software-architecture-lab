from fastapi import FastAPI, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    description="Owns customer notification processing for the microservices lab.",
)


class OrderApprovedNotification(BaseModel):
    order_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    total: float = Field(ge=0)


NOTIFICATIONS: list[OrderApprovedNotification] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "notification-service"}


@app.post(
    "/notifications/order-approved",
    status_code=status.HTTP_202_ACCEPTED,
)
def order_approved(
    notification: OrderApprovedNotification,
) -> dict[str, str]:
    NOTIFICATIONS.append(notification)

    print(
        f"[notification] Customer {notification.customer_id}: "
        f"order {notification.order_id} was approved "
        f"for total={notification.total:.2f}"
    )

    return {
        "status": "accepted",
        "order_id": notification.order_id,
    }


@app.get("/notifications")
def list_notifications() -> list[OrderApprovedNotification]:
    return NOTIFICATIONS
