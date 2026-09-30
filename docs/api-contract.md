# Common API Contract

This contract defines the externally visible behavior that architectural implementations should preserve whenever applicable.

Base resource:

```text
/orders
```

## 1. Create an order

```http
POST /orders
Content-Type: application/json
```

Request:

```json
{
  "customer_id": "C001"
}
```

Example response:

```json
{
  "id": "O001",
  "customer_id": "C001",
  "status": "CREATED",
  "items": [],
  "total": 0
}
```

Expected status:

```text
201 Created
```

## 2. Add an item

```http
POST /orders/{order_id}/items
Content-Type: application/json
```

Request:

```json
{
  "product_id": "P001",
  "quantity": 2,
  "unit_price": 25.5
}
```

Example response:

```json
{
  "id": "O001",
  "customer_id": "C001",
  "status": "CREATED",
  "items": [
    {
      "product_id": "P001",
      "quantity": 2,
      "unit_price": 25.5,
      "subtotal": 51.0
    }
  ],
  "total": 51.0
}
```

## 3. Get an order

```http
GET /orders/{order_id}
```

Expected status:

```text
200 OK
```

If the order does not exist:

```text
404 Not Found
```

## 4. Approve an order

```http
POST /orders/{order_id}/approve
```

Example response:

```json
{
  "id": "O001",
  "customer_id": "C001",
  "status": "APPROVED",
  "items": [
    {
      "product_id": "P001",
      "quantity": 2,
      "unit_price": 25.5,
      "subtotal": 51.0
    }
  ],
  "total": 51.0
}
```

## 5. Cancel an order

```http
POST /orders/{order_id}/cancel
```

The resulting order status is:

```text
CANCELLED
```

## Error semantics

Implementations should use equivalent semantics for domain errors.

Examples:

- `404 Not Found` — unknown order
- `409 Conflict` — invalid state transition
- `422 Unprocessable Entity` — invalid request data

Exact framework-generated error payloads may differ, but the architectural comparison should not depend on those differences.

## Compatibility principle

The APIs are intentionally boring.

The interesting differences belong behind the API boundary:

```text
                    SAME API
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
    Layered        Hexagonal       Event-Driven
       │               │               │
       └───────────────┼───────────────┘
                       ▼
                 SAME BUSINESS
                   BEHAVIOR
```

Later implementations such as microservices may distribute this contract internally, but the class should still be able to exercise an equivalent user-facing workflow.
