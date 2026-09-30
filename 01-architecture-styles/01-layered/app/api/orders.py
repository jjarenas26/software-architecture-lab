from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.domain.order import DomainError, Order
from app.repositories.order_repository import InMemoryOrderRepository
from app.services.order_service import OrderNotFoundError, OrderService
from app.services.secondary_services import AnalyticsService, NotificationService


router = APIRouter(prefix="/orders", tags=["orders"])

repository = InMemoryOrderRepository()
order_service = OrderService(
    repository=repository,
    notification_service=NotificationService(),
    analytics_service=AnalyticsService(),
)


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)


class AddItemRequest(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)


class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    status: str
    items: list[OrderItemResponse]
    total: float


def to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status.value,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
        total=order.total,
    )


def translate_error(error: Exception) -> HTTPException:
    if isinstance(error, OrderNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    if isinstance(error, DomainError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected error",
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(request: CreateOrderRequest) -> OrderResponse:
    order = order_service.create_order(request.customer_id)
    return to_response(order)


@router.post(
    "/{order_id}/items",
    response_model=OrderResponse,
)
def add_item(order_id: str, request: AddItemRequest) -> OrderResponse:
    try:
        order = order_service.add_item(
            order_id=order_id,
            product_id=request.product_id,
            quantity=request.quantity,
            unit_price=request.unit_price,
        )
        return to_response(order)
    except (OrderNotFoundError, DomainError) as error:
        raise translate_error(error) from error


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(order_id: str) -> OrderResponse:
    try:
        return to_response(order_service.get_order(order_id))
    except OrderNotFoundError as error:
        raise translate_error(error) from error


@router.post(
    "/{order_id}/approve",
    response_model=OrderResponse,
)
def approve_order(order_id: str) -> OrderResponse:
    try:
        return to_response(order_service.approve_order(order_id))
    except (OrderNotFoundError, DomainError) as error:
        raise translate_error(error) from error


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancel_order(order_id: str) -> OrderResponse:
    try:
        return to_response(order_service.cancel_order(order_id))
    except (OrderNotFoundError, DomainError) as error:
        raise translate_error(error) from error
