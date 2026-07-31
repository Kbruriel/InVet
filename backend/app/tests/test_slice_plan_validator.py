from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / "backend/scripts/validate_slice_plan.py"
TEMPLATE_PATH = REPO_ROOT / "docs/opencode/templates/slice_plan_template.md"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "invet_slice_plan_validator",
        VALIDATOR_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


@pytest.mark.parametrize("prefix", ["BE", "FE", "QA", "be", "fe", "qa"])
def test_normalize_slice_id_keeps_the_vertical_index(prefix: str) -> None:
    result = validator.normalize_slice_id(f"{prefix}-007")

    assert result.index == "007"
    assert result.backend == "BE-007"
    assert result.frontend == "FE-007"
    assert result.qa == "QA-007"


def test_normalize_slice_id_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        validator.normalize_slice_id("FE-7")


def test_schema_v2_template_is_valid() -> None:
    ids = validator.normalize_slice_id("FE-002")
    text = TEMPLATE_PATH.read_text(encoding="utf-8").replace("XXX", "002")

    assert validator.validate_plan_text(text, ids) == []


def test_plan_rejects_missing_frontend_contract_section() -> None:
    ids = validator.normalize_slice_id("BE-002")
    text = TEMPLATE_PATH.read_text(encoding="utf-8").replace("XXX", "002")
    text = text.replace("### Formularios y validacion\n", "")

    errors = validator.validate_plan_text(text, ids)

    assert "Falta la subseccion frontend: formularios y validacion." in errors


def test_completed_task_requires_evidence() -> None:
    ids = validator.normalize_slice_id("BE-002")
    text = TEMPLATE_PATH.read_text(encoding="utf-8").replace("XXX", "002")
    text = text.replace("- [ ] BE-002-T01", "- [x] BE-002-T01")

    errors = validator.validate_plan_text(text, ids)

    assert any("esta completada sin evidencia verificable" in error for error in errors)


def test_previous_qa_gate_blocks_and_resolved_findings_do_not(
    tmp_path: Path,
) -> None:
    qa_dir = tmp_path / "docs/opencode/qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "QA-001-results.md").write_text(
        "## Decision final\n\n- decision: `APPROVED`\n",
        encoding="utf-8",
    )
    findings = qa_dir / "QA-001-findings.md"
    findings.write_text("- Estado: `RESOLVED`\n", encoding="utf-8")
    ids = validator.normalize_slice_id("FE-002")

    assert validator.validate_previous_slice_gate(tmp_path, ids) == []

    findings.write_text("- Estado: `READY_FOR_REVALIDATION`\n", encoding="utf-8")
    errors = validator.validate_previous_slice_gate(tmp_path, ids)

    assert any("sigue abierto" in error for error in errors)


def test_checks_and_docs_require_approved_evidence(tmp_path: Path) -> None:
    review_dir = tmp_path / "docs/opencode/reviews"
    checks_dir = tmp_path / "docs/opencode/checks"
    review_dir.mkdir(parents=True)
    checks_dir.mkdir(parents=True)
    ids = validator.normalize_slice_id("BE-001")

    for suffix in validator.REVIEW_SUFFIXES:
        (review_dir / f"BE-001-{suffix}.md").write_text(
            "- Decision: `APPROVED`\n",
            encoding="utf-8",
        )
    (checks_dir / "BE-001-checks.md").write_text(
        "- Decision: `APPROVED`\n",
        encoding="utf-8",
    )

    assert validator.validate_review_gates(tmp_path, ids) == []
    assert validator.validate_checks_gate(tmp_path, ids) == []
