# QA-003 - Landing publica y busqueda

## Fecha de ejecucion

- 3 de agosto de 2026

## Estado general

- Resultado: PASS
- Decision: APPROVED
- Slice validado: BE-003 / FE-003 / QA-003
- Nota: el reporte anterior de bloqueo por infraestructura queda reemplazado por evidencia actual del repo y del stack de Docker.

## Evidencia ejecutada

| Verificacion | Comando | Resultado |
|---|---|---|
| Preflight QA | `python backend/scripts/validate_slice_plan.py QA-003 --stage qa` | PASS |
| Preflight plan | `python backend/scripts/validate_slice_plan.py BE-003 --stage plan` | PASS |
| Backend + frontend + Docker hook | `run-checks.ps1` | PASS |
| Backend clinic API smoke | `python -m pytest app/tests/test_clinic_api.py -q` | 18 passed |
| Frontend regression | `npm test -- --run` | 25 files / 36 tests passed |
| Frontend build | `npm run build` | PASS |
| Docker stack | `docker compose ps` | `db`, `backend` y `frontend` en healthy/up |

## Cobertura por criterio

### Criterio 1: Happy path validado
- Estatus: PASS
- Evidencia: la landing publica renderiza resultados y el backend responde con contratos activos para el slice.

### Criterio 2: Negative path validado
- Estatus: PASS
- Evidencia: la busqueda sin coincidencias muestra estado vacio y los errores del backend se mantienen controlados.

### Criterio 3: Permisos validados
- Estatus: PASS
- Evidencia: el endpoint protegido del slice requiere autenticacion; el flujo publico permanece accesible sin credenciales.

### Criterio 4: IDOR/BOLA validado si aplica
- Estatus: PASS
- Evidencia: el perfil publico y el perfil protegido conservan separacion de datos y no exponen recursos administrativos de forma cruzada.

### Criterio 5: Regresion minima validada
- Estatus: PASS
- Evidencia: la corrida completa de checks paso sin regresiones en backend ni frontend.

### Criterio 6: Evidencia documentada
- Estatus: PASS
- Evidencia: este archivo reemplaza el baseline stale y enlaza comandos ejecutados con la decision final.

## Hallazgos

- No hay defects abiertos para el alcance validado en esta corrida.

## Riesgo residual

- El explorador publico usa un dataset local en la UI mientras se sigue consolidando el contrato de busqueda del slice.
- Persisten avisos menores de mantenimiento en el repo, pero no bloquearon la validacion.

## Conclusiones

- El problema reportado como "falta de infraestructura" no corresponde al estado actual.
- La validacion de QA-003 pasa con el entorno actual, el plan v2 y la evidencia de tests y build.
