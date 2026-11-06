# Clase 11 - Banco Horizonte Architecture Validation Sprint

## Objetivo

En la clase anterior el equipo evaluó la arquitectura con QAW + ATAM-lite. En esta sesión no repetiremos esa evaluación. Partiremos de los findings y los convertiremos en hipótesis verificables mediante experimentos.

## La idea central

```text
Evaluation -> What might be risky?
Validation -> What evidence supports or rejects that concern?
```

## Prototype, Spike y Walking Skeleton

- **Prototype:** artefacto para explorar experiencia, forma o comportamiento; puede no ser productivo.
- **Spike:** experimento técnico acotado para reducir incertidumbre; su producto principal es conocimiento.
- **Walking skeleton:** implementación mínima end-to-end, desplegable y observable, que atraviesa las piezas esenciales del sistema.

En este caso usaremos un walking skeleton de Payment -> Fraud -> Core.

## Antes de ejecutar

1. Lea `validation-plan.md`.
2. Identifique finding, hypothesis, variable independiente, variables dependientes y acceptance criteria.
3. Prediga el resultado antes de ejecutar.
4. Ejecute.
5. Registre evidencia.
6. Clasifique el resultado como PASS / FAIL / INCONCLUSIVE.

## Experimento 1 - Load test

**Finding:** 1.200 TPS esperados vs core sostenible de 700 TPS.

**Comando:** `make load-test`

Registre:

| Métrica | Resultado |
|---|---|
| Offered RPS | |
| Achieved RPS | |
| p50 | |
| p95 | |
| p99 | |
| Error rate | |
| PASS/FAIL | |

Pregunta: ¿qué componente parece limitar la capacidad end-to-end?

## Experimento 2 - Stress test

**Comando:** `make stress-test`

Identifique el knee point y describa cómo falla el sistema: errores, latencia, throughput o combinación.

## Experimento 3 - Latency injection

**Comando:** `make latency-test`

Compare 20, 200, 500 y 900 ms de latencia del Fraud Provider. Explique qué ocurre alrededor del timeout de 400 ms.

## Experimento 4 - Fraud unavailable

**Comando:** `make fraud-down`

Verifique que high-risk no bypassa Fraud y que el Core no recibe débito.

## Experimento 5 - Idempotency normal path

**Comando:** `make duplicate-payment-test`

Cinco requests concurrentes, misma Idempotency-Key. Acceptance criteria: 1 transaction_id y 1 core debit.

## Experimento 6 - Crash window

**Comando:** `make crash-after-core-debit`

Observe la ventana: core debit -> crash -> no local commit -> retry. Explique por qué la idempotencia local puede ser insuficiente.

## Experimento 7 - Observability

**Comando:** `make trace-payment`

Reconstruya la secuencia del pago usando correlation ID.

## Experimento 8 - Security

**Comando:** `make security-test`

Valide missing token, invalid token, fraud bypass y fraud unavailable.

## Experimento 9 - Static analysis / modularity

**Comandos:**

```bash
make architecture-test
make modularity-metrics
```

Explique qué prueban y qué NO prueban estas métricas.

## De experimento a fitness function

Seleccione dos validaciones y responda:

1. ¿Es objetiva?
2. ¿Es repetible?
3. ¿Puede automatizarse?
4. ¿Debe ejecutarse en cada commit, cada build, cada release o periódicamente?
5. ¿Qué threshold usaría como gate?

## Entregable del grupo

Prepare una síntesis de 5 minutos:

- finding más importante;
- hipótesis;
- evidencia;
- PASS/FAIL/INCONCLUSIVE;
- decisión arquitectónica;
- una validación que convertiría en fitness function.
