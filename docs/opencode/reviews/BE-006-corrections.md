# Correcciones slice BE-006 / FE-006 / QA-006

## Finding 006-001 (BLOCKER) — Duplicate SQLAlchemy table definitions

### Problema
Dos pares de archivos en `backend/app/infrastructure/database/models/` definían las mismas tablas SQLAlchemy:
- `service.py` y `service_model.py` ambos con `__tablename__ = "services"`
- `veterinarian.py` y `veterinarian_model.py` ambos con `__tablename__ = "veterinarians"`

Esto causaba `InvalidRequestError: Table 'services' is already defined for this MetaData instance.` al importar los modelos en `conftest.py`.

### Corrección
- Eliminé `backend/app/infrastructure/database/models/service.py` (duplicado)
- Eliminé `backend/app/infrastructure/database/models/veterinarian.py` (duplicado)
- Los archivos canónicos (`service_model.py` y `veterinarian_model.py`) son los importados por `__init__.py` y se conservaron intactos

### Verificación
```
[PASS] BE-006/FE-006/QA-006 stage=secure-persistence
```

## Finding 006-002 (MAJOR) — TypeScript type errors in test mocks

### Problema
Los hooks (`useServices`, `useVeterinarians`, `useInternalUsers`) retornan `{ items, total, page, size, loading, error, submitting, setPage, create, update, deactivate, fetchOne }` pero los mocks en los tests solo incluían las primeras propiedades sin `create`, `update`, `fetchOne`.

### Corrección
Actualizados 3 archivos de test con las propiedades faltantes:
- `frontend/src/features/slice-006/components/service-list.test.tsx` — 3 mocks actualizados
- `frontend/src/features/slice-006/components/veterinarian-list.test.tsx` — 2 mocks actualizados
- `frontend/src/features/slice-006/components/internal-user-list.test.tsx` — 2 mocks actualizados

Cada mock ahora incluye:
```typescript
create: jest.fn().mockResolvedValue({}),
update: jest.fn().mockResolvedValue({}),
fetchOne: jest.fn().mockResolvedValue({}),
```

### Verificación
```
Test Suites: 6 passed, 6 total
Tests:       17 passed, 17 total
```

## Estado de los findings

| Finding | Estado | Evidencia |
|---------|--------|----------|
| FINDING-006-001 | READY_FOR_REVALIDATION | Antes: OPEN; `service.py` y `veterinarian.py` eliminados; modelos canónicos conservados |
| FINDING-006-002 | READY_FOR_REVALIDATION | Antes: OPEN; mocks de tests actualizados con `create`, `update` y `fetchOne` |
