# Banco Horizonte - Architecture Validation Sprint

This module continues the Banco Horizonte architecture-evaluation case without modifying the previous QAW + ATAM-lite material.

## Continuity

```text
Class 10
QAW + ATAM-lite
      |
      v
Architecture findings
      |
      v
Class 11
Hypotheses + experiments + evidence
      |
      v
Validated / Rejected / Inconclusive
      |
      v
Fitness functions / automated governance
```

## Learning objectives

Students should be able to:

- distinguish architecture evaluation from architecture validation;
- choose between prototype, spike and walking skeleton;
- formulate hypotheses, variables and acceptance criteria;
- execute load and stress tests;
- interpret p50, p95 and p99 latency;
- validate resilience using fault injection;
- reason about idempotency under failure;
- validate security and observability properties;
- use static analysis and structural metrics as architecture evidence;
- recognize when a repeatable validation can become a fitness function.

## Lab topology

```text
Experiment runner
      |
      v
Payment Service :8101
   |            |
   v            v
Fraud :8102   Core :8103
```

The services are intentionally small and deterministic. Faults are injected through explicit admin endpoints so classroom results are repeatable.

## Scenario scaling

The business case uses 1,200 TPS peak and a legacy-core sustainable capacity of 700 TPS. A laptop should not need to generate real bank-scale traffic, so this lab uses a default scale factor of 20:1:

- 60 lab requests/sec represents 1,200 TPS.
- 35 lab requests/sec represents 700 TPS.

Latency targets remain unscaled:

- p95 <= 1.5 s
- p99 <= 3 s

## Quick start

```bash
cd 03-architecture-validation/01-banco-horizonte-validation-sprint
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
make up
make smoke
```

Run experiments:

```bash
make load-test
make stress-test
make latency-test
make fraud-down
make duplicate-payment-test
make crash-after-core-debit
make trace-payment
make security-test
make architecture-test
make modularity-metrics
```

Stop:

```bash
make down
```

## Materials

- `validation-plan.md`
- `student-guide.md`
- `teacher-guide.md`
- `results/README.md`
