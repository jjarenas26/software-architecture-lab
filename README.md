# Software Architecture Lab

A hands-on laboratory for the **Software Design and Evaluation** course.

The purpose of this repository is to make software architecture visible in code. Instead of studying architectural styles only through diagrams, we implement the **same business problem and functional behavior** using different architectural styles and compare the consequences of each design.

## Core learning idea

> Same requirements. Same business rules. Different architecture.

Students can therefore focus on architectural decisions rather than on differences in functionality.

## Common domain

All implementations use a small **Order Management** domain with the same core use cases:

1. Create an order
2. Add an item
3. Get an order
4. Approve an order
5. Cancel an order

When an order is approved, the system must also support secondary reactions such as customer notification and analytics. This gives us a useful scenario for comparing synchronous coupling with event-driven designs.

See:

- [Domain model](docs/domain.md)
- [Common API contract](docs/api-contract.md)

## Architectural styles roadmap

The first module of the lab will compare:

- Layered Architecture
- Hexagonal Architecture (Ports & Adapters)
- Event-Driven Architecture
- Microservices
- Pipes and Filters

The repository can later grow into a broader architecture laboratory covering:

- Quality attributes
- Architecture tactics
- ATAM-style evaluation
- Technical debt
- Architecture evolution

## Pedagogical rule

Every architecture should preserve the same externally visible behavior whenever possible.

That lets us ask the important question:

> If the systems do the same thing, why would we choose one architecture over another?

The answer should be discussed in terms of quality attributes and trade-offs such as:

- Modifiability
- Testability
- Deployability
- Scalability
- Availability
- Performance
- Maintainability
- Operational complexity

## Repository structure

```text
software-architecture-lab/
├── README.md
├── docs/
│   ├── domain.md
│   └── api-contract.md
├── 01-architecture-styles/
│   ├── 01-layered/
│   ├── 02-hexagonal/
│   ├── 03-event-driven/
│   ├── 04-microservices/
│   └── 05-pipes-and-filters/
└── exercises/
```

Directories are added progressively as each implementation is built.

## Technology principles

Examples should optimize for **architectural clarity**, not production infrastructure complexity.

Default stack:

- Python
- FastAPI
- pytest
- In-memory persistence first
- SQLite only when persistence adds pedagogical value
- Docker Compose when multiple processes are genuinely useful
- Mermaid for architecture diagrams

Infrastructure such as Kafka, Kubernetes, or external databases should only be introduced when the architectural concept requires it.

## How to use this repository in class

A typical learning sequence is:

```text
Business problem
      ↓
Baseline implementation
      ↓
Architectural style
      ↓
Change scenario
      ↓
Observe impact
      ↓
Discuss quality attributes and trade-offs
```

The lab is intentionally evolutionary: architectural styles are not presented as rankings. Each style is a response to a different set of forces, constraints, and quality-attribute priorities.
