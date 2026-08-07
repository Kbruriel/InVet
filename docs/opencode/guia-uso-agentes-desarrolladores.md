# Guia de uso de agentes para desarrolladores

## Objetivo

Esta guia explica como pedir trabajo a los agentes de InVet y como leer su resultado usando el flujo agentico vigente.

La unidad real de trabajo es el slice vertical. Un mismo indice funcional se representa con estos artefactos:

- `US-00X`: historias de usuario y criterios `CA-NN`
- `BE-00X`: backend
- `FE-00X`: frontend
- `QA-00X`: validacion del slice
- `UIA-00X`: automatizacion UI/E2E
- `APIA-00X`: automatizacion API

El sistema no trata backend, frontend, QA y automatizacion como esfuerzos aislados. Todo pertenece al mismo slice verificable.

## Que pedir

La forma mas estable de pedir trabajo es indicar:

- ID del slice
- objetivo funcional
- alcance MVP
- criterios de aceptacion
- restricciones o riesgos
- dependencias conocidas

Ejemplo:

```text
Implementa FE-008 para busqueda publica de clinicas.

Objetivo:
Permitir buscar clinicas y abrir su perfil publico.

Alcance:
- Ruta /search/clinics
- Listado de resultados
- Navegacion a /clinics/[clinicId]
- Estados loading, error, empty y success

Criterios de aceptacion:
- Usa el contrato API del slice
- UI responsive
- Sin mocks si el backend del slice ya existe
- Build y typecheck en verde
- Automatizacion UI y API alineada al slice
```

## Comando recomendado

Para un flujo completo, la entrada preferida es:

```text
/execute-slice FE-008
```

El orquestador normaliza el indice y ejecuta el flujo completo con gates.

Si quieres operar paso a paso, usa:

```text
/plan-task FE-008
/implement-backend-task BE-008
/implement-frontend-task FE-008
/implement-ui-automation-task FE-008
/implement-api-automation-task BE-008
/qa-task QA-008
/review-slice FE-008
/clean-architecture-review FE-008
/security-review FE-008
/run-ui-checks FE-008
/run-checks FE-008
/update-docs FE-008
/final-gate FE-008
```

`/final-gate` es opcional. Se usa cuando hace falta una segunda opinion fuerte antes de liberar el slice.

## Como funciona el flujo

### 1. Plan

`/plan-task` acepta `BE-00X`, `FE-00X` o `QA-00X`, pero siempre genera un unico plan canonico:

- `docs/opencode/plans/BE-00X-plan.md`

Ademas debe crear o actualizar estos artefactos companeros:

- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`

El plan usa `schema_version: 3` y debe incluir:

- contexto
- matriz de trazabilidad
- tareas pequenas con `Responsabilidad unica: Si`
- contrato Docker y pruebas
- plan de reportes y findings
- politica UTF-8

El planner no implementa codigo. Si el plan queda incompleto, compuesto o con encoding roto, el flujo debe bloquearse ahi.

### 2. Implementacion backend

Usa `/implement-backend-task BE-00X` cuando el slice toque:

- endpoints
- dominio
- casos de uso
- persistencia
- permisos
- seguridad
- pruebas unitarias backend

El implementador backend debe leer el plan y ejecutar su preflight antes de editar. Si la tarea mezcla varias responsabilidades, debe devolverla al planner para division.

### 3. Implementacion frontend

Usa `/implement-frontend-task FE-00X` cuando el slice toque:

- rutas
- componentes
- layouts
- formularios
- cliente API
- estados UX
- pruebas unitarias o de componente

El implementador frontend consume el mismo plan canonico y debe respetar contratos API, estados UX y granularidad del slice.

### 4. Automatizacion UI

Usa `/implement-ui-automation-task FE-00X` cuando el slice tenga experiencia visible en navegador.

Este agente debe:

- leer `US-00X` y `UIA-00X`
- cubrir navegacion, formularios, redirects y estados UX con Playwright
- implementar pruebas en `InVet_UI_Automation/tests/e2e`
- actualizar `UIA-00X.md` con cobertura, evidencia, bloqueos y casos no automatizados

Si falta `UIA-00X.md`, el trabajo debe volver a `/plan-task`.

### 5. Automatizacion API

Usa `/implement-api-automation-task BE-00X` cuando el slice exponga o consuma contratos HTTP verificables.

Este agente debe:

- leer `US-00X` y `APIA-00X`
- cubrir contratos HTTP con Playwright `APIRequestContext`
- implementar pruebas en `InVet_UI_Automation/tests/api`
- actualizar `APIA-00X.md` con cobertura, evidencia, bloqueos y casos no automatizados

Si falta `APIA-00X.md`, el trabajo debe volver a `/plan-task`.

### 6. QA

Usa `/qa-task QA-00X` cuando backend, frontend y automatizacion ya tienen una version candidata.

QA:

- valida backend, frontend e integracion
- revisa cobertura funcional y gaps unitarios
- consume evidencia de `US`, `UIA` y `APIA`
- puede crear pruebas QA de aceptacion, integracion, contrato, seguridad y regresion
- no corrige codigo productivo

Resultados esperados:

- `docs/opencode/qa/QA-00X-results.md`
- `docs/opencode/qa/QA-00X-findings.md` cuando hay hallazgos o bloqueos

Decisiones posibles:

- `APPROVED`
- `REJECTED`
- `BLOCKED`

Antes de declarar `BLOCKED`, QA intenta autorecuperacion de entorno:

- preparar dependencias
- usar `.env.qa`
- mover la validacion a Docker si el host no representa el entorno real

### 7. Reviews

Despues de QA aprobado, entran las revisiones:

- `/review-slice BE-00X` o `/review-slice FE-00X`
- `/clean-architecture-review FE-00X`
- `/security-review FE-00X`

Artefactos esperados:

- `docs/opencode/reviews/BE-00X-review.md`
- `docs/opencode/reviews/BE-00X-clean-architecture-review.md`
- `docs/opencode/reviews/BE-00X-security-review.md`

Si alguien intenta usar `QA-00X` en `/review-slice`, el comando debe rechazar esa entrada y redirigir a `/qa-task QA-00X`.

### 8. Correccion de hallazgos

Usa `/implement-findings` cuando QA o una review dejaron hallazgos accionables.

Acepta:

- `BE-00X`
- `FE-00X`
- una ruta puntual a un archivo de findings

El agente:

- consolida hallazgos del slice
- corrige codigo y pruebas de la capa responsable
- deja evidencia en `docs/opencode/reviews/BE-00X-corrections.md`
- cambia findings corregidos a `READY_FOR_REVALIDATION`

No puede marcar `RESOLVED`. Solo QA puede cerrar formalmente un finding.

### 9. Checks y documentacion

`/run-ui-checks FE-00X` ejecuta el gate de automatizacion UI del workspace `InVet_UI_Automation`.

`/run-checks FE-00X` ejecuta el gate tecnico integral del slice.

Ambos deben distinguir entre:

- `pass`
- `fail`
- `skipped`
- `blocked`

`skipped` solo es valido cuando algo realmente no aplica. Un entorno roto o un comando fallido no cuentan como `skipped`.

El reporte formal esperado para cierre tecnico es:

- `docs/opencode/checks/BE-00X-checks.md`

Despues, `/update-docs FE-00X` consolida el cierre documental del slice.

### 10. Gate final

`/final-gate FE-00X` revisa:

- resultados QA
- findings
- reviews
- UI checks
- checks
- documentacion

El artefacto esperado es:

- `docs/opencode/reviews/BE-00X-final-review.md`

Este gate no reemplaza QA ni checks. Solo valida el cierre global del slice cuando se requiere una segunda opinion fuerte.

## Como pedir bien cada tipo de trabajo

### Pedido para plan

```text
Genera el plan del slice FE-008.
Usa schema v3.
Divide el trabajo en tareas pequenas con responsabilidad unica.
Incluye trazabilidad, contrato frontend, Docker/pruebas, reportes esperados y politica UTF-8.
Ademas crea o actualiza US-008, UIA-008 y APIA-008.
```

### Pedido para backend

```text
Implementa BE-008 segun el plan vigente.
Respeta el contrato API del slice.
Agrega las pruebas unitarias backend necesarias.
No cierres tareas compuestas; si el plan esta mal dividido, bloquealo.
```

### Pedido para frontend

```text
Implementa FE-008 segun el plan vigente.
Conecta el cliente API real del slice.
Incluye loading, error, empty y success.
Agrega pruebas de frontend necesarias y valida build/typecheck.
```

### Pedido para automatizacion UI

```text
Implementa UIA-008 para el slice FE-008.
Cubre happy path, negative path y estados UX visibles.
Usa Playwright y actualiza UIA-008 con evidencia y gaps.
```

### Pedido para automatizacion API

```text
Implementa APIA-008 para el slice BE-008.
Valida contratos HTTP, auth, errores y estados relevantes.
Usa Playwright APIRequestContext y actualiza APIA-008 con evidencia y gaps.
```

### Pedido para QA

```text
Ejecuta QA-008 sobre el slice vertical.
Valida happy path, negative path, estados UX, permisos si aplica, regresion y gaps unitarios.
Consume la cobertura de US-008, UIA-008 y APIA-008.
Documenta results y findings con evidencia reproducible.
```

### Pedido para findings

```text
Implementa los findings de FE-008.
Corrige solo los puntos del slice.
Deja las correcciones en READY_FOR_REVALIDATION y reejecuta los checks relevantes.
```

## Artefactos que debes esperar

Por slice, los archivos clave son:

- `docs/opencode/plans/BE-00X-plan.md`
- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`
- `docs/opencode/qa/QA-00X-results.md`
- `docs/opencode/qa/QA-00X-findings.md`
- `docs/opencode/reviews/BE-00X-review.md`
- `docs/opencode/reviews/BE-00X-clean-architecture-review.md`
- `docs/opencode/reviews/BE-00X-security-review.md`
- `docs/opencode/reviews/BE-00X-corrections.md` si hubo correcciones
- `docs/opencode/checks/BE-00X-checks.md`
- `docs/opencode/reviews/BE-00X-final-review.md` si hubo gate final

La existencia del archivo no basta. Debe contener una decision valida y evidencia actual.

## Docker y entorno

Cuando el slice requiere persistencia real o runtime integrado:

- levantar `db` con `docker compose up -d db`
- correr pruebas backend dentro de `backend`
- recrear `db backend frontend` solo si hay cambios relevantes

El stack completo:

```text
docker compose up -d --build --force-recreate db backend frontend
```

No debe ejecutarse por reflejo en cada comando. Primero hay que revisar si hubo cambios relevantes en:

- `backend`
- `frontend`
- `docker-compose.yml`
- `Dockerfile*`
- lockfiles o manifiestos de dependencias

## Reglas de oro

- No pidas cerrar un slice sin plan schema v3.
- No cierres el slice si faltan `US-00X`, `UIA-00X` o `APIA-00X`.
- No cierres QA si faltan pruebas unitarias explicitas en archivos productivos del slice.
- No trates un `skipped` como aprobacion silenciosa.
- No mezcles cambios no relacionados dentro del mismo slice.
- No uses `/review-slice QA-00X`; para eso existe `/qa-task QA-00X`.
- No marques findings QA como `RESOLVED` fuera de QA.
- No asumas que una corrida local equivale a una corrida en contenedor cuando el criterio exige PostgreSQL o runtime real.
- Todo artefacto operativo nuevo debe conservar UTF-8.

## Cierre esperado

Un slice esta realmente cerrado cuando:

- el plan esta validado
- `US-00X`, `UIA-00X` y `APIA-00X` existen y estan actualizados
- backend y frontend completaron sus entregables
- la automatizacion UI y API del slice quedo implementada cuando aplica
- QA quedo `APPROVED`
- no quedan findings bloqueantes
- las tres reviews estan `APPROVED`
- `run-ui-checks` quedo aprobado cuando aplica
- checks estan `APPROVED`
- documentacion esta actualizada
- el gate final, si se uso, tambien quedo `APPROVED`

Si cualquiera de esos puntos falta, el slice sigue abierto aunque el codigo "ya funcione".
