# Guía docente — Banco Horizonte: evaluación de arquitectura con QAW + ATAM-lite

> **Documento para el docente. No distribuir junto con el caso del alumno.**

## Propósito de la actividad

La meta no es que los estudiantes memoricen QAW o ATAM. La meta es que aprendan a:

1. convertir business drivers vagos en escenarios verificables;
2. conectar escenarios con decisiones arquitectónicas;
3. distinguir evidencia de opinión;
4. identificar riesgos, no-riesgos, sensitivity points y trade-offs;
5. formular recomendaciones justificadas por atributos de calidad.

La actividad combina **QAW** y **ATAM-lite** porque son complementarios: QAW ayuda a descubrir y refinar escenarios de calidad incluso antes de que exista una arquitectura completa, mientras ATAM evalúa una arquitectura contra objetivos de calidad y hace explícitos riesgos y trade-offs. El SEI describe QAW como complementario a ATAM y orientado a producir escenarios priorizados y refinados; ATAM, en su forma formal, tiene nueve pasos y típicamente requiere varios días. Por eso aquí se usa una adaptación académica. 

---

# 1. Duración total de la clase

Duración: **3 horas**  
Recesos: **2 × 15 minutos**  
Tiempo neto: **2 h 30 min**

## Distribución sugerida

| Tiempo | Actividad |
|---|---|
| 0:00–0:15 | Introducción: de quality attributes vagos a escenarios medibles |
| 0:15–0:35 | Lectura guiada del caso y stakeholders |
| 0:35–1:00 | QAW: generación de escenarios |
| 1:00–1:15 | **Receso 1** |
| 1:15–1:45 | QAW: priorización y refinamiento |
| 1:45–2:15 | ATAM-lite: utility tree + análisis |
| 2:15–2:30 | **Receso 2** |
| 2:30–2:50 | Presentaciones rápidas de grupos |
| 2:50–3:00 | Debrief y cierre |

---

# 2. Apertura — 15 min

## Mensaje de entrada

Comience con dos frases:

> “La arquitectura es escalable.”

> “Durante nómina, el sistema recibe 1.200 TPS durante 15 minutos y mantiene p95 ≤ 1,5 s y error rate < 0,5%.”

Pregunte:

> ¿Cuál de las dos afirmaciones se puede evaluar?

La segunda.

## Concepto clave

Un quality attribute útil para evaluación requiere contexto y una medida observable.

Use la estructura de seis partes:

```text
Source
  ↓
Stimulus
  ↓
Environment
  ↓
Artifact
  ↓
Response
  ↓
Response Measure
```

No espere que memoricen el orden exacto; sí deben comprender que el escenario elimina ambigüedad.

## Diferencia pedagógica entre QAW y ATAM

### QAW

Pregunta central:

> “¿Qué significa realmente calidad para estos stakeholders?”

Resultado esperado:

- drivers;
- escenarios;
- priorización;
- refinamiento.

### ATAM

Pregunta central:

> “Dada esta arquitectura, ¿qué decisiones soportan o ponen en riesgo esos escenarios?”

Resultado esperado:

- approaches;
- utility tree;
- risks;
- non-risks;
- sensitivity points;
- trade-offs;
- risk themes.

Aclare:

> “Hoy no vamos a ejecutar un ATAM formal. Vamos a utilizar sus mecanismos analíticos más útiles dentro de una clase.”

---

# 3. Lectura del caso — 20 min

## Cómo repartir roles

Grupos recomendados: **4–6 estudiantes**.

Asigne perspectivas, no cargos rígidos:

- Producto;
- SRE/Operaciones;
- Seguridad/Fraude;
- Cumplimiento;
- Arquitectura/Ingeniería;
- Core/Operación bancaria.

La diversidad de stakeholders importa porque un escenario valioso suele emerger de tensiones entre objetivos.

## Qué hacer mientras leen

Pídales marcar:

- cifras;
- límites;
- dependencias externas;
- componentes con capacidad conocida;
- palabras vagas;
- decisiones que parezcan tener consecuencias sobre más de un atributo.

## Elementos que idealmente deberían detectar

Sin dar aún la respuesta:

1. Peak objetivo de **1.200 TPS** vs core sostenible de **700 TPS**.
2. RTO objetivo **≤ 5 min** vs failover probado **8–12 min**.
3. RPO objetivo **0** vs réplica DR asíncrona con **15–60 s** de lag.
4. Fraude síncrono con política fail-closed.
5. Idempotency-Key en Redis + unique constraint en PostgreSQL.
6. Fraud Adapter con contrato canónico.
7. DB commit y publicación de evento no atómicos.
8. Core legado como restricción no removible.

No revele esta lista antes de que terminen la primera discusión.

---

# 4. QAW — generación de escenarios — 25 min

## Instrucción a los grupos

Cada grupo debe producir al menos seis escenarios.

Recomiende comenzar desde los comentarios ambiguos del caso.

## Qué debe vigilar el docente

### Problema 1: escenarios demasiado generales

Mal:

> “El sistema debe ser altamente disponible.”

Respuesta del docente:

> “¿Qué falla? ¿Cuándo? ¿Qué tiene que hacer el sistema? ¿En cuánto tiempo?”

### Problema 2: solución disfrazada de escenario

Mal:

> “El sistema debe usar active-active para disponibilidad.”

Respuesta:

> “Eso es una solución. ¿Cuál es la situación que queremos tolerar?”

### Problema 3: medida no verificable

Mal:

> “Responder rápidamente.”

Respuesta:

> “¿Cuánto es rápidamente?”

---

# 5. Escenarios QAW esperados

No existe una única redacción válida. Use estos como referencia.

## Q1 — Performance

**Atributo:** Performance  
**Fuente:** clientes digitales / procesos de nómina  
**Estímulo:** llegan 1.200 TPS  
**Ambiente:** pico de nómina durante 15 minutos  
**Artefacto:** flujo end-to-end de pagos  
**Respuesta:** procesa o rechaza controladamente las transferencias  
**Medida:** p95 ≤ 1,5 s; p99 ≤ 3 s; errores < 0,5%

### Qué resaltar

La medida obliga a mirar toda la cadena, no solo el Payment Orchestrator.

---

## Q2 — Recuperación regional

**Atributo:** Availability / Recoverability  
**Fuente:** falla de infraestructura  
**Estímulo:** pérdida total de región principal  
**Ambiente:** operación a 900 TPS  
**Artefacto:** plataforma crítica de pagos  
**Respuesta:** activa región secundaria y continúa operación  
**Medida:** RTO ≤ 5 min; RPO = 0 para pagos confirmados; sin doble débito

### Qué resaltar

RTO y RPO son objetivos distintos.

---

## Q3 — Idempotencia

**Atributo:** Reliability / Consistency  
**Fuente:** API Gateway / cliente  
**Estímulo:** mismo request se reenvía cinco veces con el mismo Idempotency-Key  
**Ambiente:** timeout de red en operación normal  
**Artefacto:** Payment Orchestrator + storage + core integration  
**Respuesta:** reconoce duplicados y retorna el mismo resultado lógico  
**Medida:** un solo débito; un transaction_id; respuesta ≤ 2 s

### Qué resaltar

“No duplicate debit” no es solo performance ni disponibilidad; es una propiedad de consistencia/idempotencia.

---

## Q4 — Cambio de proveedor antifraude

**Atributo:** Modifiability  
**Fuente:** negocio / seguridad  
**Estímulo:** se reemplaza proveedor antifraude  
**Ambiente:** evolución planificada  
**Artefacto:** integración de fraude  
**Respuesta:** integra el nuevo proveedor manteniendo contratos internos  
**Medida:** ≤ 6 semanas; sin cambios en mobile, web ni core

### Qué resaltar

El response measure puede expresar esfuerzo, alcance del cambio y calendario.

---

## Q5 — Caída del proveedor antifraude

**Atributo:** Availability + Security  
**Fuente:** proveedor externo  
**Estímulo:** antifraude deja de responder por 2 minutos  
**Ambiente:** operación normal o pico  
**Artefacto:** Fraud Adapter / Payment Orchestrator  
**Respuesta:** aplica política de degradación sin permitir bypass en transacciones de alto riesgo  
**Medida posible:** 100% high-risk bloqueadas o enviadas a revisión; porcentaje definido de low-risk continúa; error rate global dentro de objetivo acordado

### Qué resaltar

Este es un buen **trade-off candidate** porque seguridad y disponibilidad pueden entrar en tensión.

---

## Q6 — Auditoría

**Atributo:** Auditability / Observability  
**Fuente:** auditor / investigador  
**Estímulo:** solicita reconstrucción de una transacción  
**Ambiente:** post-incidente  
**Artefacto:** logs, traces, eventos y respuestas de core/fraude  
**Respuesta:** reconstruye la secuencia completa  
**Medida:** ≤ 10 min y correlación inequívoca mediante transaction_id/correlation_id

---

## Q7 — Event publication failure

**Atributo:** Reliability  
**Fuente:** falla del proceso o bus  
**Estímulo:** Payment Orchestrator cae después del commit y antes de publicar PaymentCompleted  
**Ambiente:** producción  
**Artefacto:** DB + publicación de eventos  
**Respuesta:** el evento eventualmente debe ser publicado exactamente una vez o de forma idempotente  
**Medida:** ningún pago confirmado queda permanentemente sin evento downstream

### Qué resaltar

Este escenario no está escrito explícitamente en los comentarios de stakeholders. Surge al examinar la arquitectura. Excelente señal de madurez del grupo.

---

# 6. QAW — priorización y refinamiento — 30 min

Después del primer receso, cada integrante asigna tres votos.

## Qué debe observar

No busque un ranking “correcto”.

Busque si el grupo puede justificar:

- impacto al negocio;
- probabilidad/frecuencia;
- dificultad arquitectónica;
- costo de falla.

## Buena pregunta docente

> “¿Un escenario puede ser muy importante aunque ocurra rara vez?”

Sí. Una falla regional o un evento de fraude puede ser poco frecuente y aun así ser crítico.

## Resultado esperado

Probablemente aparecerán arriba:

- peak performance;
- regional recovery;
- idempotency;
- fraud availability/security;
- fraud provider modifiability.

No fuerce este orden.

---

# 7. ATAM-lite — 30 min

## Paso A — Utility Tree

Pida un árbol pequeño, no exhaustivo.

Ejemplo:

```text
Utility
├── Availability
│   ├── Region failure            H / H
│   └── Fraud provider outage     H / H
├── Performance
│   └── 1.200 TPS peak            H / H
├── Reliability
│   └── Duplicate request         H / M
├── Modifiability
│   └── Replace fraud provider    M / M
└── Auditability
    └── Reconstruct transaction   M / M
```

Formato:

```text
Importance / Difficulty
```

### Qué resaltar

ATAM no prioriza solo importancia de negocio. También interesa dónde existe dificultad arquitectónica.

---

# 8. Análisis esperado de escenarios ATAM-lite

## S1 — Peak performance

### Evidencia

- objetivo: 1.200 TPS;
- Core Orchestrator escala horizontalmente;
- core legado sostenible: 700 TPS;
- fraude y core están en el camino síncrono.

### Finding esperado

**Riesgo alto.**

Aunque el Payment Orchestrator escale horizontalmente, el throughput end-to-end está limitado por el core.

### Punto de sensibilidad

- capacidad del core;
- concurrencia del Core Adapter;
- latencia de fraude;
- timeout de llamadas síncronas.

### Trade-off posible

Aumentar agresivamente concurrencia/pool del Core Adapter puede mejorar throughput inicialmente, pero también puede saturar el core y empeorar disponibilidad/latencia.

### Pregunta al grupo

> “¿Agregar 20 instancias de Payment Orchestrator resuelve el problema?”

Respuesta:

> No necesariamente. El bottleneck está aguas abajo.

### Mitigaciones válidas

- modelar capacidad real del core;
- admission control / backpressure;
- rate limiting;
- colas donde el negocio lo permita;
- negociación de SLA del flujo;
- optimización/batching solo si semánticamente válido;
- pruebas de carga end-to-end.

No acepte “poner autoscaling” como respuesta suficiente.

---

## S2 — Region failure

### Evidencia

- RTO objetivo ≤ 5 min;
- failover observado 8–12 min;
- RPO objetivo 0;
- réplica DR tiene 15–60 s de lag.

### Finding esperado

**Dos riesgos claros.**

**R1 — RTO mismatch:** arquitectura/proceso actual no demuestra ≤5 minutos.

**R2 — RPO mismatch:** replicación asíncrona no puede garantizar por sí sola RPO 0 para todo pago confirmado.

### Sensitivity points

- replication mode;
- failover automation;
- DNS/routing TTL;
- recovery procedure;
- commit semantics.

### Trade-off

Replicación sincrónica cross-region puede mejorar RPO, pero aumenta latencia y puede reducir disponibilidad ante particiones.

Este es un excelente trade-off point.

### Mitigaciones válidas

- redefinir semántica de “confirmado”;
- synchronous replication para ledger crítico;
- active-active solo si el modelo de consistencia lo soporta;
- automated failover;
- replicated log;
- ejercicios de DR periódicos;
- reconciliación explícita.

No exija una única solución.

---

## S3 — Fraud provider replacement

### Evidencia

- Fraud Adapter encapsula contrato externo;
- Orchestrator recibe decisión canónica ALLOW/REVIEW/BLOCK;
- canales y core no dependen del proveedor.

### Finding esperado

**No-riesgo razonable**, con evidencia limitada.

La decisión de adapter + canonical contract favorece modificabilidad.

### Preguntas abiertas

- ¿Existen reglas específicas del proveedor filtrándose al modelo interno?
- ¿Hay contract tests?
- ¿Qué porcentaje de lógica está dentro del adapter?
- ¿Existen diferencias semánticas entre scores de proveedores?

### Sensitivity point

La estabilidad del contrato canónico.

### Qué resaltar

Un non-risk no significa “garantizado”. Significa que la decisión observada apoya el objetivo con la evidencia actual.

---

## S4 — Duplicate request

### Evidencia

- Idempotency-Key;
- Redis TTL 24 h;
- unique constraint en PostgreSQL.

### Finding esperado

**No-riesgo parcial / decisión sólida**, pero con preguntas.

La unique constraint durable protege mejor que depender únicamente de Redis.

### Preguntas clave

- ¿Cuándo se registra la clave respecto al débito en core?
- ¿Qué pasa si el core debita pero el banco cae antes del commit local?
- ¿El Core Adapter soporta idempotencia propia?
- ¿El transaction_id se conserva al reintentar?

### Sensitivity point

Orden de operaciones entre:

```text
reserve idempotency
call core
persist result
return response
```

### Riesgo potencial

Si el core no es idempotente y el crash ocurre en la ventana incorrecta, la unique constraint local no necesariamente evita un segundo débito remoto.

Este es un buen ejemplo de por qué “tenemos Redis” no termina el análisis.

---

# 9. Findings adicionales esperados

## Event publication gap

Arquitectura:

```text
DB commit
   |
   | crash possible here
   v
publish PaymentCompleted
```

Sin transactional outbox, existe una ventana donde:

- pago está confirmado;
- evento no fue publicado;
- Notification/Analytics nunca reciben el evento.

### Clasificación

**Riesgo.**

### Mitigación típica

Transactional outbox + publisher idempotente.

### Trade-off / costo

Más complejidad operacional y procesamiento eventual.

---

## Fraud fail-closed

Política:

```text
Fraud timeout -> reject / 503
```

### Non-risk

Protege el objetivo de no bypassar fraude de alto riesgo.

### Riesgo

Disponibilidad depende directamente del proveedor antifraude.

### Trade-off point

**Security vs Availability.**

### Sensitivity point

Timeout de 400 ms y política por nivel de riesgo.

### Discusión avanzada

Una política diferenciada podría ser:

- high-risk: fail-closed;
- low-risk: fallback controlado bajo reglas explícitas;
- revisión posterior o límites reducidos.

No presente esto como recomendación automática: depende de riesgo, regulación y apetito del banco.

---

# 10. Lista de riesgos esperables

Los grupos deberían identificar al menos tres de estos:

### R1
Core de 700 TPS amenaza objetivo de 1.200 TPS.

### R2
Failover probado 8–12 min no cumple RTO ≤ 5 min.

### R3
Replica DR async de 15–60 s no demuestra RPO 0.

### R4
Commit de DB y publish de evento no atómicos.

### R5
Dependencia síncrona de fraude puede convertir fallo de tercero en indisponibilidad sistémica.

### R6
Idempotencia local puede ser insuficiente si el core remoto no participa en la semántica idempotente.

### R7
Trazabilidad se degrada dentro del core legado porque no propaga distributed trace.

No tienen que encontrar todos.

---

# 11. Non-risks esperables

## NR1 — Fraud Adapter

El contrato canónico reduce impacto del cambio de proveedor.

## NR2 — Idempotency unique constraint

La restricción durable complementa Redis y reduce riesgo de duplicados locales.

## NR3 — Async downstream para Notification/Analytics

Mantener funciones no críticas fuera del camino de respuesta puede favorecer performance y desacoplamiento.

Pero pregunte:

> “¿Sigue siendo non-risk sin outbox?”

Respuesta:

La decisión de hacerlo async puede ser positiva; la implementación de publicación no transaccional introduce otro riesgo.

Esta distinción es importante.

---

# 12. Sensitivity points esperados

1. Fraud timeout: **400 ms**.
2. Capacidad/concurrencia del Core Adapter.
3. Tipo de replicación regional.
4. TTL/idempotency retention.
5. Orden de operaciones alrededor del débito remoto.
6. Failover automation y routing TTL.
7. Canonical fraud contract.

## Frase docente

> “Un sensitivity point no es necesariamente un problema. Es una perilla arquitectónica que importa mucho.”

---

# 13. Trade-off points esperados

## T1 — Fraud policy

Más fail-closed:

- + seguridad;
- – disponibilidad.

Más fail-open:

- + disponibilidad;
- – riesgo de fraude.

## T2 — Cross-region replication

Más sincronía:

- + RPO;
- – latencia;
- posible impacto en disponibilidad durante particiones.

## T3 — Core concurrency

Más concurrencia:

- + throughput hasta cierto punto;
- – riesgo de saturar sistema legado.

---

# 14. Risk themes esperados

Un risk theme no es una lista de riesgos; debe sintetizar una causa común.

## Theme A — Critical synchronous dependencies

Agrupa:

- core legado en critical path;
- antifraude externo en critical path;
- timeouts;
- throughput limitado;
- propagación de fallas.

Redacción posible:

> “El flujo crítico depende de múltiples interacciones síncronas con sistemas de capacidad o disponibilidad no controladas por la plataforma.”

## Theme B — DR objectives not matched by data architecture

Agrupa:

- RTO mismatch;
- RPO mismatch;
- warm standby manual;
- async replication.

Redacción posible:

> “Los objetivos de continuidad son más fuertes que los mecanismos actuales de replicación y failover.”

## Theme C — Cross-boundary consistency gaps

Agrupa:

- idempotencia frente al core;
- DB/event publication gap;
- retries;
- remote side effects.

---

# 15. Presentaciones de grupos — 20 min

Máximo 5 minutos por grupo.

Pida que no lean todas las tablas.

Formato:

1. escenario más importante;
2. riesgo más importante;
3. trade-off principal;
4. recomendación prioritaria.

## Preguntas de presión

Si dicen:

> “Hay que usar Kafka.”

Pregunte:

> “¿Qué escenario resuelve y qué medida mejora?”

Si dicen:

> “Hay que migrar a microservicios.”

Pregunte:

> “¿Cuál de los riesgos identificados desaparece por dividir deployment units?”

Si dicen:

> “Hay que ir active-active.”

Pregunte:

> “¿Qué modelo de consistencia requiere el ledger y qué trade-off introduce?”

Si dicen:

> “Redis resuelve idempotencia.”

Pregunte:

> “¿Qué pasa si el side effect ocurrió en el core y luego falla la persistencia local?”

---

# 16. Debrief — 10 min

## Pregunta 1

> ¿QAW evaluó la arquitectura?

Respuesta esperada:

No principalmente. QAW ayudó a descubrir, priorizar y refinar quality attribute scenarios. Puede trabajar incluso cuando la arquitectura todavía es conceptual.

## Pregunta 2

> ¿ATAM nos dio una respuesta binaria de “buena” o “mala”?

No.

ATAM ayuda a comprender:

- cómo decisiones soportan quality goals;
- dónde hay riesgos;
- qué parámetros son sensibles;
- dónde existen trade-offs.

## Pregunta 3

> ¿Cuál fue la diferencia entre un requisito funcional y un quality attribute scenario?

Ejemplo:

Funcional:

> “El cliente puede realizar una transferencia.”

Quality scenario:

> “Durante nómina, 1.200 TPS se procesan con p95 ≤1,5 s y error rate <0,5%.”

## Pregunta de cierre

> “¿Qué hizo esta arquitectura más fácil y qué hizo más difícil?”

Conecte con la clase anterior de estilos arquitectónicos.

---

# 17. Rúbrica sugerida

Total: **20 puntos**

| Criterio | Puntos |
|---|---:|
| Escenarios QAW completos y medibles | 5 |
| Priorización justificada por business drivers | 3 |
| Análisis arquitectura ↔ escenarios | 4 |
| Riesgos / non-risks correctamente argumentados | 3 |
| Sensitivity + trade-off | 2 |
| Risk theme | 1 |
| Recomendación trazable a business driver | 2 |

## Errores frecuentes

### –1 o –2
Escenarios sin response measure.

### –1
Confundir riesgo arquitectónico con bug de implementación.

### –1
Llamar “trade-off” a cualquier decisión.

### –1
Recomendaciones tecnológicas sin conexión con escenarios.

### –1
Declarar riesgo sin evidencia del caso.

---

# 18. Extensión opcional

Si tiene tiempo o quiere dejar tarea:

## Parte A — Architecture Decision

Pida un ADR corto para una de estas decisiones:

- transactional outbox;
- DR replication strategy;
- fraud degradation policy;
- idempotency across core boundary.

Debe incluir:

- contexto;
- opciones;
- decisión;
- quality attributes afectados;
- trade-offs.

## Parte B — Re-evaluación

Después del ADR, pida:

> “¿Qué riesgos se mitigaron? ¿Qué riesgos nuevos aparecieron?”

Eso muestra que evaluar arquitectura es iterativo.

---

# 19. Referencias metodológicas para el docente

Fuentes principales del Software Engineering Institute (CMU):

1. **Quality Attribute Workshop Collection** — explica QAW como técnica para identificar quality attributes arquitectónicamente críticos, generar, priorizar y refinar escenarios.
2. **Quality Attribute Workshops (QAWs), Third Edition**, CMU/SEI-2003-TR-016.
3. **SEI Architecture Analysis Techniques and When to Use Them**, CMU/SEI-2002-TN-005 — describe cómo QAW y ATAM pueden usarse de manera complementaria.
4. **Architecture Tradeoff Analysis Method Collection** — describe los nueve pasos, utility tree, risks, non-risks, sensitivity points, trade-offs y risk themes.
5. **ATAM: Method for Architecture Evaluation**, CMU/SEI-2000-TR-004.

## Mensaje metodológico importante

Un ATAM formal no es una actividad de 30 minutos. El SEI señala que una evaluación ATAM típicamente toma varios días e involucra evaluadores entrenados, arquitectos y stakeholders.

Por eso la actividad se denomina deliberadamente:

> **ATAM-lite — adaptación académica**

El objetivo de la clase es practicar el razonamiento, no simular que se ejecutó una evaluación formal certificada.
