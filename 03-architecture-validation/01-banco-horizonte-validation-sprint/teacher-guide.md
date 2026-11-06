# Guía docente - Clase 11 Banco Horizonte Architecture Validation Sprint

> DOCENTE - NO DISTRIBUIR AL ALUMNO

## Propósito

Dar continuidad directa a Clase 10: ATAM-lite produjo findings; Clase 11 convierte esos findings en hipótesis, experimentos y evidencia.

## Timing - 3 horas

| Tiempo | Bloque |
|---|---|
| 0:00-0:15 | Evaluación vs validación; prototype/spike/walking skeleton |
| 0:15-0:30 | Anatomy of an experiment: hypothesis, variables, acceptance criteria |
| 0:30-0:55 | Load + stress + p95/p99 |
| 0:55-1:00 | Síntesis rápida |
| 1:00-1:15 | Receso 1 |
| 1:15-1:40 | Resilience + latency injection + fraud-down |
| 1:40-2:05 | Idempotency + crash window |
| 2:05-2:15 | Observability |
| 2:15-2:30 | Receso 2 |
| 2:30-2:45 | Security + static analysis + modularity metrics |
| 2:45-2:55 | Fitness functions + pipeline |
| 2:55-3:00 | Cierre |

## Apertura

Frase guía: **ATAM nos dijo qué nos preocupa; hoy ingeniería debe probarlo.**

Diferencie:

- Evaluation: judgment based on scenarios, decisions and evidence available.
- Validation: targeted experiment against a hypothesis and explicit acceptance criteria.

## Prototype / Spike / Walking Skeleton

Aclare que estos conceptos se usan aquí como framing de ingeniería complementario a las lecturas.

- prototype: explora forma/experiencia;
- spike: reduce incertidumbre técnica;
- walking skeleton: mínimo end-to-end desplegable/observable.

Pregunta: ¿por qué un walking skeleton es mejor base para validación arquitectónica que un mock aislado? Respuesta: porque atraviesa boundaries y permite observar interacciones reales entre piezas.

## Load test

`make load-test`

Resultado esperado con configuración base: **FAIL** o degradación significativa, porque el core lab está limitado a 35 RPS (equivalente a 700 TPS) y ofrecemos 60 RPS (equivalente a 1.200 TPS).

Resalte que escalar Payment no elimina un bottleneck downstream.

## Stress test

`make stress-test`

Resultado esperado: degradación alrededor o por encima de 35 RPS. Pida identificar knee point, no solo máximo throughput.

## p50 / p95 / p99

Mensaje clave: el promedio puede ocultar tail latency. p95 significa que 95% de observaciones están en o debajo de ese valor; p99 enfoca el 1% más lento.

## Latency injection

`make latency-test`

Fraud timeout = 400 ms. A 500/900 ms deberían aparecer 503/timeouts. Pregunte: ¿qué atributo mejora fail-closed? Seguridad. ¿Cuál perjudica? Availability.

## Fraud down

`make fraud-down`

Esperado: 503 y core_debits=0. Clasificación: security property validada para este escenario; availability degradada deliberadamente.

## Idempotency

`make duplicate-payment-test`

Esperado: cinco requests concurrentes, un transaction_id lógico y un core debit.

Luego `make crash-after-core-debit`.

Esperado: primer request 500, retry 200, core debit count = 2. Esto reproduce el riesgo cross-boundary: el side effect remoto ya ocurrió antes del commit local.

Pregunta de presión: ¿Redis arregla esto por sí solo? No.

## Observability

`make trace-payment`

Esperado: stages payment_received, fraud_decision, core_debit, local_commit bajo el mismo correlation ID.

Diferencie logs sueltos de reconstrucción causal de una operación.

## Security

`make security-test`

Esperado: 401, 401, 403, 503 y core_debits=0.

Aclare que esto no demuestra que el sistema sea 'seguro'; valida propiedades concretas bajo estímulos concretos.

## Static analysis y modularidad

`make architecture-test` debe pasar.

`make modularity-metrics` reporta Ca, Ce e Instability por módulo.

Mensaje clave: métricas estructurales son evidencia parcial. No existe un único número que certifique una buena arquitectura.

## Fitness functions

Cierre con la transformación:

```text
one-off experiment
      -> repeatable check
      -> automated threshold
      -> fitness function / governance gate
```

Candidatos fuertes del lab:

- architecture dependency check;
- security regression gate;
- idempotency regression test;
- smoke test;
- performance budget seleccionado.

## Preguntas de presión

- 'Pongamos autoscaling' -> ¿dónde está el bottleneck end-to-end?
- 'Kafka arregla reliability' -> ¿qué failure window elimina exactamente?
- 'Redis da idempotencia' -> ¿qué pasa si el side effect remoto ya ocurrió?
- 'Tenemos 100% coverage' -> ¿qué propiedad arquitectónica quedó demostrada?
- 'p95 está bien' -> ¿qué ocurre con p99 y con el error rate?

## Respuesta de cierre esperada

La arquitectura no se valida por una demo exitosa ni por una herramienta. Se valida una hipótesis concreta mediante evidencia y criterios de aceptación. Las validaciones repetibles pueden convertirse en mecanismos de gobernanza automatizada.
