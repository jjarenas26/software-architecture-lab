# Class Demo Runbook — Architectural Styles

This runbook is designed for the live classroom demonstration of the **Software Architecture Lab**.

The objective is not merely to execute the code. In each step, make the architectural consequence visible.

---

# 0. Preparation before class

## Clone or update the repository

If you have not cloned it yet:

```bash
git clone https://github.com/jjarenas26/software-architecture-lab.git
cd software-architecture-lab
```

If it is already cloned:

```bash
cd software-architecture-lab
git pull
```

## Create one Python environment for the single-process examples

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r 01-architecture-styles/01-layered/requirements.txt
```

The same dependencies are sufficient for:

- Layered
- Hexagonal
- Event-Driven
- Pipes & Filters

Microservices uses Docker Compose.

## Verify Docker

```bash
docker --version
docker compose version
```

---

# 1. Layered Architecture

## Teaching objective

Make this flow visible:

```text
HTTP -> API -> Service -> Repository -> Data
                  |
                  +-> Notification
                  +-> Analytics
```

The key question is:

> How are responsibilities separated, and who depends directly on whom?

## 1.1 Run the tests

From the repository root:

```bash
cd 01-architecture-styles/01-layered
pytest -q
```

### What to highlight

- The business behavior is already protected by automated tests.
- These tests will remain conceptually equivalent in the next styles.
- Architecture can change while behavior remains stable.

Say:

> "These tests are our functional contract. We are going to change architecture, not business behavior."

## 1.2 Start the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Keep this terminal visible because Notification and Analytics write to the console.

## 1.3 Create an order

Using Swagger:

```text
POST /orders
```

Body:

```json
{
  "customer_id": "C001"
}
```

Or from another terminal:

```bash
ORDER_ID=$(curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C001"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')

echo $ORDER_ID
```

### What to highlight

- The API does not contain business rules.
- The API delegates to the service.
- The service coordinates the use case.

Open:

```text
app/api/orders.py
app/services/order_service.py
```

Ask:

> "Which layer knows about HTTP? Which layer knows the use case?"

## 1.4 Add an item

```bash
curl -s -X POST "http://localhost:8000/orders/$ORDER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id":"P001",
    "quantity":2,
    "unit_price":25.5
  }'
```

### What to highlight

The result should contain:

```text
total = 51.0
```

Open:

```text
app/domain/order.py
```

Point out that rules such as quantity validation and total calculation belong to the domain.

Ask:

> "Why would putting this calculation in the controller be a problem?"

## 1.5 Approve the order

```bash
curl -s -X POST "http://localhost:8000/orders/$ORDER_ID/approve"
```

Look at the server terminal.

You should see output similar to:

```text
[notification] ...
[analytics] ...
```

### What to highlight

Open:

```text
app/services/order_service.py
```

Show that `approve_order()` directly invokes Notification and Analytics.

Key observation:

```text
OrderService
   +--> NotificationService
   +--> AnalyticsService
```

Ask:

> "If tomorrow we add Loyalty, which class will probably have to change?"

Expected answer:

```text
OrderService
```

This is the first concrete discussion about **coupling** and **modifiability**.

## 1.6 Demonstrate a business-rule failure

Try to add another item after approval:

```bash
curl -i -X POST "http://localhost:8000/orders/$ORDER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id":"P002",
    "quantity":1,
    "unit_price":10
  }'
```

Expected:

```text
409 Conflict
```

### What to highlight

Architecture separates responsibilities, but business rules still belong to the domain.

---

# 2. Hexagonal Architecture

Stop the previous server with:

```text
Ctrl+C
```

Then:

```bash
cd ../02-hexagonal
```

## Teaching objective

Show that functionality is nearly identical, while **dependency direction changes**.

Key question:

> Does the application core depend on infrastructure, or does infrastructure depend on the application contracts?

## 2.1 Run all tests

```bash
pytest -q
```

Then run the architectural test alone:

```bash
pytest -q tests/test_port_substitution.py
```

### What to highlight

The application core can be instantiated with fake adapters.

Open:

```text
app/application/ports/outbound.py
tests/test_port_substitution.py
```

Point out:

```text
OrderRepository
NotificationPort
AnalyticsPort
```

These are contracts.

Then show:

```text
app/adapters/outbound/
```

These are implementations.

Ask:

> "If tomorrow PostgreSQL replaces the in-memory repository, should OrderService change?"

Expected answer:

```text
No. A new adapter can implement the same port.
```

## 2.2 Start the application

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Repeat quickly:

- Create Order
- Add Item
- Approve Order

### What to highlight

The HTTP behavior looks essentially the same as Layered.

Say:

> "From the user's perspective, almost nothing changed. The architectural difference is inside the dependency structure."

## 2.3 Compare OrderService side by side

From the repository root, an optional terminal comparison is:

```bash
cd ../../

grep -n -A25 "def approve_order" \
  01-architecture-styles/01-layered/app/services/order_service.py

grep -n -A25 "def approve_order" \
  01-architecture-styles/02-hexagonal/app/application/services/order_service.py
```

### What to highlight

Layered knows concrete collaborators.

Hexagonal knows ports.

Draw:

```text
Layered:
Core ---> concrete dependency

Hexagonal:
Core ---> port <--- adapter
```

Name the principle:

> Dependency Inversion.

---

# 3. Event-Driven Architecture

Stop the previous server:

```text
Ctrl+C
```

Then:

```bash
cd 01-architecture-styles/03-event-driven
```

## Teaching objective

Show that the producer no longer knows **who reacts** to an approved order.

## 3.1 Run tests

```bash
pytest -q
```

Then run:

```bash
pytest -q tests/test_event_decoupling.py
```

### What to highlight

Open:

```text
tests/test_event_decoupling.py
```

Show that a new Loyalty consumer is subscribed without changing `OrderService`.

Ask:

> "What class did we have to modify to add another reaction?"

Expected answer:

```text
None in the producer.
```

## 3.2 Start the server

```bash
uvicorn app.main:app --reload
```

Create an order:

```bash
ORDER_ID=$(curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C001"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
```

Add an item:

```bash
curl -s -X POST "http://localhost:8000/orders/$ORDER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id":"P001",
    "quantity":2,
    "unit_price":25.5
  }'
```

Approve:

```bash
curl -s -X POST "http://localhost:8000/orders/$ORDER_ID/approve"
```

Look at the application terminal.

You should see Notification and Analytics reactions.

## 3.3 Show the producer

Open:

```text
app/services/order_service.py
```

Find:

```python
self.event_bus.publish(
    OrderApproved.create(...)
)
```

Ask students:

> "Where are NotificationService and AnalyticsService?"

They are not in `OrderService`.

Then open:

```text
app/main.py
```

Show:

```python
event_bus.subscribe(OrderApproved, NotificationConsumer())
event_bus.subscribe(OrderApproved, AnalyticsConsumer())
```

### What to highlight

Before:

```text
OrderService
  +--> Notification
  +--> Analytics
```

Now:

```text
OrderService
     |
     v
OrderApproved
     |
     v
Event Bus
  /      \
Notification Analytics
```

Key sentence:

> "Hexagonal decoupled the core from technologies. Event-Driven decouples the producer from knowing all the reactions."

Also clarify:

> "This lab uses a synchronous in-memory event bus. Event-driven does not automatically mean Kafka or asynchronous processing."

---

# 4. Microservices

Stop the previous server:

```text
Ctrl+C
```

Return to:

```bash
cd ../04-microservices
```

## Teaching objective

Make the **network boundary and partial failure** visible.

This is the first example where architecture changes the deployment topology.

## 4.1 Start the complete topology

```bash
docker compose up --build
```

Use a second terminal for the next commands.

Check the services:

```bash
docker compose ps
```

Expected services:

```text
order-service
inventory-service
notification-service
```

### What to highlight

These are now three separate processes.

Open:

```text
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
```

Ask:

> "What changed compared with Hexagonal? We had boundaries before too."

Important answer:

> The boundaries are now process/network/deployment boundaries.

## 4.2 Create an order

```bash
ORDER_ID=$(curl -s -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C001"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')

echo $ORDER_ID
```

## 4.3 Add an item

```bash
curl -s -X POST "http://localhost:8001/orders/$ORDER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id":"P001",
    "quantity":2,
    "unit_price":25.5
  }'
```

In another terminal:

```bash
docker compose logs inventory-service --tail=20
```

### What to highlight

The Order service had to cross the network to ask Inventory.

Open:

```text
services/order-service/app/clients.py
```

Show the HTTP call.

Ask:

> "What new things can fail here that could not fail with a normal method call?"

Expected examples:

- timeout;
- DNS/service discovery;
- service unavailable;
- network latency;
- remote 5xx.

## 4.4 Approve the order

```bash
curl -s -X POST "http://localhost:8001/orders/$ORDER_ID/approve"
```

Then:

```bash
docker compose logs notification-service --tail=20
```

### What to highlight

Notification is no longer an in-process collaborator.

It is another independently running service.

## 4.5 Demonstrate partial failure

This is the most important Microservices demo.

Stop Notification:

```bash
docker compose stop notification-service
```

Create another order:

```bash
FAILED_ORDER_ID=$(curl -s -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"C002"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
```

Add an item:

```bash
curl -s -X POST "http://localhost:8001/orders/$FAILED_ORDER_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id":"P001",
    "quantity":1,
    "unit_price":25.5
  }'
```

Try approval:

```bash
curl -i -X POST "http://localhost:8001/orders/$FAILED_ORDER_ID/approve"
```

Expected:

```text
503 Service Unavailable
```

Now retrieve the order:

```bash
curl -s "http://localhost:8001/orders/$FAILED_ORDER_ID"
```

Observe:

```json
{
  "status": "APPROVED"
}
```

### Stop here and ask

> "The API said the operation failed. Why is the order APPROVED?"

This is the gateway to:

- partial failure;
- lack of distributed atomicity;
- retries;
- idempotency;
- Saga;
- compensating actions;
- outbox pattern;
- eventual consistency.

Then ask:

> "If we restart Notification Service, will the missing notification magically happen?"

Answer in this implementation:

```text
No.
```

There is no durable event, retry queue or outbox.

Restart:

```bash
docker compose start notification-service
```

## 4.6 Clean up

```bash
docker compose down
```

---

# 5. Pipes & Filters

From:

```bash
cd ../05-pipes-and-filters
```

## Teaching objective

Show that this style solves a **different shape of architectural problem**: sequential transformation.

Key question:

> Can the work be decomposed into independent processing stages?

## 5.1 Run tests

```bash
pytest -q
```

Run the extension tests:

```bash
pytest -q tests/test_pipeline_extension.py
```

### What to highlight

A Fraud Detection filter can be inserted without changing the other filters.

Open:

```text
app/pipeline.py
app/filters/
tests/test_pipeline_extension.py
```

## 5.2 Start the application

```bash
uvicorn app.main:app --reload
```

## 5.3 Inspect the current pipeline

```bash
curl -s http://localhost:8000/pipeline
```

Expected:

```json
{
  "filters": [
    "validate",
    "normalize",
    "calculate_total",
    "persist"
  ]
}
```

### What to highlight

The pipeline itself defines composition and order.

Each filter focuses on one transformation.

## 5.4 Process an order draft

```bash
curl -s -X POST http://localhost:8000/orders/process \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id":" c001 ",
    "items":[
      {
        "product_id":" p001 ",
        "quantity":2,
        "unit_price":25.5
      }
    ]
  }'
```

Observe:

```text
customer_id: C001
product_id: P001
total: 51.0
```

And especially:

```json
"trace": [
  "validate",
  "normalize",
  "calculate_total",
  "persist"
]
```

### What to highlight

The trace makes the architectural style visible at runtime.

Ask:

> "Which component knows the complete sequence?"

Answer:

```text
The pipeline/composition code.
```

Individual filters should not need to know the full chain.

## 5.5 Demonstrate the Fraud filter

The default API does not enable Fraud Detection because the objective is to show how a filter can be inserted.

Run:

```bash
pytest -q tests/test_pipeline_extension.py
```

Open:

```text
app/filters/fraud.py
tests/test_pipeline_extension.py
```

Show:

```text
Validate
   |
Normalize
   |
Calculate Total
   |
Fraud Detection
   |
Persist
```

Ask:

> "Did ValidationFilter, NormalizationFilter or CalculateTotalFilter have to change?"

Expected:

```text
No.
```

Then ask an even more important question:

> "Would Loyalty processing naturally belong in this pipeline?"

Likely answer:

> Not necessarily. Loyalty is a reaction to approval, not naturally a sequential transformation of the draft.

This is the lesson about **architectural fit**.

---

# 6. Closing comparison

Return to the repository root:

```bash
cd ../..
```

Open:

```text
docs/architecture-comparison.md
```

Use the same requirement:

> Every approved order must trigger Loyalty processing.

Ask students to describe what changes in each style.

## Layered

```text
OrderService
  +--> LoyaltyService
```

Highlight:

- direct coupling;
- service orchestration grows.

## Hexagonal

```text
OrderService --> LoyaltyPort <-- LoyaltyAdapter
```

Highlight:

- dependency inversion;
- technology replaceability.

## Event-Driven

```text
OrderApproved --> LoyaltyConsumer
```

Highlight:

- producer does not change;
- control flow becomes less explicit.

## Microservices

Possible design:

```text
order-service --> loyalty-service
```

Then ask:

> "Should that interaction really be synchronous HTTP?"

This connects Microservices back to Event-Driven.

## Pipes & Filters

Ask:

> "Is Loyalty actually a filter in an order-processing pipeline?"

The important lesson is that architecture is not selecting a fashionable style. It is matching **forces, constraints and quality attributes**.

---

# 7. Recommended live-class narrative

Use this storyline instead of presenting five disconnected definitions.

```text
1. Layered
   "Let's separate responsibilities."

2. Hexagonal
   "But our core still depends on things outside it.
    Can we invert those dependencies?"

3. Event-Driven
   "But the producer still needs to know every reaction.
    Can we decouple reactions?"

4. Microservices
   "What happens if some boundaries become independently
    deployable processes?"

5. Pipes & Filters
   "What if our problem is not service orchestration at all,
    but sequential data transformation?"
```

The recurring evaluation question is:

> "What did this architectural decision make easier, and what new problem did it create?"

That question is more important than memorizing the diagram of each style.
