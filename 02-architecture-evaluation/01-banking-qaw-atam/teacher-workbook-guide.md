# Guía docente del workbook — Banco Horizonte QAW + ATAM-lite

> **DOCENTE — NO DISTRIBUIR AL ALUMNO**

Esta guía acompaña el workbook de 26 páginas del caso Banco Horizonte. Su objetivo es ayudar al docente a facilitar la actividad, intervenir sin revelar demasiado pronto las respuestas y disponer de un answer key para QAW y ATAM-lite.

## Timing de la sesión

| Tiempo | Workbook | Actividad |
|---|---|---|
| 0:00–0:15 | Págs. 1–3 | Apertura, contexto y stakeholders |
| 0:15–0:35 | Págs. 4–7 | Lectura arquitectónica y objetivos cuantitativos |
| 0:35–1:00 | Págs. 8–14 | QAW: drivers + escenarios |
| 1:00–1:15 | — | Receso 1 |
| 1:15–1:45 | Págs. 14–15 | QAW: priorización y refinamiento |
| 1:45–2:15 | Págs. 16–23 | ATAM-lite: Utility Tree, S1–S4 y findings |
| 2:15–2:30 | — | Receso 2 |
| 2:30–2:50 | Pág. 24 | Presentaciones |
| 2:50–3:00 | Págs. 25–26 | Debrief y cierre |

## Answer key ejecutivo

Los siguientes findings deberían emerger de la evaluación:

1. **Performance gap:** 1.200 TPS requeridos vs 700 TPS sostenibles del core.
2. **RTO gap:** RTO ≤5 min vs failover probado 8–12 min.
3. **RPO gap:** RPO=0 vs réplica DR async con 15–60 s de lag.
4. **Event publication gap:** DB commit y publish de PaymentCompleted no son atómicos.
5. **Fraud coupling:** fraude está en critical path, timeout 400 ms y fail-closed.
6. **Idempotency ambiguity:** Redis + unique constraint ayudan localmente, pero la semántica frente al side effect remoto del core permanece abierta.
7. **Modifiability strength:** Fraud Adapter + contrato ALLOW/REVIEW/BLOCK es un non-risk razonable para cambio de proveedor.

### Risk themes esperables

- Critical synchronous dependencies.
- DR objectives not matched by data architecture.
- Cross-boundary consistency gaps.

### Trade-offs fuertes

- Security vs Availability en la política fail-closed.
- RPO vs Latency/Availability en replicación cross-region.
- Throughput vs Core stability en concurrencia hacia el core.

---

## Págs. 1–3 — Propósito, contexto y stakeholders

### Qué debe lograr

Alinear expectativas: no se busca “aprobar” o “rechazar” la arquitectura, sino explicar consecuencias a partir de business drivers, quality attributes y evidencia.

### Qué debería detectar el grupo

- core legado como restricción fija;
- presión de time-to-market por lanzamiento en 6 meses;
- picos de nómina como ambiente operativo concreto;
- idempotencia, experiencia, fallas de terceros y continuidad como drivers arquitectónicos.

### Preguntas de presión

- ¿Qué significa “instantánea” de forma medible?
- ¿Qué objetivo sería costoso violar aunque ocurra rara vez?
- ¿Qué stakeholders podrían tener objetivos en tensión?

---

## Pág. 4 — Arquitectura propuesta

Pida seguir el camino de una transferencia y marcar fronteras:

1. canal → API Gateway → Payment Orchestrator;
2. Fraud Adapter y Core Adapter en critical path síncrono;
3. persistencia en PostgreSQL;
4. publicación de PaymentCompleted posterior al commit;
5. replicación DR asíncrona.

**Pregunta:** ¿Qué flecha puede convertirse en un riesgo aunque cada componente individual funcione?

---

## Págs. 5–7 — Decisiones A1–A8 y objetivos

### Lecturas clave

- A1 stateless favorece escalabilidad del Orchestrator, pero no elimina límites downstream.
- A2 Fraud Adapter favorece modificabilidad; fail-closed amenaza availability.
- A3 Redis + unique DB fortalece deduplicación local, pero no cierra por sí sola idempotencia frente al core.
- A4 core de 700 TPS amenaza el objetivo de 1.200 TPS.
- A5 DR async/warm standby no demuestra RPO=0 ni RTO≤5.
- A6 sin transactional outbox existe ventana DB commit → publish.
- A7 mTLS/OIDC son controles positivos; seguridad y availability pueden entrar en trade-off.
- A8 el core es un punto ciego parcial de observabilidad.

### Tres tensiones mínimas de pág. 7

1. 1.200 TPS vs 700 TPS.
2. RTO≤5 vs 8–12 min.
3. RPO=0 vs 15–60 s de lag.

---

## Pág. 8 — QAW

Drivers razonables:

- Availability / recoverability
- Performance / scalability
- Reliability / consistency / idempotency
- Security / fraud
- Modifiability
- Auditability / observability

Intervenciones:

- “alta disponibilidad” → ¿qué falla, cuándo, qué respuesta y qué medida?
- “usar active-active” → eso es solución; ¿cuál es el escenario?
- “rápido” → ¿qué percentil y umbral?
- “seguro” → ¿frente a qué estímulo y qué resultado verificable?

---

## Págs. 9–14 — Escenarios QAW de referencia

### Q1 Performance
1.200 TPS por 15 min en nómina; p95≤1,5 s, p99≤3 s, error<0,5%.

### Q2 Region recovery
Pérdida de región a 900 TPS; RTO≤5, RPO=0, sin doble débito.

### Q3 Idempotencia
Cinco retries con misma key; 1 débito, 1 transaction_id, resolución≤2 s.

### Q4 Cambio de fraude
Nuevo proveedor en ≤6 semanas; sin cambios en mobile/web/core.

### Q5 Fraud outage
Proveedor no responde; política de degradación sin bypass high-risk.

### Q6 Auditoría
Reconstrucción de una transferencia en ≤10 min con correlación inequívoca.

### Q7 Event publication gap
Crash después del commit y antes del publish; ningún pago confirmado debe quedar permanentemente sin evento downstream.

---

## Págs. 14–15 — Priorización y refinamiento

No existe un ranking único. Evalúe la justificación.

Top 4 probable:

- Peak performance
- Region failure
- Duplicate request
- Fraud outage o provider replacement

En el refinamiento exija:

1. medida observable;
2. decisión arquitectónica relacionada;
3. pregunta concreta al arquitecto.

---

## Págs. 16–17 — Utility Tree

Ejemplo:

```text
Utility
├── Availability
│   ├── Region failure            H/H
│   └── Fraud provider outage     H/H
├── Performance
│   └── 1.200 TPS peak            H/H
├── Reliability
│   └── Duplicate request         H/M
├── Modifiability
│   └── Replace fraud provider    M/M
└── Auditability
    └── Reconstruct transaction   M/M
```

Aclare que **Importancia** y **Dificultad** son dimensiones diferentes.

---

## Pág. 18 — S1 Peak performance

**Riesgo alto.**

Evidencia:

- target 1.200 TPS;
- core sostenible 700 TPS;
- fraude y core síncronos.

Sensitivity points:

- capacidad del core;
- concurrencia/pool del Core Adapter;
- latencia/timeout de fraude.

Trade-off: más concurrencia puede elevar throughput inicialmente y luego saturar el core.

Pregunta de presión: **¿20 instancias de Orchestrator resuelven el problema?** No necesariamente.

---

## Pág. 19 — S2 Region failure

Dos riesgos:

- **RTO mismatch:** 8–12 min no cumple ≤5.
- **RPO mismatch:** async replication no garantiza RPO=0.

Sensitivity points:

- replication mode;
- failover automation;
- routing TTL;
- commit semantics.

Trade-off: más sincronía cross-region mejora RPO, pero puede aumentar latencia y reducir availability ante particiones.

---

## Pág. 20 — S3 Fraud provider replacement

**Non-risk razonable**, con evidencia limitada.

Fortalezas:

- adapter dedicado;
- contrato canónico ALLOW/REVIEW/BLOCK;
- canales y core no dependen del proveedor.

Sensitivity: estabilidad del contrato canónico.

Preguntas abiertas:

- contract tests;
- leakage de reglas del proveedor;
- mapping semántico entre scores;
- cutover/dual operation.

---

## Pág. 21 — S4 Duplicate request

**Non-risk parcial + riesgo abierto.**

Fortalezas:

- Idempotency-Key;
- Redis 24 h;
- unique constraint en PostgreSQL.

Riesgo:

Si el core debita y el sistema cae antes de persistir localmente, la deduplicación local puede ser insuficiente si el core remoto no participa de la semántica idempotente.

Sensitivity: orden de operaciones.

---

## Págs. 22–23 — Findings

### Riesgos aceptables

- R1 core capacity.
- R2 RTO mismatch.
- R3 RPO mismatch.
- R4 DB/event publish gap.
- R5 fraude síncrono propaga fallo de tercero.
- R6 idempotencia local insuficiente frente a side effect remoto.
- R7 core limita trazabilidad end-to-end.

### Non-risks

- Fraud Adapter/canonical contract.
- Unique DB constraint complementando Redis.
- Notification/Analytics fuera del critical path, aunque el publish gap sigue siendo riesgo.

### Sensitivity points

- 400 ms fraud timeout.
- Core Adapter concurrency.
- Replication mode.
- Idempotency retention.
- Ordering del side effect remoto.
- Failover/routing TTL.
- Canonical fraud contract.

### Trade-offs

- fail-closed: security↑ / availability↓;
- cross-region sync: RPO↑ / latency-partition sensitivity↑;
- core concurrency: throughput↑ / core stability↓.

---

## Pág. 24 — Presentación y recomendación

La recomendación debe tener:

**mecanismo + escenario + response measure + business driver + costo/trade-off.**

Respuestas de presión:

- “Kafka” → ¿qué escenario resuelve?
- “microservicios” → ¿qué riesgo desaparece por cambiar deployment boundary?
- “active-active” → ¿qué consistencia requiere el ledger?
- “autoscaling” → ¿dónde está el bottleneck?
- “Redis resuelve idempotencia” → ¿qué pasa si el side effect remoto ya ocurrió?

---

## Pág. 25 — Reflexión individual

Respuesta esperada:

> “Alta disponibilidad” es una aspiración vaga. Demostrarla requiere un escenario con estímulo, ambiente, respuesta, medida y evidencia de que los mecanismos arquitectónicos pueden cumplirla.

---

## Pág. 26 — Debrief

Diferencias:

- **Risk:** puede impedir cumplir un quality goal.
- **Non-risk:** la evidencia actual soporta el goal; no significa garantía absoluta.
- **Sensitivity point:** parámetro/decisión al que el resultado es muy sensible.
- **Trade-off point:** afecta materialmente múltiples atributos.
- **Risk theme:** causa común que agrupa varios riesgos.

---

## Rúbrica — 20 puntos

| Criterio | Puntos |
|---|---:|
| Escenarios QAW completos y medibles | 5 |
| Priorización por business drivers | 3 |
| Análisis arquitectura ↔ escenarios | 4 |
| Risks / non-risks | 3 |
| Sensitivity + trade-off | 2 |
| Risk theme | 1 |
| Recomendación | 2 |

## Extensión opcional

Pedir un ADR para:

- transactional outbox;
- DR replication strategy;
- fraud degradation policy;
- idempotency across core boundary.

Re-evaluar después: **¿qué riesgos se mitigaron, cuáles permanecen y cuáles nuevos aparecieron?**
