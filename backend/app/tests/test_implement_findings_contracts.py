from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_implement_findings_primary_and_payload_commands_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/commands/implement-findings.md").read_text(
        encoding="utf-8"
    )
    payload = (
        REPO_ROOT / "payload/.opencode/commands/implement-findings.md"
    ).read_text(encoding="utf-8")

    assert primary == payload


def test_implement_findings_primary_and_payload_agents_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/agents/invet-findings-implementer.md").read_text(
        encoding="utf-8"
    )
    payload = (
        REPO_ROOT / "payload/.opencode/agents/invet-findings-implementer.md"
    ).read_text(encoding="utf-8")

    assert primary == payload


def test_implement_findings_accepts_fe_input() -> None:
    command = (REPO_ROOT / ".opencode/commands/implement-findings.md").read_text(
        encoding="utf-8"
    )
    agent = (REPO_ROOT / ".opencode/agents/invet-findings-implementer.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "Acepta un indice `BE-00X`, `FE-00X` o la ruta de un archivo de hallazgos.",
        "Si recibe `FE-00X`",
        "BE-00X` equivalente",
        "mismo slice vertical",
    ]

    for phrase in required_phrases:
        assert phrase in command

    assert "Aceptar el slice tanto desde `BE-00X` como desde `FE-00X`" in agent
