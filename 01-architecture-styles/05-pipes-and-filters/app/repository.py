from copy import deepcopy

from app.models import ProcessingContext


class InMemoryProcessedOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, ProcessingContext] = {}

    def save(self, context: ProcessingContext) -> None:
        if context.order_id is None:
            raise ValueError("order_id must exist before persistence")
        self._orders[context.order_id] = deepcopy(context)

    def find_by_id(self, order_id: str) -> ProcessingContext | None:
        order = self._orders.get(order_id)
        return deepcopy(order) if order is not None else None

    def clear(self) -> None:
        self._orders.clear()
