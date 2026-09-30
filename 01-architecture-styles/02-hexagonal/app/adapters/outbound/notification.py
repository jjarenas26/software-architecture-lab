from app.domain.order import Order


class ConsoleNotificationAdapter:
    """Outbound adapter; could later be replaced by email, SMS, etc."""

    def notify_order_approved(self, order: Order) -> None:
        print(
            f"[notification] Customer {order.customer_id}: "
            f"order {order.id} was approved."
        )
