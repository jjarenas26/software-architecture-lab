from uuid import uuid4

from app.models import ProcessingContext
from app.repository import InMemoryProcessedOrderRepository


class PersistenceFilter:
    name = "persist"

    def __init__(self, repository: InMemoryProcessedOrderRepository) -> None:
        self.repository = repository

    def process(self, context: ProcessingContext) -> ProcessingContext:
        if context.order_id is None:
            context.order_id = f"O-{uuid4().hex[:8].upper()}"

        context.status = "PROCESSED"
        context.trace.append(self.name)
        self.repository.save(context)
        return context
