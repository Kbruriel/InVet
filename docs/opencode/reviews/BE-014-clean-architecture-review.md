---
encoding: UTF-8
artifact: review_clean_architecture
slice: BE-014
aliases: [FE-014]
type: clean-architecture
date: 2026-09-01
estado: APPROVED
decision: APPROVED
---

# Revisión de arquitectura limpia para slice BE-014 — Soporte básico

## Normalización y agente ejecutor

El comando recibido fue `/clean-architecture-review FE-014`. `FE-014` se
normaliza al slice vertical `BE-014` (índice `014`), porque el backend es la
fuente de contrato para la UI. Este gate debe ejecutarse con el agente
`invet-clean-architecture-reviewer` (GitHub Copilot: **InVet Clean Architecture
Reviewer**). El revisor no modifica código de producto; únicamente inspecciona
la implementación y escribe este informe.

## Bloqueo operativo de PowerShell y solución reusable

La ejecución quedó bloqueada por `&&`: Windows PowerShell 5.1 no reconoce ese
token como separador de instrucciones. La solución es configurar el directorio
de trabajo (`workdir`) directamente y ejecutar cada comprobación como una
invocación independiente. No se debe usar `cd ... && ...`.

Comandos reproducibles desde `C:\InVet`:

```powershell
python backend/scripts/validate_slice_plan.py FE-014 --stage plan
python backend/scripts/validate_slice_plan.py FE-014 --stage backend
python backend/scripts/manage_slice_task.py verify FE-014 --layer all
python -m pytest backend/tests/api/test_support_ticket_migration.py -q
python -m pytest backend/app/tests/api/test_support_ticket_api.py backend/app/tests/data/test_support_ticket_repo.py backend/app/tests/usecases -q
git diff --check
```

Si se necesita una secuencia fail-fast en una sola sesión, usar sintaxis de
PowerShell (`;` y `$LASTEXITCODE`) o, preferiblemente, separar las invocaciones:

```powershell
python backend/scripts/validate_slice_plan.py FE-014 --stage plan
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python backend/scripts/validate_slice_plan.py FE-014 --stage backend
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Para Docker, cada comando también se ejecuta por separado:

```powershell
docker compose up -d db
docker compose build backend
docker compose run --rm backend pytest tests/api/test_support_ticket_migration.py -q
```

El servicio `backend` usa `/app` como directorio de trabajo; por eso las rutas
de pruebas dentro del contenedor son relativas a `/app` (`tests/api/...`) y no
incluyen el prefijo `backend/`. Si se modifica una prueba o el código copiado en
la imagen, se debe reconstruir `backend` antes de `docker compose run`; de lo
contrario se puede ejecutar una imagen obsoleta. La prueba de migración se hizo
portable resolviendo `BACKEND_DIR` desde `Path(__file__)`, válido tanto en
`C:\\InVet\\backend` como en `/app`.

## Evidencia ejecutada

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Validación del plan | PASS | `validate_slice_plan.py FE-014 --stage plan` |
| Validación backend | PASS | `validate_slice_plan.py FE-014 --stage backend` |
| Coherencia de manifiestos | PASS | `manage_slice_task.py verify FE-014 --layer all` |
| Migración Alembic | PASS | 4 pruebas en `backend/tests/api/test_support_ticket_migration.py` |
| Migración Alembic en Docker | PASS | `docker compose run --rm backend pytest tests/api/test_support_ticket_migration.py -q` → 4 passed (2 warnings de caché de pytest) |
| Backend de soporte | PASS | 51 pruebas dirigidas; 2 warnings no bloqueantes de SQLAlchemy |
| Integridad del diff | PASS | `git diff --check` sin errores (solo avisos de LF/CRLF) |

## Validación SQL y Alembic

- `backend/app/infrastructure/database/models/__init__.py` registra y exporta
  `SupportTicket`, `TicketCategory` y `TicketStatus`; `Base.metadata` puede
  descubrir ambas tablas sin imports explícitos del test.
- `backend/app/infrastructure/database/models/support_ticket_model.py` y
  `backend/alembic/versions/a014_support.py` están alineados: tablas
  `ticket_categories` y `support_tickets`, columnas requeridas, claves foráneas
  con `CASCADE` donde corresponde, índices de clínica/owner/status y unicidad de
  categoría por clínica.
- La migración `a014` es idempotente respecto al seed: inserta exactamente las
  tres categorías mínimas (`Fattura`, `Comportamiento`, `Veterinaria`) por
  clínica sin duplicarlas.
- `upgrade()` y `downgrade()` fueron verificados; el downgrade elimina primero
  `support_tickets` y después `ticket_categories`, y devuelve la revisión
  anterior `a013`.
- No existe un módulo Python duplicado bajo la ruta mal escrita
  `backend/app/infraestructure`; solo quedan directorios vacíos sin código
  importable.
- El warning de relación SQLAlchemy (`SupportTicket.category`/
  `TicketCategory.tickets`) no rompe el contrato ni las pruebas; queda como
  observación menor para una futura limpieza con `back_populates`/`overlaps`.

## Diff final contra AC-014

| Criterio | Evidencia | Estado |
|---|---|---|
| AC-01 Crear ticket | Router, caso de uso y pruebas C1/C2 | PASS |
| AC-02 Categorías activas y deduplicación | Repo, seed y pruebas C7/C13 | PASS |
| AC-03 Listado paginado | Repo/router y pruebas C3/C11 | PASS |
| AC-04 Detalle autorizado | Aislamiento owner/clínica y prueba C4 | PASS |
| AC-05 Transiciones | Reglas en application y C5/C6/C12 | PASS |
| AC-06 Datos iniciales | Seed Alembic de 3 categorías por clínica | PASS |
| AC-07 Autenticación | Dependencia bearer y prueba C10 | PASS |
| AC-08 Formulario | FE-014-T01/T02 y suites frontend | PASS |
| AC-09 Estados de lista | FE-014-T02 y pruebas de estados UI | PASS |
| AC-10 Reversión | Upgrade/downgrade de `a014` | PASS |
| AC-11 Aislamiento | Filtros por owner/clínica, C9 y pruebas de repo | PASS |

## Checklist de arquitectura

- [x] Routers delgados: HTTP, autenticación y mapeo de schemas únicamente.
- [x] Casos de uso y reglas de transición en `application`.
- [x] Dominio sin dependencias de FastAPI, SQLAlchemy ni proveedores.
- [x] Repositorio detrás de su contrato; ORM aislado en `infrastructure`.
- [x] Schemas Pydantic separados de los modelos ORM.
- [x] Autorización y aislamiento aplicados en backend.
- [x] Migración reversible y descubrible por `Base.metadata`.
- [x] Capas frontend (`app`, `features`, `entities`, `shared`) sin acceso HTTP ad hoc.
- [x] Evidencia de pruebas y diff trazada a AC-014.

## Hallazgos y riesgos aceptados

No hay hallazgos `BLOCKER`, `CRITICAL` ni `MAJOR`. Se aceptan como menores:

1. `status` tiene default de servidor en la migración y el repositorio fija
   explícitamente `iniciado`, una decisión compatible con SQLite y PostgreSQL.
2. `description` es nullable, conforme al contrato actual.
3. El warning de relación SQLAlchemy indicado arriba es de mantenibilidad y no
   afecta el comportamiento del slice.

## Estado de ejecución

**APPROVED** — la arquitectura, el modelo SQL, la migración y la trazabilidad
contra AC-014 están verificadas.

## Siguiente paso recomendado

Ejecutar `/security-review BE-014` con el agente `invet-security-reviewer` y
mantener las mismas reglas de PowerShell (directorio de trabajo explícito y
comandos separados). Después continuar con `/run-ui-checks BE-014`,
`/run-checks BE-014`, `/update-docs BE-014` y `/final-gate BE-014`.

- Decision: APPROVED
