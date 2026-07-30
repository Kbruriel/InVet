from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_primary_and_payload_qa_agent_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/agents/invet-qa-validator.md").read_text(
        encoding="utf-8"
    )
    payload = (REPO_ROOT / "payload/.opencode/agents/invet-qa-validator.md").read_text(
        encoding="utf-8"
    )

    assert primary == payload


def test_primary_and_payload_qa_command_are_in_sync() -> None:
    primary = (REPO_ROOT / ".opencode/commands/qa-task.md").read_text(encoding="utf-8")
    payload = (REPO_ROOT / "payload/.opencode/commands/qa-task.md").read_text(
        encoding="utf-8"
    )

    assert primary == payload


def test_primary_and_payload_qa_templates_are_in_sync() -> None:
    template_pairs = [
        (
            REPO_ROOT / "docs/opencode/templates/qa_findings_template.md",
            REPO_ROOT / "payload/docs/opencode/templates/qa_findings_template.md",
        ),
        (
            REPO_ROOT / "docs/opencode/templates/qa_results_template.md",
            REPO_ROOT / "payload/docs/opencode/templates/qa_results_template.md",
        ),
    ]

    for primary, payload in template_pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )


def test_qa_agent_frontmatter_allows_known_safe_validation_commands() -> None:
    frontmatter = _read_frontmatter(
        REPO_ROOT / ".opencode/agents/invet-qa-validator.md"
    )

    required_patterns = [
        "pytest*",
        "python -m pytest*",
        "coverage*",
        "python -m coverage*",
        "python -m pip install*",
        "pip install*",
        "git status*",
        "git diff*",
        "git log*",
        "git show*",
    ]

    for pattern in required_patterns:
        assert pattern in frontmatter


def test_qa_agent_body_includes_required_states_and_gates() -> None:
    body = _read_body(REPO_ROOT / ".opencode/agents/invet-qa-validator.md")

    required_phrases = [
        "PASS",
        "FAIL",
        "BLOCKED",
        "NOT_APPLICABLE",
        "APPROVED",
        "REJECTED",
        "Matriz de trazabilidad",
        "JUnit XML",
        "git diff",
        "No modificar codigo productivo",
        "solo puede cambiar una tarea de",
        "prepare_qa_env.py",
        ".env.qa",
        "sqlite:///./qa-test.db",
        "baseline auditable",
        "NOT_APPLICABLE",
        "frontend/package.json",
        "run-checks",
    ]

    for phrase in required_phrases:
        assert phrase in body


def test_qa_command_invalidates_stale_frontend_not_applicable_results() -> None:
    command = (REPO_ROOT / ".opencode/commands/qa-task.md").read_text(encoding="utf-8")

    required_phrases = [
        "auditalo antes de reutilizarlo",
        "invalida conclusiones historicas",
        "no conserves `NOT_APPLICABLE` para frontend",
        "frontend/package.json",
        "run-checks",
        "evidencia stale",
    ]

    for phrase in required_phrases:
        assert phrase in command


def test_qa_findings_template_has_required_fields() -> None:
    template = (
        REPO_ROOT / "docs/opencode/templates/qa_findings_template.md"
    ).read_text(encoding="utf-8")

    required_fields = [
        "Identificador",
        "Severidad",
        "Criterio afectado",
        "Componente",
        "Ambiente",
        "Precondiciones",
        "Pasos para reproducir",
        "Resultado esperado",
        "Resultado observado",
        "Prueba de regresion propuesta",
        "Estado",
    ]

    for field in required_fields:
        assert field in template


def test_qa_results_template_has_required_sections() -> None:
    template = (REPO_ROOT / "docs/opencode/templates/qa_results_template.md").read_text(
        encoding="utf-8"
    )

    required_sections = [
        "commit",
        "branch",
        "timestamp",
        "Matriz de trazabilidad",
        "criterios y estados",
        "Comandos ejecutados",
        "Codigos de salida",
        "Cobertura",
        "Comparacion contra baseline",
        "Decision final",
    ]

    lower_template = template.lower()
    for section in required_sections:
        assert section.lower() in lower_template


def _read_frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return parts[1]


def _read_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return parts[2]
