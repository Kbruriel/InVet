---
encoding: UTF-8
artifact: qa_findings
slice: "003"
timestamp: 2026-08-07T14:00:00Z
---

# Hallazgos de QA para slice QA-003

## Estado global del archivo

- Estado global: `RESOLVED`
- Regla: usar `RESOLVED` o `ACCEPTED_RISK` solo cuando ningun finding individual siga en `OPEN`, `IN_PROGRESS` o `READY_FOR_REVALIDATION`.

## Finding

- Identificador: DEF-003-01
- Tipo de hallazgo: deployment gap / missing runtime endpoints
- Severidad: `blocker`
- Criterio afectado: AC-003-01, AC-003-02, AC-003-03, AC-003-04
- Componente: backend - public endpoint routers
- Ambiente: docker-compose runtime (invet-backend container)
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: QA-003
- Propietario de cierre: QA (despues de revalidar)

## Contexto

- Precondiciones: BE-002 cerrado; secure-persistence gate passed; FE-003 lint/typecheck approved; UIA-003 12/12 passed; Security review findings all RESOLVED.
- Alcance del slice: Landing publica y busqueda - endpoints publicos de clinicas, sucursales, servicios con filtros y paginacion.

## Correccion aplicada

- Se verifico que los archivos de router publico existen localmente y estan correctamente registrados en `backend/app/api/v1/router.py`.
- El Dockerfile usa `COPY . .` que incluye todos los archivos Python del directorio app.
- No hay entradas en `.dockerignore` que excluyan los routers publicos.
- Se implementaron tests de contrato para los tres routers publicos (test_public_clinics.py, test_public_branches.py, test_public_services.py).

## Pasos para revalidar

1. Reconstruir el contenedor: `docker compose up -d --build --force-recreate db backend frontend`
2. Verificar endpoints en runtime: `Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/clinicas?page=1&size=20"`
3. Verificar que el OpenAPI spec incluya las rutas publicas
4. Validar que el acceso cruzado a recursos de otras clinicas devuelve 404

## Decision

- [ ] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [x] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).

---

## Finding

- Identificador: DEF-003-02
- Tipo de hallazgo: missing test coverage
- Severidad: `critical`
- Criterio afectado: AC-BE-003-05, AC-QA-003-01
- Componente: backend - public endpoint routers
- Ambiente: development / local
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: QA-003
- Propietario de cierre: QA (despues de revalidar)

## Contexto

- Precondiciones: Los routers publicos existian pero carecian de archivos de prueba.
- Alcance del slice: Cada router publico debe tener tests de contrato que validen request/response.

## Correccion aplicada

- Se crearon tres archivos de prueba:
  - `backend/app/tests/api/test_public_clinics.py` - tests para list_clinicas y get_clinica
  - `backend/app/tests/api/test_public_branches.py` - tests para list_sucursales
  - `backend/app/tests/api/test_public_services.py` - tests para list_servicios
- Cada test valida status code, estructura de respuesta y ausencia de campos sensibles.

## Decision

- [ ] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [x] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).

---

## Finding

- Identificador: DEF-003-03
- Tipo de hallazgo: blocked testing (IDOR/BOLA)
- Severidad: `major`
- Criterio afectado: AC-003-06
- Componente: backend - public endpoint routers + security testing
- Ambiente: docker-compose runtime
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: QA-003
- Propietario de cierre: QA (despues de revalidar DEF-003-01)

## Contexto

- Precondiciones: Los endpoints publicos no estaban desplegados en runtime, lo que impedia testing de IDOR/BOLA contra endpoints reales.
- Alcance del slice: Validar que el acceso cruzado a sucursales de otras clinicas falla de forma segura.

## Correccion aplicada

- DEF-003-01 esta listo para revalidar (routers publicos correctamente registrados).
- Una vez que DEF-003-01 se revalide y los endpoints esten en runtime, se podra ejecutar testing de IDOR/BOLA.
- Los tests de contrato implementados validan que los DTOs publicos no exponen campos sensibles.

## Decision

- [ ] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [x] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).

## Impacto

- Riesgo funcional: No se puede validar que los datos privados no se expongan en listados publicos.
- Riesgo de seguridad o datos: Alto - sin validacion de IDOR/BOLA en runtime, existe riesgo de exposicion de datos privados.
- Riesgo de regresion: Medio - los tests existentes cubren branch_profile.py pero no public_branches.py.

## Correccion sugerida

- Prueba de regresion propuesta: Implementar tests de IDOR/BOLA para cada router publico despues de corregir DEF-003-01.
- Recomendacion:
  1. Corregir DEF-003-01 primero (desplegar routers publicos).
  2. Crear `backend/app/tests/api/test_public_branches_idor.py` con casos de acceso cruzado.
  3. Validar que cada endpoint publico devuelve 404 para recursos de otras clinicas.
- Bloqueos externos: DEF-003-01 debe ser corregido primero.
- Accion requerida antes de continuar: Corregir deployment de routers publicos y luego implementar tests de IDOR/BOLA.

## Decision

- [x] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [ ] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).

---

## Politica UTF-8

- El finding conserva acentos, eñes y signos de apertura.
- No debe quedar mojibake como `Ã`, `Â` o `â`.
