from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

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
    slice_id: str = "999",
) -> str:
    backend_plan = f"BE-{slice_id}"
    frontend_plan = f"FE-{slice_id}"
    qa_plan = f"QA-{slice_id}"
    return f"""---
schema_version: 3
slice: "{slice_id}"
canonical_plan: {backend_plan}
status: PLANNED
encoding: UTF-8
---

# {backend_plan} Plan - Contrato de prueba

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

- [ ] {backend_plan}-T01 - Definir contrato
  Capa: backend
  Tipo: contrato
  Historia o criterio: AC-{slice_id}-01
  Objetivo: {objective}
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

- [ ] {frontend_plan}-T01 - Implementar cliente
  Capa: frontend
  Tipo: cliente api
  Historia o criterio: AC-{slice_id}-01
  Objetivo: Implementar cliente tipado.
  Responsabilidad unica: Si
  Depende de: {backend_plan}-T01
  Contexto necesario: contrato frontend
  Contratos usados: endpoint principal
  Entregables: cliente API
  Criterios de aceptacion: cliente tipado.
  Validacion: npm run typecheck
  Resultado esperado: cliente listo
  Evidencia: pending
  Paralelismo[P]: No

### QA

- [ ] {qa_plan}-T01 - Validar criterio
  Capa: qa
  Tipo: qa
  Historia o criterio: AC-{slice_id}-01
  Objetivo: Validar criterio principal.
  Responsabilidad unica: Si
  Depende de: {backend_plan}-T01, {frontend_plan}-T01
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


def _write_plan(repo_root: Path, slice_id: str, plan_text: str) -> None:
    plan_path = repo_root / "docs" / "opencode" / "plans" / f"BE-{slice_id}-plan.md"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan_text, encoding="utf-8")


def _write_qa_result(
    repo_root: Path, slice_id: str, decision: str = "APPROVED"
) -> None:
    results_path = repo_root / "docs" / "opencode" / "qa" / f"QA-{slice_id}-results.md"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(f"- Decision: {decision}\n", encoding="utf-8")


def _write_carryover_registry(
    repo_root: Path,
    slice_id: str,
    status: str,
    closure_evidence: str = "pending",
) -> None:
    registry_path = (
        repo_root / "docs" / "opencode" / "carryovers" / f"BE-{slice_id}-carryovers.md"
    )
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        f"""# BE-{slice_id} Carryovers

| source_plan | source_task | destination_plan | destination_task | reason_postponed | status | owner | updated_at | closure_evidence | source_reference | destination_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BE-998-plan.md | BE-998-T03 | BE-{slice_id}-plan.md | BE-{slice_id}-T04 | Dependencia externa | {status} | planner | 2026-08-15 | {closure_evidence} | docs/opencode/plans/BE-998-plan.md#L10 | docs/opencode/plans/BE-{slice_id}-plan.md#L20 |
""",
        encoding="utf-8",
    )


def test_schema_v3_plan_contract_accepts_atomic_tasks() -> None:
    validator = _load_validator()
    slice_ids = validator.normalize_slice_id("BE-999")

    errors = validator.validate_plan_text(_minimal_schema_v3_plan(), slice_ids)

    assert errors == []


def test_schema_v3_composite_markers_outside_objective_are_allowed() -> None:
    validator = _load_validator()
    slice_ids = validator.normalize_slice_id("BE-999")
    plan = _minimal_schema_v3_plan().replace(
        "Contexto necesario: tarea backend",
        "Contexto necesario: `docs/opencode/tasks/backend/BE-999.md`; guia y contrato + pruebas",
    )

    errors = validator.validate_plan_text(plan, slice_ids)

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


def test_schema_v3_plan_contract_rejects_noncanonical_task_rows() -> None:
    validator = _load_validator()
    slice_ids = validator.normalize_slice_id("BE-999")
    plan = _minimal_schema_v3_plan().replace(
        "- [ ] BE-999-T01 - Definir contrato",
        "- [ ] BE-999-T01: Definir contrato",
    )

    errors = validator.validate_plan_text(plan, slice_ids)

    assert any("formato no canonico" in error for error in errors)


@pytest.mark.parametrize("status", ["OPEN", "TRANSFERRED"])
def test_schema_v3_plan_contract_blocks_open_carryovers_at_qa(
    tmp_path: Path,
    status: str,
) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    _write_plan(tmp_path, slice_id, _minimal_schema_v3_plan(slice_id=slice_id))
    _write_qa_result(tmp_path, slice_id)
    _write_carryover_registry(tmp_path, slice_id, status=status)

    errors = validator.validate_stage(tmp_path, slice_ids, "qa")

    assert any("carryover" in error.lower() and status in error for error in errors)


def test_schema_v3_plan_contract_accepts_closed_carryovers_at_qa(
    tmp_path: Path,
) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    _write_plan(tmp_path, slice_id, _minimal_schema_v3_plan(slice_id=slice_id))
    _write_qa_result(tmp_path, slice_id)
    _write_carryover_registry(
        tmp_path,
        slice_id,
        status="CLOSED",
        closure_evidence="docs/opencode/plans/BE-998-plan.md#L10",
    )

    errors = validator.validate_stage(tmp_path, slice_ids, "qa")

    assert errors == []


def test_qa_preflight_allows_qa_tasks_to_remain_open(tmp_path: Path) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    _write_plan(tmp_path, slice_id, _minimal_schema_v3_plan(slice_id=slice_id))

    errors = validator.validate_stage(tmp_path, slice_ids, "qa")

    assert errors == []


@pytest.mark.parametrize("stage", ["review", "checks", "docs"])
def test_closure_stages_block_open_applicable_tasks(
    tmp_path: Path,
    stage: str,
) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    _write_plan(tmp_path, slice_id, _minimal_schema_v3_plan(slice_id=slice_id))
    _write_qa_result(tmp_path, slice_id)

    errors = validator.validate_stage(tmp_path, slice_ids, stage)

    assert any("BE-001-T01 sigue abierta" in error for error in errors)
    assert any("FE-001-T01 sigue abierta" in error for error in errors)
    assert any("QA-001-T01 sigue abierta" in error for error in errors)


def test_closure_gate_accepts_cancelled_tasks_with_evidence(tmp_path: Path) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    plan = _minimal_schema_v3_plan(slice_id=slice_id).replace(
        "  Evidencia: pending\n  Paralelismo[P]: No",
        "  Evidencia: docs/opencode/decisions/BE-001-cancellation.md\n"
        "  Estado: CANCELLED\n"
        "  Paralelismo[P]: No",
    )
    _write_plan(tmp_path, slice_id, plan)

    errors = validator.validate_task_closure_gate(tmp_path, slice_ids)

    assert errors == []


def test_closure_gate_rejects_cancelled_tasks_without_evidence(tmp_path: Path) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    plan = _minimal_schema_v3_plan(slice_id=slice_id).replace(
        "  Paralelismo[P]: No",
        "  Estado: CANCELLED\n  Paralelismo[P]: No",
    )
    _write_plan(tmp_path, slice_id, plan)

    errors = validator.validate_task_closure_gate(tmp_path, slice_ids)

    assert any("CANCELLED sin evidencia verificable" in error for error in errors)


def test_schema_v3_plan_contract_requires_carryover_registry_when_transfers_are_mentioned(
    tmp_path: Path,
) -> None:
    validator = _load_validator()
    slice_id = "001"
    slice_ids = validator.normalize_slice_id(f"BE-{slice_id}")
    plan = (
        _minimal_schema_v3_plan(slice_id=slice_id)
        + "\n## Revision de gaps\n- Una tarea heredada de otro slice quedo postergada y debe registrarse.\n"
    )
    _write_plan(tmp_path, slice_id, plan)
    _write_qa_result(tmp_path, slice_id)

    errors = validator.validate_stage(tmp_path, slice_ids, "qa")

    assert any("registro canonico" in error.lower() for error in errors)


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
        (
            REPO_ROOT / "docs/opencode/references/carryovers_governance.md",
            REPO_ROOT / "payload/docs/opencode/references/carryovers_governance.md",
        ),
        (
            REPO_ROOT / "docs/opencode/templates/carryovers_registry_template.md",
            REPO_ROOT
            / "payload/docs/opencode/templates/carryovers_registry_template.md",
        ),
    ]

    for primary, payload in pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )
