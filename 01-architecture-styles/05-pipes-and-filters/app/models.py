from dataclasses import dataclass, field


class PipelineError(Exception):
    """Base exception for pipeline failures."""


class ValidationError(PipelineError):
    pass


class FraudReviewRequired(PipelineError):
    pass


@dataclass
class DraftItem:
    product_id: str
    quantity: int
    unit_price: float


@dataclass
class ProcessingContext:
    customer_id: str
    items: list[DraftItem]
    total: float = 0.0
    order_id: str | None = None
    status: str = "DRAFT"
    trace: list[str] = field(default_factory=list)
