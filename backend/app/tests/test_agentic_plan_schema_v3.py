from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / "backend/scripts/validate_slice_plan.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_slice_plan", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _minimal_schema_v3_plan(
    objective: str = "Definir contrato backend verificable.",
) -> str:
    backend_objective = objective
    return f"""---
schema_version: 3
slice: "999"
canonical_plan: BE-999
status: PLANNED
encoding: UTF-8
---

# BE-999 Plan - Contrato de prueba

## Objetivo del slice
## Alcance MVP
## Fuera de alcance
## Suposiciones
## Revision de gaps
## Entidades y reglas de negocio
## Fuentes y artefactos de contexto
## Matriz de trazabilidad
## Endpoints esperados
## Contrato de implementacion frontend
### Rutas y acceso
### Flujos y estados UX
### Contratos API por accion
### Formularios y validacion
### Arquitectura de componentes
### Responsive y accesibilidad
### Estrategia de pruebas frontend
## Contrato de ejecucion Docker y pruebas
## Plan de reportes y findings
## Pruebas QA
## Riesgos de seguridad/IDOR/BOLA
## Politica UTF-8
## Checklist tecnico
## Checklist de tareas

### Backend

- [ ] BE-999-T01 - Definir contrato
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-999-01
  Objetivo: {backend_objective}
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: tarea backend
  Contratos usados: endpoint principal
  Entregables: contrato backend
  Criterios de aceptacion: contrato documentado.
  Validacion: inspeccion del plan
  Resultado esperado: contrato listo
  Evidencia: pending
  Paralelismo[P]: No

### Frontend

- [ ] FE-999-T01 - Implementar cliente
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-999-01
  Objetivo: Implementar cliente tipado.
  Responsabilidad unica: Si
  Depende de: BE-999-T01
  Contexto necesario: contrato frontend
  Contratos usados: endpoint principal
  Entregables: cliente API
  Criterios de aceptacion: cliente tipado.
  Validacion: npm run typecheck
  Resultado esperado: cliente listo
  Evidencia: pending
  Paralelismo[P]: No

### QA

- [ ] QA-999-T01 - Validar criterio
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-999-01
  Objetivo: Validar criterio principal.
  Responsabilidad unica: Si
  Depende de: BE-999-T01, FE-999-T01
  Contexto necesario: plan canonico
  Contratos usados: matriz trazabilidad
  Entregables: reporte QA
  Criterios de aceptacion: criterio en PASS.
  Validacion: reporte QA
  Resultado esperado: decision trazable
  Evidencia: pending
  Paralelismo[P]: No

## Definition of Done
"""


def test_schema_v3_plan_contract_accepts_atomic_tasks() -> None:
    validator = _load_validator()
    slice_ids = validator.normalize_slice_id("BE-999")

    errors = validator.validate_plan_text(_minimal_schema_v3_plan(), slice_ids)

    assert errors == []


def test_schema_v3_plan_contract_rejects_composite_objectives_and_mojibake() -> None:
    validator = _load_validator()
    slice_ids = validator.normalize_slice_id("BE-999")
    plan = _minimal_schema_v3_plan(
        "Definir contrato backend y crear pruebas Ã©rroneas."
    )

    errors = validator.validate_plan_text(plan, slice_ids)

    assert any("Objetivo parece compuesto" in error for error in errors)
    assert any("mojibake" in error for error in errors)


def test_schema_v3_contracts_are_synced_with_payload() -> None:
    pairs = [
        (
            REPO_ROOT / "backend/scripts/validate_slice_plan.py",
            REPO_ROOT / "payload/backend/scripts/validate_slice_plan.py",
        ),
        (
            REPO_ROOT / "docs/opencode/templates/slice_plan_template.md",
            REPO_ROOT / "payload/docs/opencode/templates/slice_plan_template.md",
        ),
        (
            REPO_ROOT / "docs/opencode/references/spec_kit_reference_improvements.md",
            REPO_ROOT
            / "payload/docs/opencode/references/spec_kit_reference_improvements.md",
        ),
    ]

    for primary, payload in pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )
