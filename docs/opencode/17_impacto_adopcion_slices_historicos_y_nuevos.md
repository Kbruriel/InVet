# Impacto de la adopcion Brain-InVet en slices historicos y nuevos

## 1. Decision recomendada

La adopcion debe usar dos politicas distintas:

- **Slices historicos**: migracion retrospectiva, no invasiva y basada en la evidencia existente.
- **Slices nuevos**: aplicacion completa de trazabilidad, certeza, riesgo y aprobaciones desde la planeacion.

No se recomienda reabrir automaticamente un slice aprobado ni exigirle artefactos que no formaban parte de su contrato original. La nueva capa debe explicar y enlazar el cierre historico, no reescribirlo.

## 2. Estado observado de los slices existentes

La revision del repositorio muestra que `status: COMPLETED` no siempre equivale a un gate final aprobado. El estado real debe obtenerse de la combinacion del plan, QA, revisiones, checks y gate final.

| Slice | Estado del plan | Evidencia de gate final | Clasificacion para migracion |
|---|---|---|---|
| 001 | `DONE`, schema v2 | `APPROVED` | Cerrado historico; elegible para certificacion legacy |
| 002 | `BACKEND_FRONTEND_IMPLEMENTED` | No existe final review | No cerrado; no debe certificarse |
| 003 | `COMPLETED` | `BLOCKED` | Estado contradictorio; requiere conciliacion |
| 004 | `COMPLETED` | `APPROVED` | Cerrado historico; elegible para certificacion legacy |
| 005 | `PLANNED` | `REJECTED` por seguridad y APIA faltante | No cerrado; mantiene bloqueadores reales |
| 006 | `COMPLETED` | No existe final review | Cierre no demostrable; requiere completar o reconstruir el gate |
| 007 | `IMPLEMENTED` | `BLOCKED` | Implementado, pero no cerrado |
| 008 | `COMPLETED` | `APPROVED` | Cerrado historico; elegible para certificacion legacy |
| 009 | `IN_PROGRESS` | `APPROVED` | Gate aprobado con metadata desactualizada; conciliacion documental |
| 010 | `COMPLETED` | `APPROVED` | Cerrado historico; elegible para certificacion legacy |
| 011 | `COMPLETED` | `APPROVED` | Cerrado historico; elegible para certificacion legacy |

Por tanto, existen cinco cierres consistentes y comprobables —001, 004, 008, 010 y 011—, un cierre funcional aprobado con deriva de metadata —009— y varios slices que no deben considerarse cerrados solo por el estado del plan.

Este hallazgo es, por si mismo, uno de los primeros beneficios de la adopcion: una entidad de cambio no podria declarar cierre si su evidencia final expresa `BLOCKED` o `REJECTED`.

## 3. Impacto sobre slices terminados y cerrados

### 3.1 Lo que no debe cambiar

Para los slices con gate final aprobado:

- no se modifica el codigo entregado;
- no se reescribe el plan original;
- no se vuelven a ejecutar automaticamente pruebas historicas;
- no se cambia la decision del gate original;
- no se inventan requisitos, ADR o evidencias que no existieron;
- no se aplican retroactivamente umbrales de riesgo nuevos.

Su cierre debe quedar registrado como `legacy-certified`, acompañado por la version de politica bajo la cual fue aceptado.

### 3.2 Lo que se añade

La migracion genera una vista derivada por slice con:

- requisito de origen: `US-00X` y criterios `CA-*`;
- cambio: `CHG-00X`, enlazado al plan y a las tareas BE/FE/QA/UIA/APIA;
- decisiones conocidas: referencias a documentos existentes;
- evidencias: QA, revisiones, checks y gate final;
- hashes de los artefactos enlazados;
- etiqueta de certeza por relacion;
- estado de integridad del cierre;
- fecha y version de la migracion.

Ejemplo conceptual:

```yaml
change: CHG-001
source_slice: BE-001
migration_mode: retrospective
closure:
  status: legacy-certified
  decision: APPROVED
  policy_version: pre-governance-v1
traceability:
  requirement: US-001
  certainty: confirmed
evidence:
  - path: docs/opencode/qa/QA-001-results.md
    relation: confirmed
  - path: docs/opencode/reviews/BE-001-final-review.md
    relation: confirmed
```

El archivo seria generado. Las fuentes canonicas seguirian siendo los artefactos originales.

### 3.3 Beneficios para los cierres historicos

#### Auditoria mas rapida

Se podra conocer, desde un unico indice, que requisito cubrio un slice, que componentes modifico y que pruebas permitieron aprobarlo.

#### Analisis de impacto

Cuando un nuevo cambio toque autenticacion, pagos, propietarios, mascotas o citas, el agente podra identificar que slices historicos y que decisiones pueden verse afectados.

#### Deteccion de deriva

Los hashes permiten detectar que una evidencia o plan historico cambio despues del cierre. El cambio no invalida automaticamente el slice, pero obliga a explicar la nueva version.

#### Conservacion de conocimiento

Las decisiones dejan de depender de recordar conversaciones anteriores. Los nuevos agentes pueden reconstruir por que existe una ruta, una regla de autorizacion o un modelo de datos.

#### Seguridad acumulativa

El riesgo de un cambio nuevo puede considerar lo que ya existe. Por ejemplo, una modificacion en pagos puede heredar controles y riesgos de BE-011 sin volver a descubrirlos desde cero.

## 4. Tratamiento de slices historicos inconsistentes

La adopcion no debe ocultar contradicciones. Debe crear una cola de conciliacion:

### BE-003

El plan dice `COMPLETED`, pero la revision final dice `BLOCKED`. Debe conservarse como `closure-disputed` hasta determinar si existe una revalidacion posterior que realmente resolvio el bloqueo.

### BE-005

La revision final rechaza el release por endpoints administrativos sin autenticacion/autorizacion y por API automation faltante. No debe migrarse como cerrado. El nuevo modelo permitiria clasificarlo como riesgo alto o critico y exigir aprobacion humana y evidencia de correccion.

### BE-006

Tiene QA, revisiones y checks, pero no se encontro final review. Puede reconstruirse un gate usando evidencia existente, pero la decision nueva debe declarar que es una **certificacion retrospectiva**, no fingir que el gate ocurrio en la fecha original.

### BE-007

La implementacion existe, pero el gate esta `BLOCKED`. Debe permanecer abierto hasta resolver o cancelar formalmente sus hallazgos.

### BE-009

El gate final esta aprobado, mientras el plan conserva `IN_PROGRESS`. Es un caso de deriva documental. Si no hay evidencia posterior contradictoria, bastaria corregir la metadata mediante un cambio auditado y luego clasificarlo como cerrado.

### BE-002

El estado solo confirma implementacion backend/frontend y no existe gate final. Debe mantenerse como historico incompleto, aunque otros slices dependan de sus capacidades.

## 5. Como beneficiaria a los slices nuevos

### 5.1 Antes de implementar

Cada slice nuevo nacera con:

- requisito y criterios de aceptacion identificados;
- stakeholders y aprobador definidos;
- hechos confirmados separados de inferencias;
- componentes e integraciones afectados;
- ADR aplicables o nueva decision requerida;
- puntaje de riesgo;
- nivel de autonomia permitido;
- dependencias y carryovers enlazados.

Esto reduce planes ambiguos y evita que una suposicion del agente se convierta en alcance oficial.

### 5.2 Durante la implementacion

El flujo actual de InVet se conserva, pero cada agente recibe contexto mas preciso:

- Backend y Frontend conocen requisitos, decisiones e invariantes aplicables.
- UIA y APIA generan evidencia enlazada a criterios concretos.
- Los hashes y checkpoints conservan la capacidad de reanudar.
- Los cambios de alcance generan una relacion explicita, en vez de modificar silenciosamente el plan.
- El paralelismo se habilita solo cuando dependencias y archivos no colisionan.

### 5.3 Durante QA y revisiones

QA no solo comprobara que las pruebas pasan. Tambien verificara:

- cobertura de todos los criterios;
- correspondencia entre requisito, implementacion y evidencia;
- resolucion de inferencias importantes;
- cumplimiento de ADR e invariantes;
- aprobaciones humanas exigidas por riesgo;
- ausencia de carryovers abiertos no autorizados.

Las revisiones funcional, de arquitectura y de seguridad mantendran su independencia actual.

### 5.4 En el cierre

Un slice solo podra cerrarse cuando coincidan cuatro estados:

```text
Plan COMPLETED
  + QA y revisiones APPROVED
  + Evidencia completa e integra
  + Aprobaciones de riesgo satisfechas
  = CHG CLOSED
```

Esto impediria contradicciones como plan `COMPLETED` con final gate `BLOCKED` o plan `IN_PROGRESS` con gate final `APPROVED`.

### 5.5 Despues del cierre

El slice nuevo se convierte automaticamente en contexto confiable para los siguientes:

- facilita regresiones dirigidas por impacto;
- permite reutilizar decisiones e invariantes;
- reduce el redescubrimiento del dominio;
- muestra que evidencia debe repetirse cuando se modifica un componente;
- mejora auditorias, soporte e investigacion de incidentes.

## 6. Diferencia operativa entre historico y nuevo

| Control | Slice historico aprobado | Slice nuevo |
|---|---|---|
| Grafo de trazabilidad | Generado retrospectivamente | Obligatorio desde el plan |
| `confirmed/inferred` | Aplicado a relaciones reconstruidas | Aplicado a todo el ciclo |
| Riesgo | Evaluacion informativa del riesgo actual | Determina autonomia y aprobaciones |
| ADR | Solo decisiones relevantes aun vigentes | Obligatorio cuando hay decision significativa |
| Evidencia | Se enlaza, no se recrea | Se genera y enlaza durante cada gate |
| Politica de cierre | Se conserva la original | Se aplica la politica nueva |
| Reapertura | Solo por contradiccion o riesgo activo grave | Por cambio de alcance, fallo o evidencia invalida |
| CI | Comprueba integridad del indice | Comprueba plan, ejecucion, evidencia y cierre |

## 7. Costos y riesgos de la adopcion

### Sobredocumentacion

Crear manualmente REQ, CHG, ADR y EVD duplicaria el trabajo. La mitigacion es generarlos o indexarlos desde `US`, planes y resultados existentes.

### Falsificacion retrospectiva involuntaria

Completar huecos historicos con inferencias puede aparentar evidencia que nunca existio. Todo dato reconstruido debe incluir procedencia y certeza.

### Reapertura masiva

Aplicar nuevas reglas retroactivamente paralizaria el proyecto. Solo deben reabrirse cierres por contradiccion demostrable, vulnerabilidad activa, perdida de datos o incumplimiento legal relevante.

### Rigidez excesiva

No todo cambio necesita un ADR o aprobacion humana. La profundidad debe depender del riesgo y de si existe una decision arquitectonica real.

### Segunda fuente de verdad

El grafo no debe editarse manualmente para contradecir los planes y resultados. Debe ser una vista derivada y verificable.

## 8. Plan de adopcion recomendado

### Fase 1 — Inventario sin alterar cierres

1. Congelar un snapshot y hashes de planes, QA, revisiones y checks.
2. Clasificar cada slice como `legacy-certified`, `incomplete`, `blocked`, `rejected` o `closure-disputed`.
3. Registrar contradicciones sin corregirlas automaticamente.

### Fase 2 — Piloto historico

4. Generar trazabilidad retrospectiva para 001, 004 y 011: base tecnica, un slice funcional intermedio y el cierre mas reciente.
5. Medir cuantos enlaces se generan automaticamente y cuantos requieren confirmacion humana.
6. Ajustar el esquema antes de migrar los demas cierres aprobados.

### Fase 3 — Conciliacion

7. Resolver metadata de 009.
8. Auditar los bloqueos de 003, 005 y 007.
9. Decidir si 002 y 006 se completan, se certifican retrospectivamente o se archivan como incompletos.

### Fase 4 — Aplicacion prospectiva

10. Aplicar el contrato completo al siguiente slice que aun no haya iniciado implementacion.
11. Ejecutar el primer ciclo con riesgo y aprobaciones en modo informativo.
12. Volver obligatorios los gates nuevos despues de validar que no producen falsos bloqueos.

### Fase 5 — CI y operacion continua

13. Añadir verificacion del grafo, hashes, estados y aprobaciones a CI.
14. Generar `status`, `doctor` y `verify` sobre los scripts actuales.
15. Revisar periodicamente inferencias abiertas, evidencia alterada y ADR impactados.

## 9. Indicadores para medir el beneficio

La adopcion deberia considerarse exitosa si reduce:

- slices con estado contradictorio;
- criterios sin evidencia enlazada;
- hallazgos descubiertos solamente en el gate final;
- tiempo para reconstruir el impacto de un cambio;
- inferencias sin confirmar al iniciar implementacion;
- reaperturas por dependencias o carryovers olvidados.

Y si aumenta:

- porcentaje de requisitos con evidencia completa;
- decisiones arquitectonicas con contexto recuperable;
- riesgos altos detectados antes de implementar;
- ejecuciones reanudadas sin reinterpretar tareas;
- cierres verificables automaticamente.

## 10. Resultado esperado

Para los slices terminados, la adopcion aporta memoria, auditoria y deteccion de deriva sin destruir la validez de los cierres originales.

Para los slices nuevos, aporta prevencion: menos ambiguedad al planear, autonomia proporcional al riesgo, evidencia creada durante el trabajo y una unica definicion verificable de `CLOSED`.

El mayor beneficio inmediato para InVet no seria crear mas documentos, sino eliminar la diferencia actual entre **“el plan dice que termino”** y **“la evidencia demuestra que puede cerrarse”**.
