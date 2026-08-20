from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_secure_persistence_is_internal_to_the_backend_command() -> None:
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
    assert "--stage secure-persistence" not in orchestrator
    assert "--stage secure-persistence" not in execute_slice
    assert "validacion de persistencia" in orchestrator
    assert "validacion interna de persistencia" in execute_slice
    assert "--stage secure-persistence" in backend_agent
    assert "--stage secure-persistence" in backend_command


def test_public_flows_do_not_expose_internal_secure_persistence_script() -> None:
    public_flows = [
        REPO_ROOT / ".github/copilot-instructions.md",
        REPO_ROOT / ".github/agents/invet-orchestrator.agent.md",
        REPO_ROOT / ".github/prompts/execute-slice.prompt.md",
        REPO_ROOT / "docs/opencode/README.md",
        REPO_ROOT / "docs/opencode/13_agents_architecture_and_gate_flow.md",
        REPO_ROOT / "docs/opencode/14_github_copilot_agentic_flow.md",
        REPO_ROOT / "docs/opencode/15_operational_manifests_flow.md",
    ]

    for path in public_flows:
        assert "--stage secure-persistence" not in path.read_text(encoding="utf-8")


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
