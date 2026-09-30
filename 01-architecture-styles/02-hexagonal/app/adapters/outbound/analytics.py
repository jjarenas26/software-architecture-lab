from app.domain.order import Order


class ConsoleAnalyticsAdapter:
    """Outbound adapter; could later call an analytics platform."""

    def track_order_approved(self, order: Order) -> None:
        print(
            f"[analytics] order_approved "
            f"order_id={order.id} total={order.total:.2f}"
        )
