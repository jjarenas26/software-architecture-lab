from fastapi import FastAPI

from app.api.orders import router as orders_router


app = FastAPI(
    title="Software Architecture Lab - Layered Architecture",
    version="1.0.0",
    description=(
        "Order Management implemented with a classic layered architecture. "
        "Use /docs to exercise the common API."
    ),
)

app.include_router(orders_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "architecture": "layered",
        "message": "Open /docs to explore the Order Management API.",
    }
