from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_review_slice_primary_and_payload_commands_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/commands/review-slice.md").read_text(
        encoding="utf-8"
    )
    payload = (REPO_ROOT / "payload/.opencode/commands/review-slice.md").read_text(
        encoding="utf-8"
    )

    assert primary == payload


def test_review_slice_primary_and_payload_agents_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/agents/invet-slice-reviewer.md").read_text(
        encoding="utf-8"
    )
    payload = (
        REPO_ROOT / "payload/.opencode/agents/invet-slice-reviewer.md"
    ).read_text(encoding="utf-8")

    assert primary == payload


def test_review_slice_accepts_fe_input_without_silent_remap() -> None:
    command = (REPO_ROOT / ".opencode/commands/review-slice.md").read_text(
        encoding="utf-8"
    )
    agent = (REPO_ROOT / ".opencode/agents/invet-slice-reviewer.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "Acepta argumentos `BE-00X` o `FE-00X`.",
        "Si recibe `FE-00X`",
        "revisa el mismo slice vertical completo",
        "Si recibe `QA-00X`",
        "/qa-task QA-00X",
        "docs/opencode/plans/BE-00X-plan.md",
    ]

    for phrase in required_phrases:
        assert phrase in command

    assert "Aceptar el slice tanto desde `BE-00X` como desde `FE-00X`" in agent
    assert "redirigir a `/qa-task QA-00X`" in agent
