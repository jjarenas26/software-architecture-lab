import os

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.clients import (
    HttpInventoryClient,
    HttpNotificationClient,
    InventoryClient,
    NotificationClient,
    ProductUnavailableError,
    ServiceUnavailableError,
)
from app.domain import DomainError, Order
from app.repository import InMemoryOrderRepository
from app.service import OrderNotFoundError, OrderService


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


def create_app(
    inventory_client: InventoryClient | None = None,
    notification_client: NotificationClient | None = None,
    repository: InMemoryOrderRepository | None = None,
) -> FastAPI:
    repository = repository or InMemoryOrderRepository()

    inventory_client = inventory_client or HttpInventoryClient(
        os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8002")
    )
    notification_client = notification_client or HttpNotificationClient(
        os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8003")
    )

    order_service = OrderService(
        repository=repository,
        inventory_client=inventory_client,
        notification_client=notification_client,
    )

    application = FastAPI(
        title="Order Service",
        version="1.0.0",
        description="Public Order API for the Microservices Architecture example.",
    )

    application.state.repository = repository
    application.state.order_service = order_service

    def translate_error(error: Exception) -> HTTPException:
        if isinstance(error, OrderNotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )
        if isinstance(error, (DomainError, ProductUnavailableError)):
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(error),
            )
        if isinstance(error, ServiceUnavailableError):
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(error),
            )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error",
        )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "order-service"}

    @application.post(
        "/orders",
        response_model=OrderResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_order(request: CreateOrderRequest) -> OrderResponse:
        return to_response(order_service.create_order(request.customer_id))

    @application.post(
        "/orders/{order_id}/items",
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
        except (
            OrderNotFoundError,
            DomainError,
            ProductUnavailableError,
            ServiceUnavailableError,
        ) as error:
            raise translate_error(error) from error

    @application.get(
        "/orders/{order_id}",
        response_model=OrderResponse,
    )
    def get_order(order_id: str) -> OrderResponse:
        try:
            return to_response(order_service.get_order(order_id))
        except OrderNotFoundError as error:
            raise translate_error(error) from error

    @application.post(
        "/orders/{order_id}/approve",
        response_model=OrderResponse,
    )
    def approve_order(order_id: str) -> OrderResponse:
        try:
            return to_response(order_service.approve_order(order_id))
        except (
            OrderNotFoundError,
            DomainError,
            ServiceUnavailableError,
        ) as error:
            raise translate_error(error) from error

    @application.post(
        "/orders/{order_id}/cancel",
        response_model=OrderResponse,
    )
    def cancel_order(order_id: str) -> OrderResponse:
        try:
            return to_response(order_service.cancel_order(order_id))
        except (OrderNotFoundError, DomainError) as error:
            raise translate_error(error) from error

    return application


app = create_app()
