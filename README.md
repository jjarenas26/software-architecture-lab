# Software Architecture Lab

A hands-on laboratory for the **Software Design and Evaluation** course.

The purpose of this repository is to make software architecture visible in code. Instead of studying architectural styles only through diagrams, we implement a common business domain using different architectural styles and compare the consequences of each design.

## Core learning idea

> Same domain and business forces. Different architecture. Observable trade-offs.

The first four implementations preserve the same Order Management workflow as closely as possible. Pipes & Filters intentionally focuses on a sequential order-processing scenario because part of architectural evaluation is recognizing when a style naturally fits a problem — and when it does not.

## Common domain

All implementations use the **Order Management** domain.

Core use cases include:

1. Create an order
2. Add an item
3. Get an order
4. Approve an order
5. Cancel an order

When an order is approved, the system can also trigger secondary reactions such as notification, analytics and loyalty processing.

See:

- [Domain model](docs/domain.md)
- [Common API contract](docs/api-contract.md)
- [Architectural styles comparison](docs/architecture-comparison.md)

## Implemented architectural styles

| # | Style | Lab |
|---|---|---|
| 01 | Layered Architecture | [Open](01-architecture-styles/01-layered/) |
| 02 | Hexagonal Architecture / Ports & Adapters | [Open](01-architecture-styles/02-hexagonal/) |
| 03 | Event-Driven Architecture | [Open](01-architecture-styles/03-event-driven/) |
| 04 | Microservices Architecture | [Open](01-architecture-styles/04-microservices/) |
| 05 | Pipes & Filters | [Open](01-architecture-styles/05-pipes-and-filters/) |

Each implementation includes:

- runnable code;
- architecture diagrams;
- tests;
- a suggested classroom demo;
- trade-offs and discussion questions;
- GitHub Actions validation.

## Repository structure

```text
software-architecture-lab/
├── README.md
├── docs/
│   ├── domain.md
│   ├── api-contract.md
│   └── architecture-comparison.md
├── 01-architecture-styles/
│   ├── 01-layered/
│   ├── 02-hexagonal/
│   ├── 03-event-driven/
│   ├── 04-microservices/
│   └── 05-pipes-and-filters/
└── exercises/
```

## Technology principles

Examples optimize for **architectural clarity**, not production infrastructure complexity.

Default stack:

- Python
- FastAPI
- pytest
- in-memory persistence where appropriate
- Docker Compose when multiple processes are architecturally meaningful
- Mermaid for architecture diagrams

Infrastructure such as Kafka, Kubernetes or external databases should only be introduced when the architectural concept requires it.

## How to use this repository in class

A typical learning sequence is:

```text
Business problem
      |
      v
Architectural style
      |
      v
Run the code
      |
      v
Introduce a change or failure
      |
      v
Observe what must change
      |
      v
Discuss quality attributes and trade-offs
```

Useful recurring change scenario:

> Every approved order must also trigger loyalty processing.

Useful recurring evaluation question:

> If the business requirement is similar, why does this architecture make some changes or failures easier and others harder?

The lab is intentionally evolutionary: architectural styles are not presented as rankings. Each style is a response to a different set of forces, constraints and quality-attribute priorities.

## Future modules

The repository can later grow into a broader architecture laboratory covering:

- Quality attributes
- Architecture tactics
- ATAM-style evaluation
- Technical debt
- Architecture evolution
