from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class OrderApproved:
    """Fact emitted after an order successfully transitions to APPROVED."""

    order_id: str
    customer_id: str
    total: float
    occurred_at: datetime

    @classmethod
    def create(
        cls,
        order_id: str,
        customer_id: str,
        total: float,
    ) -> "OrderApproved":
        return cls(
            order_id=order_id,
            customer_id=customer_id,
            total=total,
            occurred_at=datetime.now(timezone.utc),
        )
