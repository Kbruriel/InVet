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


def test_plan_task_rejects_fe_and_qa_arguments() -> None:
    command = (REPO_ROOT / ".opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "Acepta exclusivamente argumentos `BE-00X`",
        "Si recibe `FE-00X`",
        "/implement-frontend-task FE-00X",
        "Si recibe `QA-00X`",
        "/qa-task QA-00X",
        "no debe remapear silenciosamente",
    ]

    for phrase in required_phrases:
        assert phrase in command


def test_plan_task_never_implements_code() -> None:
    command = (REPO_ROOT / ".opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )
    agent = (REPO_ROOT / ".opencode/agents/invet-product-planner.md").read_text(
        encoding="utf-8"
    )

    assert "/plan-task` nunca implementa backend, frontend ni QA" in command
    assert "No implementas codigo backend ni frontend" in agent
