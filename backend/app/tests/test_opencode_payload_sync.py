from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OPERATIONAL_DOCS = (
    "00_installation_manifest.md",
    "01_command_runbook.md",
    "03_task_prompt_contracts.md",
    "04_agent_contracts.md",
    "05_done_gates_by_command.md",
    "11_chatgpt_project_context.md",
    "12_troubleshooting_skills_vs_agents.md",
    "README.md",
)


def _operational_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    mappings = [
        (REPO_ROOT / ".opencode/agents", REPO_ROOT / "payload/.opencode/agents"),
        (
            REPO_ROOT / ".opencode/commands",
            REPO_ROOT / "payload/.opencode/commands",
        ),
        (
            REPO_ROOT / "docs/opencode/templates",
            REPO_ROOT / "payload/docs/opencode/templates",
        ),
    ]
    for primary_root, payload_root in mappings:
        for primary in primary_root.glob("*.md"):
            pairs.append((primary, payload_root / primary.name))

    for name in OPERATIONAL_DOCS:
        pairs.append(
            (
                REPO_ROOT / "docs/opencode" / name,
                REPO_ROOT / "payload/docs/opencode" / name,
            )
        )

    pairs.append(
        (
            REPO_ROOT / "backend/scripts/validate_slice_plan.py",
            REPO_ROOT / "payload/backend/scripts/validate_slice_plan.py",
        )
    )
    return pairs


@pytest.mark.parametrize(
    ("primary", "payload"),
    _operational_pairs(),
    ids=lambda path: path.name,
)
def test_operational_contracts_are_in_sync(
    primary: Path,
    payload: Path,
) -> None:
    assert payload.exists(), f"Falta espejo distribuible para {primary}"
    assert primary.read_text(encoding="utf-8") == payload.read_text(encoding="utf-8")
