from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_COMMAND = "docker compose up -d --build --force-recreate db backend frontend"


def test_closure_hook_contracts_are_in_sync_with_payload() -> None:
    file_pairs = [
        (
            REPO_ROOT / ".opencode/commands/implement-backend-task.md",
            REPO_ROOT / "payload/.opencode/commands/implement-backend-task.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/implement-frontend-task.md",
            REPO_ROOT / "payload/.opencode/commands/implement-frontend-task.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/qa-task.md",
            REPO_ROOT / "payload/.opencode/commands/qa-task.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/implement-findings.md",
            REPO_ROOT / "payload/.opencode/commands/implement-findings.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/run-checks.md",
            REPO_ROOT / "payload/.opencode/commands/run-checks.md",
        ),
        (
            REPO_ROOT / "docs/opencode/03_task_prompt_contracts.md",
            REPO_ROOT / "payload/docs/opencode/03_task_prompt_contracts.md",
        ),
        (
            REPO_ROOT / "docs/opencode/05_done_gates_by_command.md",
            REPO_ROOT / "payload/docs/opencode/05_done_gates_by_command.md",
        ),
    ]

    for primary, payload in file_pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )


def test_closure_hook_phrase_is_present_in_contracts_and_wrapper() -> None:
    files = [
        REPO_ROOT / ".opencode/commands/implement-backend-task.md",
        REPO_ROOT / ".opencode/commands/implement-frontend-task.md",
        REPO_ROOT / ".opencode/commands/qa-task.md",
        REPO_ROOT / ".opencode/commands/implement-findings.md",
        REPO_ROOT / ".opencode/commands/run-checks.md",
        REPO_ROOT / "run-checks.ps1",
    ]

    for path in files:
        text = path.read_text(encoding="utf-8")
        assert HOOK_COMMAND in text

    gates = REPO_ROOT / "docs/opencode/05_done_gates_by_command.md"
    gates_text = gates.read_text(encoding="utf-8")
    assert "El hook de Docker Compose de cierre" in gates_text
