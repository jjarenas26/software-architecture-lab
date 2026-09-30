from app.domain.order import Order


class NotificationService:
    def notify_order_approved(self, order: Order) -> None:
        print(
            f"[notification] Customer {order.customer_id}: "
            f"order {order.id} was approved."
        )


class AnalyticsService:
    def track_order_approved(self, order: Order) -> None:
        print(
            f"[analytics] order_approved "
            f"order_id={order.id} total={order.total:.2f}"
        )
