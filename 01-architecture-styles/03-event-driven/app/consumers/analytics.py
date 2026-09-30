from app.events.order_events import OrderApproved


class AnalyticsConsumer:
    def __call__(self, event: OrderApproved) -> None:
        print(
            f"[analytics] order_approved "
            f"order_id={event.order_id} total={event.total:.2f}"
        )
