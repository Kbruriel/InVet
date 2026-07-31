from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_fe001_task_primary_and_payload_are_in_sync() -> None:
    primary = (REPO_ROOT / "docs/opencode/tasks/frontend/FE-001.md").read_text(
        encoding="utf-8"
    )
    payload = (REPO_ROOT / "payload/docs/opencode/tasks/frontend/FE-001.md").read_text(
        encoding="utf-8"
    )

    assert primary == payload


def test_be001_plan_primary_and_payload_are_in_sync() -> None:
    primary = (REPO_ROOT / "docs/opencode/plans/BE-001-plan.md").read_text(
        encoding="utf-8"
    )
    payload = (REPO_ROOT / "payload/docs/opencode/plans/BE-001-plan.md").read_text(
        encoding="utf-8"
    )

    assert primary == payload


def test_implement_frontend_task_bootstraps_fe001_workspace() -> None:
    command = (REPO_ROOT / ".opencode/commands/implement-frontend-task.md").read_text(
        encoding="utf-8"
    )
    agent = (REPO_ROOT / ".opencode/agents/invet-frontend-implementer.md").read_text(
        encoding="utf-8"
    )

    assert "Si falta `frontend/package.json`" in command
    assert "scripts `lint`, `typecheck`, `test`, `build`" in command
    assert "docs/opencode/references/frontend_visual_alignment.md" in agent
    assert "DESIGN.md" not in agent


def test_frontend_command_requires_valid_plan_and_unit_tests() -> None:
    command = (REPO_ROOT / ".opencode/commands/implement-frontend-task.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "validate_slice_plan.py FE-00X --stage frontend",
        "Contrato de implementacion frontend",
        "Capa: frontend",
        "Depende de",
        "pruebas unitarias o de componente",
        "Evidencia: pending",
    ]

    for phrase in required_phrases:
        assert phrase in command


def test_fe001_and_plan_require_executable_frontend() -> None:
    task = (REPO_ROOT / "docs/opencode/tasks/frontend/FE-001.md").read_text(
        encoding="utf-8"
    )
    plan = (REPO_ROOT / "docs/opencode/plans/BE-001-plan.md").read_text(
        encoding="utf-8"
    )

    assert (
        "Existe `frontend/package.json` con scripts `lint`, `typecheck`, `test` y `build`."
        in task
    )
    assert "Workspace frontend ejecutable con `package.json`, scripts y `src/`." in plan
    assert "Definicion documental" not in plan
