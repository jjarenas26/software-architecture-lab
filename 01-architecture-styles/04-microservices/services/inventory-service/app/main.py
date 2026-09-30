from fastapi import FastAPI, HTTPException, Query, status


app = FastAPI(
    title="Inventory Service",
    version="1.0.0",
    description="Owns product stock availability for the microservices lab.",
)

STOCK: dict[str, int] = {
    "P001": 100,
    "P002": 50,
    "P003": 0,
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "inventory-service"}


@app.get("/inventory/{product_id}")
def check_inventory(
    product_id: str,
    quantity: int = Query(gt=0),
) -> dict[str, str | int | bool]:
    if product_id not in STOCK:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"product {product_id} was not found",
        )

    stock = STOCK[product_id]

    print(
        f"[inventory] product_id={product_id} "
        f"requested={quantity} stock={stock}"
    )

    return {
        "product_id": product_id,
        "requested_quantity": quantity,
        "stock": stock,
        "available": stock >= quantity,
    }
