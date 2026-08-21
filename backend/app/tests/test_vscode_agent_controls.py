from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_vscode_runtime_limits_agent_requests() -> None:
    settings = json.loads(
        (REPO_ROOT / ".vscode/settings.json").read_text(encoding="utf-8")
    )

    assert settings["chat.agent.maxRequests"] == 50


def test_vscode_orchestrator_cannot_delegate() -> None:
    orchestrator = (
        REPO_ROOT / ".github/agents/invet-orchestrator.agent.md"
    ).read_text(encoding="utf-8")

    assert "'agent'" not in orchestrator
    assert "\nagents:" not in orchestrator
    assert "\nhandoffs:" not in orchestrator
    assert "Never call a subagent" in orchestrator


def test_vscode_contract_uses_compact_context_and_mandatory_final_gate() -> None:
    instructions = (REPO_ROOT / ".github/copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    orchestrator = (
        REPO_ROOT / ".github/agents/invet-orchestrator.agent.md"
    ).read_text(encoding="utf-8")

    assert "48,000 context tokens" in instructions
    assert "matching verified manifest" in instructions
    assert "Save a checkpoint after every task" in instructions
    assert "Run final gate" in instructions
    assert "The final gate is mandatory" in orchestrator


def test_vscode_profiles_are_specialized_and_payload_is_synced() -> None:
    agents = sorted((REPO_ROOT / ".github/agents").glob("*.agent.md"))
    prompts = sorted((REPO_ROOT / ".github/prompts").glob("*.prompt.md"))

    assert len(agents) == 14
    for source in agents + prompts + [REPO_ROOT / ".github/copilot-instructions.md"]:
        relative = source.relative_to(REPO_ROOT / ".github")
        payload = REPO_ROOT / "payload/.github" / relative
        assert payload.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")

    settings = REPO_ROOT / ".vscode/settings.json"
    payload_settings = REPO_ROOT / "payload/.vscode/settings.json"
    assert settings.read_text(encoding="utf-8") == payload_settings.read_text(
        encoding="utf-8"
    )


def test_removed_generic_profiles_do_not_return() -> None:
    removed = {
        "invet-planner.agent.md",
        "invet-implementer.agent.md",
        "invet-qa-reviewer.agent.md",
        "invet-findings-resolver.agent.md",
    }

    assert not removed.intersection(
        path.name for path in (REPO_ROOT / ".github/agents").glob("*.agent.md")
    )
