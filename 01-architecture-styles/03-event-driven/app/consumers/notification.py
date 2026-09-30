from app.events.order_events import OrderApproved


class NotificationConsumer:
    def __call__(self, event: OrderApproved) -> None:
        print(
            f"[notification] Customer {event.customer_id}: "
            f"order {event.order_id} was approved."
        )
