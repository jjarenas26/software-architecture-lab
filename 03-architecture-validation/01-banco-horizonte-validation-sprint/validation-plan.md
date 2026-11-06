# Validation Plan - Banco Horizonte

This plan converts the architecture findings from the previous QAW + ATAM-lite exercise into testable hypotheses.

## Experiment template

| Field | Description |
|---|---|
| Finding | Architecture concern inherited from the evaluation |
| Hypothesis | Statement that can be supported or rejected |
| Independent variable | What the experiment deliberately changes |
| Dependent variables | What is measured |
| Controls | What must stay stable |
| Experiment | How evidence is collected |
| Acceptance criteria | Observable pass/fail thresholds |
| Result | PASS / FAIL / INCONCLUSIVE |
| Evidence | Metrics, traces, logs or structural results |
| Decision | Accept, mitigate, redesign or retest |

## V1 - Peak performance

**Finding:** expected peak is 1,200 TPS while the legacy core sustains 700 TPS.

**Hypothesis:** the end-to-end platform cannot sustain the equivalent of 1,200 TPS while meeting the agreed latency and error objectives.

**Independent variable:** offered load.

**Dependent variables:** achieved RPS, p50, p95, p99, error rate.

**Acceptance criteria:** scenario-equivalent 1,200 TPS; p95 <= 1.5 s; p99 <= 3 s; error rate < 0.5%.

**Lab mapping:** 60 RPS represents 1,200 TPS; 35 RPS represents core capacity of 700 TPS.

## V2 - Stress and breaking point

**Finding:** scaling the Payment Service may not remove downstream bottlenecks.

**Hypothesis:** the system has a visible knee point near the core capacity, after which errors and/or tail latency grow sharply.

**Independent variable:** RPS stepped from low to above capacity.

**Dependent variables:** p95, p99, error rate, achieved RPS.

**Acceptance criterion:** identify the first load level where degradation becomes material and describe the failure mode.

## V3 - Fraud latency / availability

**Finding:** Fraud is synchronous, timeout is 400 ms and policy is fail-closed.

**Hypothesis:** fraud latency above the client timeout causes payment availability to degrade while preventing fraud bypass.

**Acceptance criteria:** high-risk bypass = 0; no core debit occurs when Fraud is unavailable; behavior is explainable and observable.

## V4 - Duplicate request

**Finding:** local idempotency protects the normal retry path, but the transaction crosses a remote core boundary.

**Hypothesis:** five concurrent retries using the same Idempotency-Key produce one logical transaction and one core debit during the normal flow.

**Acceptance criteria:** one logical transaction; one transaction ID; one core debit; consistent retry results.

## V5 - Crash after remote side effect

**Finding:** local idempotency may not protect against a crash after a remote core debit and before local commit.

**Hypothesis:** if the core debit succeeds and Payment crashes before persisting the result, a retry can cause a second debit when the core is not idempotent.

**Acceptance criterion:** reproduce the failure window deterministically and make the double-debit consequence visible.

## V6 - Observability

**Hypothesis:** one payment can be reconstructed across the walking skeleton using a correlation ID and stage timestamps.

**Acceptance criteria:** correlation ID present; Fraud and Core interactions visible; final outcome visible; trace retrievable immediately in the lab.

## V7 - Security validation

**Acceptance criteria:** missing token -> 401; invalid token -> 401; bypass attempt -> 403; high-risk + Fraud unavailable -> no core debit.

## V8 - Modularity / static analysis

**Hypothesis:** domain code has no dependency on HTTP clients, adapters or the FastAPI entry point.

**Acceptance criteria:** architecture check passes; no domain -> infrastructure dependency; structural metrics interpreted as evidence, not a universal score.
