from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "backend/scripts/manage_slice_task.py"


def _load_controls():
    scripts_dir = str(SCRIPT_PATH.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("manage_slice_task", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_plan(root: Path) -> None:
    path = root / "docs/opencode/plans/BE-001-plan.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        """---
schema_version: 3
slice: "001"
canonical_plan: BE-001
---

## Checklist de tareas

- [ ] BE-001-T01 - Agregar router
  Capa: backend
  Tipo: api
  Historia o criterio: AC-001-01
  Objetivo: Agregar router.
  Responsabilidad unica: Si
  Depende de: Ninguna
  Contexto necesario: router existente
  Contratos usados: AC-001-01
  Entregables: `backend/app/api/v1/routers/new.py`, registro en main router.
  Criterios de aceptacion: Router registrado.
  Validacion: pytest
  Resultado esperado: Endpoint activo.
  Evidencia: pending
  Paralelismo[P]: No
""",
        encoding="utf-8",
    )
    source = root / "docs/opencode/tasks/backend/BE-001.md"
    source.parent.mkdir(parents=True)
    source.write_text("# BE-001\n", encoding="utf-8")


def _write_all_sources(root: Path) -> None:
    sources = {
        "docs/opencode/tasks/frontend/FE-001.md": "# FE-001\n",
        "docs/opencode/tasks/qa/QA-001.md": "# QA-001\n",
        "docs/opencode/tasks/ui-automation/UIA-001.md": "# UIA-001\n",
        "docs/opencode/tasks/api-automation/APIA-001.md": "# APIA-001\n",
    }
    for relative, content in sources.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_manifest_is_compact_and_allowlist_comes_from_deliverables(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)

    [manifest] = controls.generate_manifests(tmp_path, "BE-001", "backend")
    text = manifest.read_text(encoding="utf-8")

    assert len(text.splitlines()) <= 150
    assert "backend/app/api/v1/routers/new.py" in text
    assert "backend/app/api/v1/router.py" in text
    assert "iniciar subagentes" in text


def test_manifest_verification_detects_missing_and_stale_sources(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)
    _write_all_sources(tmp_path)
    controls.generate_manifests(tmp_path, "FE-001", "all")

    assert controls.verify_manifests(tmp_path, "QA-001", "all") == []

    source = tmp_path / "docs/opencode/tasks/frontend/FE-001.md"
    source.write_text("# FE-001 actualizado\n", encoding="utf-8")
    errors = controls.verify_manifests(tmp_path, "BE-001", "all")
    assert any("stale/invalido" in error for error in errors)


def test_automation_manifests_require_docker_without_host_fallback(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)
    _write_all_sources(tmp_path)

    ui_manifest = controls.generate_manifests(
        tmp_path, "BE-001", "ui-automation"
    )[0].read_text(encoding="utf-8")
    api_manifest = controls.generate_manifests(
        tmp_path, "BE-001", "api-automation"
    )[0].read_text(encoding="utf-8")

    for manifest in (ui_manifest, api_manifest):
        assert "Entorno Docker obligatorio" in manifest
        assert "no existe fallback host" in manifest
    assert "PLAYWRIGHT_START_FRONTEND=false" in ui_manifest
    assert "backend publicado por Docker" in api_manifest


def test_automation_phase_uses_its_sidecar_allowlist_and_checkpoint(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)
    _write_all_sources(tmp_path)
    target = tmp_path / "InVet_UI_Automation/tests/e2e/slice-001.spec.ts"
    target.parent.mkdir(parents=True)

    runtime = controls.start_task(tmp_path, "BE-001", "UIA-001")
    target.write_text("// UIA-001\n", encoding="utf-8")
    checkpoint, errors = controls.finish_task(
        tmp_path, "UIA-001", "npm run test:e2e: pass", ""
    )

    assert runtime["layer"] == "ui-automation"
    assert "InVet_UI_Automation/tests/e2e/**" in runtime["allowed_files"]
    assert errors == []
    assert checkpoint["tasks"]["UIA-001"]["state"] == "completed"


def test_finish_blocks_out_of_scope_changes_and_router_removal(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)
    router = tmp_path / "backend/app/api/v1/router.py"
    router.parent.mkdir(parents=True)
    router.write_text(
        "router.include_router(existing_router)\n", encoding="utf-8"
    )
    unrelated = tmp_path / "backend/app/core/config.py"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("VALUE = 1\n", encoding="utf-8")
    controls.start_task(tmp_path, "BE-001", "BE-001-T01")

    router.write_text("router.include_router(new_router)\n", encoding="utf-8")
    unrelated.write_text("VALUE = 2\n", encoding="utf-8")
    _, errors = controls.finish_task(
        tmp_path, "BE-001-T01", "pytest: pass", ""
    )

    assert any("fuera de Entregables" in error for error in errors)
    assert any("Invariantes de router" in error for error in errors)


def test_finish_requires_justification_for_removed_lines(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)
    target = tmp_path / "backend/app/api/v1/routers/new.py"
    target.parent.mkdir(parents=True)
    target.write_text("KEEP = 1\nREMOVE = 2\n", encoding="utf-8")
    controls.start_task(tmp_path, "BE-001", "BE-001-T01")
    target.write_text("KEEP = 1\n", encoding="utf-8")

    _, errors = controls.finish_task(
        tmp_path, "BE-001-T01", "pytest: pass", ""
    )
    assert any("Lineas existentes eliminadas" in error for error in errors)

    controls.start_task(tmp_path, "BE-001", "BE-001-T01")
    target.write_text("KEEP = 3\n", encoding="utf-8")
    _, errors = controls.finish_task(
        tmp_path,
        "BE-001-T01",
        "pytest: pass",
        "Cambio de contrato aprobado en el plan.",
    )
    assert errors == []


def test_finish_does_not_complete_a_failed_or_blocked_task(tmp_path: Path) -> None:
    controls = _load_controls()
    _write_plan(tmp_path)

    controls.start_task(tmp_path, "BE-001", "BE-001-T01")
    failed, errors = controls.finish_task(
        tmp_path, "BE-001-T01", "pytest: 1 failed", "", "failed"
    )
    assert failed["tasks"]["BE-001-T01"]["state"] == "failed"
    assert failed["tasks"]["BE-001-T01"]["outcome"] == "failed"
    assert any("pruebas" in error for error in errors)

    controls.start_task(tmp_path, "BE-001", "BE-001-T01")
    blocked, errors = controls.finish_task(
        tmp_path, "BE-001-T01", "Docker no disponible", "", "blocked"
    )
    assert blocked["tasks"]["BE-001-T01"]["state"] == "blocked"
    assert blocked["tasks"]["BE-001-T01"]["outcome"] == "blocked"
    assert any("bloqueada" in error for error in errors)
