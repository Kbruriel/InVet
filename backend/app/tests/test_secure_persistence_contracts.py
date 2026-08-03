from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_secure_persistence_stage_is_wired_into_the_agentic_flow() -> None:
    validator = (REPO_ROOT / "backend/scripts/validate_slice_plan.py").read_text(
        encoding="utf-8"
    )
    orchestrator = (REPO_ROOT / ".opencode/agents/invet-orchestrator.md").read_text(
        encoding="utf-8"
    )
    execute_slice = (REPO_ROOT / ".opencode/commands/execute-slice.md").read_text(
        encoding="utf-8"
    )
    backend_agent = (
        REPO_ROOT / ".opencode/agents/invet-backend-implementer.md"
    ).read_text(encoding="utf-8")
    backend_command = (
        REPO_ROOT / ".opencode/commands/implement-backend-task.md"
    ).read_text(encoding="utf-8")

    assert '"secure-persistence"' in validator
    assert "Gate de Persistencia segura" in orchestrator
    assert "--stage secure-persistence" in execute_slice
    assert "--stage secure-persistence" in backend_agent
    assert "--stage secure-persistence" in backend_command


def test_secure_persistence_contracts_are_in_sync_with_payload() -> None:
    pairs = [
        (
            REPO_ROOT / "backend/scripts/validate_slice_plan.py",
            REPO_ROOT / "payload/backend/scripts/validate_slice_plan.py",
        ),
        (
            REPO_ROOT / ".opencode/agents/invet-orchestrator.md",
            REPO_ROOT / "payload/.opencode/agents/invet-orchestrator.md",
        ),
        (
            REPO_ROOT / ".opencode/agents/invet-backend-implementer.md",
            REPO_ROOT / "payload/.opencode/agents/invet-backend-implementer.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/execute-slice.md",
            REPO_ROOT / "payload/.opencode/commands/execute-slice.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/implement-backend-task.md",
            REPO_ROOT / "payload/.opencode/commands/implement-backend-task.md",
        ),
    ]

    for primary, payload in pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )
