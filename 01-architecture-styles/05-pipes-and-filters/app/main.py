from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.filters.normalization import NormalizationFilter
from app.filters.persistence import PersistenceFilter
from app.filters.totals import CalculateTotalFilter
from app.filters.validation import ValidationFilter
from app.models import DraftItem, PipelineError, ProcessingContext
from app.pipeline import Pipeline
from app.repository import InMemoryProcessedOrderRepository


repository = InMemoryProcessedOrderRepository()

pipeline = Pipeline(
    [
        ValidationFilter(),
        NormalizationFilter(),
        CalculateTotalFilter(),
        PersistenceFilter(repository),
    ]
)

app = FastAPI(
    title="Software Architecture Lab - Pipes & Filters",
    version="1.0.0",
    description=(
        "Order draft processing implemented as a sequence of independent filters."
    ),
)


class DraftItemRequest(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class ProcessOrderRequest(BaseModel):
    customer_id: str
    items: list[DraftItemRequest]


class ProcessedItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class ProcessedOrderResponse(BaseModel):
    id: str
    customer_id: str
    status: str
    items: list[ProcessedItemResponse]
    total: float
    trace: list[str]


def to_response(context: ProcessingContext) -> ProcessedOrderResponse:
    if context.order_id is None:
        raise ValueError("processed context must contain an order id")

    return ProcessedOrderResponse(
        id=context.order_id,
        customer_id=context.customer_id,
        status=context.status,
        items=[
            ProcessedItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in context.items
        ],
        total=context.total,
        trace=context.trace,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "architecture": "pipes-and-filters",
        "message": "Open /docs to execute the order-processing pipeline.",
    }


@app.get("/pipeline")
def pipeline_definition() -> dict[str, list[str]]:
    return {
        "filters": [filter_.name for filter_ in pipeline.filters]
    }


@app.post(
    "/orders/process",
    response_model=ProcessedOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_order(request: ProcessOrderRequest) -> ProcessedOrderResponse:
    context = ProcessingContext(
        customer_id=request.customer_id,
        items=[
            DraftItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in request.items
        ],
    )

    try:
        processed = pipeline.execute(context)
    except PipelineError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return to_response(processed)


@app.get(
    "/orders/{order_id}",
    response_model=ProcessedOrderResponse,
)
def get_processed_order(order_id: str) -> ProcessedOrderResponse:
    order = repository.find_by_id(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"order {order_id} was not found",
        )

    return to_response(order)
