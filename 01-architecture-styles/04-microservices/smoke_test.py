"""Small end-to-end smoke test for the Docker Compose topology."""

import json
import urllib.error
import urllib.request


BASE_URL = "http://localhost:8001"


def request(method: str, path: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


order = request("POST", "/orders", {"customer_id": "C-SMOKE"})
order_id = order["id"]

order = request(
    "POST",
    f"/orders/{order_id}/items",
    {
        "product_id": "P001",
        "quantity": 2,
        "unit_price": 25.5,
    },
)

assert order["total"] == 51.0

order = request("POST", f"/orders/{order_id}/approve")
assert order["status"] == "APPROVED"

retrieved = request("GET", f"/orders/{order_id}")
assert retrieved["status"] == "APPROVED"

print(f"Smoke test passed for order {order_id}")
