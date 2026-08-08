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
- Componente: backend â€” public endpoint routers
- Ambiente: docker-compose runtime (invet-backend container)
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: QA-003
- Propietario de cierre: QA (despuÃ©s de revalidar)

## Contexto

- Precondiciones: BE-002 cerrado; secure-persistence gate passed; FE-003 lint/typecheck approved; UIA-003 12/12 passed; Security review findings all RESOLVED.
- Alcance del slice: Landing pÃºblica y bÃºsqueda â€” endpoints pÃºblicos de clÃ­nicas, sucursales, servicios con filtros y paginaciÃ³n.

## Correccion aplicada

- Se verificÃ³ que los archivos de router pÃºblico existen localmente y estÃ¡n correctamente registrados en `backend/app/api/v1/router.py`.
- El Dockerfile usa `COPY . .` que incluye todos los archivos Python del directorio app.
- No hay entradas en `.dockerignore` que excluyan los routers pÃºblicos.
- Se implementaron tests de contrato para los tres routers pÃºblicos (test_public_clinics.py, test_public_branches.py, test_public_services.py).

## Pasos para revalidar

1. Reconstruir el contenedor: `docker compose up -d --build --force-recreate db backend frontend`
2. Verificar endpoints en runtime: `Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/clinicas?page=1&size=20"`
3. Verificar OpenAPI spec incluye las rutas pÃºblicas

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
- Componente: backend â€” public endpoint routers
- Ambiente: development / local
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: QA-003
- Propietario de cierre: QA (despuÃ©s de revalidar)

## Contexto

- Precondiciones: Los routers pÃºblicos existen pero carecÃ­an de archivos de prueba.
- Alcance del slice: Cada router pÃºblico debe tener tests de contrato que validen request/response.

## Correccion aplicada

- Se crearon tres archivos de prueba:
  - `backend/app/tests/api/test_public_clinics.py` â€” tests para list_clinicas y get_clinica
  - `backend/app/tests/api/test_public_branches.py` â€” tests para list_sucursales
  - `backend/app/tests/api/test_public_services.py` â€” tests para list_servicios
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
- Componente: backend â€” public endpoint routers + security testing
- Ambiente: docker-compose runtime
- Estado: `READY_FOR_REVALIDATION`
- Gate afectado: QA-003
- Propietario de cierre: QA (despuÃ©s de revalidar DEF-003-01)

## Contexto

- Precondiciones: Los endpoints pÃºblicos no estaban desplegados en runtime, lo que impedÃ­a testing de IDOR/BOLA contra endpoints reales.
- Alcance del slice: Validar que el acceso cruzado a sucursales de otras clÃ­nicas falla de forma segura.

## Correccion aplicada

- DEF-003-01 estÃ¡ listo para revalidar (routers pÃºblicos correctamente registrados).
- Una vez que DEF-003-01 se revalide y los endpoints estÃ©n en runtime, se podrÃ¡ ejecutar testing de IDOR/BOLA.
- Los tests de contrato implementados validan que los DTOs pÃºblicos no exponen campos sensibles.

## Decision

- [ ] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [x] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).
4. Validar que el acceso cruzado a recursos de otras clÃ­nicas devuelve 404

## Impacto

- Riesgo funcional: No se puede validar que los datos privados no se expongan en listados pÃºblicos.
- Riesgo de seguridad o datos: Alto â€” sin validaciÃ³n de IDOR/BOLA en runtime, existe riesgo de exposiciÃ³n de datos privados.
- Riesgo de regresion: Medio â€” los tests existentes cubren branch_profile.py pero no public_branches.py.

## Correccion sugerida

- Prueba de regresion propuesta: Implementar tests de IDOR/BOLA para cada router pÃºblico despuÃ©s de corregir DEF-003-01.
- Recomendacion: 
  1. Corregir DEF-003-01 primero (desplegar routers pÃºblicos).
  2. Crear `backend/app/tests/api/test_public_branches_idor.py` con casos de acceso cruzado.
  3. Validar que cada endpoint pÃºblico devuelve 404 para recursos de otras clÃ­nicas.
- Bloqueos externos: DEF-003-01 debe ser corregido primero.
- Accion requerida antes de continuar: Corregir deployment de routers pÃºblicos y luego implementar tests de IDOR/BOLA.

## Decision

- [x] Se puede resolver con `/implement-findings`.
- [ ] Requiere intervencion adicional externa.
- [ ] Correccion lista para revalidar (`READY_FOR_REVALIDATION`).
- [ ] QA revalido y cerro el finding (`RESOLVED`).

---

## Politica UTF-8

- El finding conserva acentos, eÃ±es y signos de apertura.
- No debe quedar mojibake como `Ãƒ`, `Ã‚` o `Ã¢`.

