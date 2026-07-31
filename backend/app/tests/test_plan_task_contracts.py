from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_plan_task_primary_and_payload_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )
    payload = (REPO_ROOT / "payload/.opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )

    assert primary == payload


def test_plan_task_accepts_and_normalizes_be_fe_qa_arguments() -> None:
    command = (REPO_ROOT / ".opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )
    agent = (REPO_ROOT / ".opencode/agents/invet-product-planner.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "`BE-00X`, `FE-00X` o `QA-00X`",
        "normaliza de forma explicita",
        "unico plan compartido",
        "slice_plan_template.md",
        "Contrato de implementacion frontend",
        "validate_slice_plan.py",
    ]

    for phrase in required_phrases:
        assert phrase in command

    assert "Aceptar `BE-00X`, `FE-00X` o `QA-00X`" in agent
    assert "Contrato frontend obligatorio" in agent


def test_plan_task_agent_and_template_are_in_sync_with_payload() -> None:
    pairs = [
        (
            REPO_ROOT / ".opencode/agents/invet-product-planner.md",
            REPO_ROOT / "payload/.opencode/agents/invet-product-planner.md",
        ),
        (
            REPO_ROOT / "docs/opencode/templates/slice_plan_template.md",
            REPO_ROOT / "payload/docs/opencode/templates/slice_plan_template.md",
        ),
        (
            REPO_ROOT / "backend/scripts/validate_slice_plan.py",
            REPO_ROOT / "payload/backend/scripts/validate_slice_plan.py",
        ),
    ]

    for primary, payload in pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )


def test_plan_task_never_implements_code() -> None:
    command = (REPO_ROOT / ".opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )
    agent = (REPO_ROOT / ".opencode/agents/invet-product-planner.md").read_text(
        encoding="utf-8"
    )

    assert "/plan-task` nunca implementa backend, frontend ni QA" in command
    assert "No implementas backend, frontend ni QA" in agent


def test_installer_distributes_orchestrator_command_and_validator() -> None:
    installer = (REPO_ROOT / "install-invet-opencode-agents.ps1").read_text(
        encoding="utf-8"
    )

    assert "payload/backend/scripts" in installer
    assert "backend/scripts" in installer
    assert "/execute-slice" in installer
