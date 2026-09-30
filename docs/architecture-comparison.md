# Architectural Styles Comparison

This document compares the five styles implemented in the lab.

It is deliberately **not a ranking**. Architectural styles respond to different forces, constraints, deployment models and quality attributes.

## At a glance

| Style | Primary organizing idea | Main boundary made visible | Collaboration model | What changes most clearly in the lab | Natural discussion topics |
|---|---|---|---|---|---|
| Layered | Separate responsibilities into layers | Controller / service / repository | Direct in-process calls | Responsibilities are grouped by technical layer | separation of concerns, coupling, maintainability |
| Hexagonal | Protect the application core behind ports | Core vs. adapters | Calls through interfaces / ports | Dependency direction points toward the core | dependency inversion, replaceability, testability |
| Event-Driven | Communicate facts through events | Producer vs. consumers | Publish / subscribe | Producer no longer knows who reacts | loose coupling, eventual consistency, idempotency |
| Microservices | Split capabilities into independently running services | Process / network / data ownership | Remote calls across service boundaries | Local calls become fallible network interactions | deployment independence, partial failure, observability |
| Pipes & Filters | Transform data through sequential stages | One processing stage vs. the next | Context flows through ordered filters | New processing stages can be inserted or reordered | composability, sequencing, stream processing |

## The same order problem through different lenses

### 1. Layered

```text
HTTP
 |
 v
Controller
 |
 v
Service
 |
 v
Repository
```

The key question:

> How are responsibilities separated?

### 2. Hexagonal

```text
             HTTP Adapter
                  |
                  v
             Inbound Port
                  |
                  v
            Application Core
             /      |      \
            v       v       v
          Port    Port     Port
            ^       ^       ^
            |       |       |
         Adapters Adapters Adapters
```

The key question:

> Which direction do dependencies point?

### 3. Event-Driven

```text
OrderService
     |
     v
OrderApproved
     |
     v
 Event Bus
  /   |   \
 v    v    v
A     B     C
```

The key question:

> Does the producer need to know who reacts?

### 4. Microservices

```text
             order-service
              /          \
             v            v
 inventory-service   notification-service
```

The key question:

> What changes when a function call becomes a network call?

### 5. Pipes & Filters

```text
Input
  |
  v
Validate
  |
  v
Normalize
  |
  v
Calculate
  |
  v
Persist
  |
  v
Output
```

The key question:

> Can processing be decomposed into independent sequential transformations?

## One requirement, different architectural impact

Use this change scenario repeatedly:

> Every approved order must also trigger loyalty processing.

### Layered

A service commonly gains another direct collaborator.

```text
OrderService
  +--> NotificationService
  +--> AnalyticsService
  +--> LoyaltyService
```

Observe how orchestration responsibilities accumulate.

### Hexagonal

Add a new outbound capability behind a port.

```text
OrderService --> LoyaltyPort <-- LoyaltyAdapter
```

Observe that the core depends on a contract rather than a concrete technology.

### Event-Driven

Add a new consumer.

```text
OrderApproved
  +--> NotificationConsumer
  +--> AnalyticsConsumer
  +--> LoyaltyConsumer
```

Observe that the producer does not change.

### Microservices

A loyalty capability could become another service boundary.

```text
order-service --> loyalty-service
```

Now ask whether synchronous HTTP is appropriate or whether an event would reduce coupling.

### Pipes & Filters

Loyalty is not naturally a sequential transformation of an order draft. That mismatch is itself important.

Ask:

> Is Pipes & Filters the right style for this requirement?

Architectural evaluation includes recognizing when a style does **not** fit the problem shape well.

## Quality-attribute discussion prompts

| Quality attribute | Questions to ask |
|---|---|
| Modifiability | How many existing components must change for a new requirement? |
| Testability | Can the core behavior be exercised without infrastructure? |
| Deployability | Can components be released independently? |
| Availability | What happens when a dependency fails? |
| Performance | How many process or network boundaries are crossed? |
| Scalability | What can be scaled independently? |
| Observability | Can we reconstruct the path of one business operation? |
| Maintainability | Is the control flow obvious to a new engineer? |

## Suggested classroom sequence

```text
Layered
   |
   | "What is coupled?"
   v
Hexagonal
   |
   | "Can we invert those dependencies?"
   v
Event-Driven
   |
   | "Does the producer need to know every reaction?"
   v
Microservices
   |
   | "What if those boundaries become separate processes?"
   v
Pipes & Filters
   |
   | "What if the problem is a transformation pipeline instead?"
   v
Architectural trade-offs
```

The objective is to move from **recognizing diagrams** to **reasoning about consequences**.
