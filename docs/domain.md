# Common Domain — Order Management

All architectural implementations in this repository solve the same small business problem.

## Goal

Manage customer orders while preserving enough business behavior to expose meaningful architectural trade-offs.

## Domain model

### Order

An order contains:

- `id`
- `customer_id`
- `status`
- `items`
- `total`

### OrderItem

An order item contains:

- `product_id`
- `quantity`
- `unit_price`
- `subtotal`

`subtotal = quantity × unit_price`

## Order states

```text
CREATED
  ├── APPROVED
  └── CANCELLED
```

An order starts in `CREATED`.

## Business rules

1. A new order starts with status `CREATED`.
2. An order can receive items only while it is `CREATED`.
3. Quantity must be greater than zero.
4. Unit price must be zero or greater.
5. The order total is the sum of all item subtotals.
6. An order can be approved only while it is `CREATED`.
7. An empty order cannot be approved.
8. An order can be cancelled only while it is `CREATED`.
9. Once approved or cancelled, the order cannot be modified.
10. Approving an order should make secondary reactions possible, such as:
   - notifying the customer;
   - updating analytics;
   - later adding loyalty processing without changing the business requirement itself.

## Common use cases

### UC-01 — Create Order

Input:

- `customer_id`

Output:

- newly created order

### UC-02 — Add Item

Input:

- `order_id`
- `product_id`
- `quantity`
- `unit_price`

Output:

- updated order

### UC-03 — Get Order

Input:

- `order_id`

Output:

- current order

### UC-04 — Approve Order

Input:

- `order_id`

Output:

- approved order

Architectural implementations may realize secondary reactions differently, but the externally visible order state must remain equivalent.

### UC-05 — Cancel Order

Input:

- `order_id`

Output:

- cancelled order

## Architectural invariants

The following should remain constant across implementations:

- business terminology;
- state transitions;
- validation rules;
- externally visible API semantics;
- functional test scenarios whenever technically applicable.

The implementation structure, dependency direction, communication model and deployment topology are intentionally allowed to change.

## Why this domain?

The domain is intentionally small. It contains enough behavior to discuss:

- separation of concerns;
- dependency direction;
- coupling;
- synchronous versus asynchronous communication;
- persistence abstractions;
- component boundaries;
- independent deployment;
- modifiability;
- testability;
- operational complexity.

The objective is not to build an e-commerce product. The objective is to make architecture observable.
