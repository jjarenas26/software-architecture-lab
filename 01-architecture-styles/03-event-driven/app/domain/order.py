from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class DomainError(Exception):
    """Base exception for business-rule violations."""


class InvalidOrderStateError(DomainError):
    """Raised when an operation is invalid for the current order state."""


class EmptyOrderError(DomainError):
    """Raised when attempting to approve an order without items."""


class InvalidOrderItemError(DomainError):
    """Raised when an order item violates a business rule."""


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise InvalidOrderItemError("product_id cannot be empty")
        if self.quantity <= 0:
            raise InvalidOrderItemError("quantity must be greater than zero")
        if self.unit_price < 0:
            raise InvalidOrderItemError("unit_price cannot be negative")

    @property
    def subtotal(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Order:
    customer_id: str
    id: str = field(default_factory=lambda: f"O-{uuid4().hex[:8].upper()}")
    status: OrderStatus = OrderStatus.CREATED
    items: list[OrderItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.customer_id.strip():
            raise ValueError("customer_id cannot be empty")

    @property
    def total(self) -> float:
        return round(sum(item.subtotal for item in self.items), 2)

    def add_item(self, product_id: str, quantity: int, unit_price: float) -> None:
        self._ensure_created("add items")
        self.items.append(
            OrderItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
            )
        )

    def approve(self) -> None:
        self._ensure_created("approve the order")
        if not self.items:
            raise EmptyOrderError("an empty order cannot be approved")
        self.status = OrderStatus.APPROVED

    def cancel(self) -> None:
        self._ensure_created("cancel the order")
        self.status = OrderStatus.CANCELLED

    def _ensure_created(self, operation: str) -> None:
        if self.status is not OrderStatus.CREATED:
            raise InvalidOrderStateError(
                f"cannot {operation} when order status is {self.status.value}"
            )
