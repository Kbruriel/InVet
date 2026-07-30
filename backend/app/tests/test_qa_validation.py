from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from app.qa.validation import (
    AcceptanceCriterionResult,
    Defect,
    DefectSeverity,
    ExecutionIssue,
    FinalDecision,
    RegressionClassification,
    RegressionFinding,
    SuiteExecution,
    TraceabilityStatus,
    analyze_changed_files,
    can_mark_qa_task_completed,
    classify_slice_decision,
)


def make_passing_criterion() -> AcceptanceCriterionResult:
    return AcceptanceCriterionResult(
        criterion_id="AC-001",
        description="Happy path covered",
        status=TraceabilityStatus.PASS,
        evidence=("docs/opencode/qa/QA-001-results.md#L1",),
    )


def make_passing_suite(**overrides: object) -> SuiteExecution:
    now = datetime.now(tz=timezone.utc)
    defaults: dict[str, Any] = {
        "suite_name": "backend-pytest",
        "command": "python -m pytest app/tests -q --junitxml report.xml",
        "exit_code": 0,
        "collected": 5,
        "executed": 5,
        "passed": 5,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "started_at": now,
        "finished_at": now + timedelta(seconds=2),
        "report_generated_at": now + timedelta(seconds=1),
    }
    defaults.update(overrides)
    return SuiteExecution(**defaults)


def test_pass_requires_reproducible_evidence() -> None:
    with pytest.raises(ValueError, match="PASS criteria require reproducible evidence"):
        AcceptanceCriterionResult(
            criterion_id="AC-001",
            description="Happy path covered",
            status=TraceabilityStatus.PASS,
        )


@pytest.mark.parametrize(
    "status",
    [TraceabilityStatus.BLOCKED, TraceabilityStatus.NOT_APPLICABLE],
)
def test_blocked_and_not_applicable_require_justification(
    status: TraceabilityStatus,
) -> None:
    with pytest.raises(ValueError, match="require a concrete justification"):
        AcceptanceCriterionResult(
            criterion_id="AC-002",
            description="Risk accepted",
            status=status,
        )


def test_final_decision_is_approved_when_evidence_and_suites_are_clean() -> None:
    summary = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[make_passing_suite()],
    )

    assert summary.decision is FinalDecision.APPROVED


def test_final_decision_is_rejected_when_any_criterion_fails() -> None:
    summary = classify_slice_decision(
        criteria=[
            AcceptanceCriterionResult(
                criterion_id="AC-003",
                description="Negative path handled",
                status=TraceabilityStatus.FAIL,
            )
        ],
        suite_executions=[make_passing_suite()],
    )

    assert summary.decision is FinalDecision.REJECTED
    assert "AC-003 failed." in summary.reasons


@pytest.mark.parametrize(
    "severity",
    [DefectSeverity.BLOCKER, DefectSeverity.CRITICAL],
)
def test_high_severity_defects_prevent_approval(severity: DefectSeverity) -> None:
    summary = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[make_passing_suite()],
        defects=[Defect(defect_id="F-001", severity=severity, summary="Blocking bug")],
    )

    assert summary.decision is FinalDecision.REJECTED
    assert any("F-001" in reason for reason in summary.reasons)


def test_zero_tests_discovered_blocks_the_decision() -> None:
    summary = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[
            make_passing_suite(
                collected=0,
                executed=0,
                passed=0,
                report_generated_at=datetime.now(tz=timezone.utc),
            )
        ],
    )

    assert summary.decision is FinalDecision.BLOCKED
    assert any(
        ExecutionIssue.ZERO_TESTS_EXECUTED.value in reason for reason in summary.reasons
    )


def test_failing_tests_are_detected() -> None:
    summary = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[
            make_passing_suite(exit_code=1, passed=4, failed=1),
        ],
    )

    assert summary.decision is FinalDecision.REJECTED
    assert "Suite backend-pytest has failing tests." in summary.reasons


def test_collection_and_setup_errors_are_reported() -> None:
    suite = make_passing_suite(
        exit_code=1,
        collection_errors=1,
        setup_errors=1,
        executed=4,
        passed=4,
        collected=4,
    )

    assert set(suite.validation_issues()) == {
        ExecutionIssue.COLLECTION_ERRORS,
        ExecutionIssue.SETUP_ERRORS,
    }


def test_skips_and_xfails_are_counted_and_block_critical_suite() -> None:
    summary = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[
            make_passing_suite(
                executed=5,
                passed=2,
                skipped=1,
                xfailed=1,
                xpassed=1,
            )
        ],
    )

    assert summary.decision is FinalDecision.BLOCKED
    assert any("skipped critical tests" in reason for reason in summary.reasons)


def test_regression_classification_distinguishes_preexisting_and_new() -> None:
    preexisting = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[make_passing_suite()],
        regressions=[
            RegressionFinding(
                finding_id="R-001",
                classification=RegressionClassification.PREEXISTING,
                summary="Known issue",
            )
        ],
    )
    new_regression = classify_slice_decision(
        criteria=[make_passing_criterion()],
        suite_executions=[make_passing_suite()],
        regressions=[
            RegressionFinding(
                finding_id="R-002",
                classification=RegressionClassification.NEW,
                summary="New breakage",
            )
        ],
    )

    assert preexisting.decision is FinalDecision.APPROVED
    assert new_regression.decision is FinalDecision.REJECTED


def test_stale_and_inconsistent_reports_are_blocking() -> None:
    now = datetime.now(tz=timezone.utc)
    suite = make_passing_suite(
        exit_code=0,
        passed=4,
        failed=1,
        report_generated_at=now - timedelta(minutes=10),
        started_at=now,
        finished_at=now + timedelta(seconds=2),
    )

    assert set(suite.validation_issues()) == {
        ExecutionIssue.EXIT_CODE_MISMATCH,
        ExecutionIssue.STALE_REPORT,
    }


def test_junit_parser_rejects_empty_reports(tmp_path: Path) -> None:
    report_path = tmp_path / "empty.xml"
    report_path.write_text("<testsuites />", encoding="utf-8")

    with pytest.raises(ValueError, match="does not contain any testsuite nodes"):
        SuiteExecution.from_junit_xml(
            suite_name="backend-pytest",
            command="python -m pytest",
            exit_code=0,
            report_path=report_path,
        )


def test_only_passed_qa_tasks_with_evidence_can_be_completed() -> None:
    blocker = Defect(
        defect_id="F-002",
        severity=DefectSeverity.BLOCKER,
        summary="Blocker defect",
    )

    assert can_mark_qa_task_completed(
        task_kind="qa",
        criterion_status=TraceabilityStatus.PASS,
        evidence_links=["docs/opencode/qa/QA-009-results.md#L1"],
        required_tests_executed=True,
    )
    assert not can_mark_qa_task_completed(
        task_kind="qa",
        criterion_status=TraceabilityStatus.BLOCKED,
        evidence_links=["docs/opencode/qa/QA-009-results.md#L1"],
        required_tests_executed=True,
    )
    assert not can_mark_qa_task_completed(
        task_kind="backend",
        criterion_status=TraceabilityStatus.PASS,
        evidence_links=["docs/opencode/qa/QA-009-results.md#L1"],
        required_tests_executed=True,
    )
    assert not can_mark_qa_task_completed(
        task_kind="qa",
        criterion_status=TraceabilityStatus.PASS,
        evidence_links=[],
        required_tests_executed=True,
    )
    assert not can_mark_qa_task_completed(
        task_kind="qa",
        criterion_status=TraceabilityStatus.PASS,
        evidence_links=["docs/opencode/qa/QA-009-results.md#L1"],
        required_tests_executed=True,
        unresolved_defects=[blocker],
    )


def test_impact_analysis_targets_qa_agent_changes() -> None:
    analysis = analyze_changed_files(
        [
            ".opencode/agents/invet-qa-validator.md",
            "docs/opencode/templates/qa_findings_template.md",
        ]
    )

    assert "qa-automation" in analysis.affected_areas
    assert any(
        "test_qa_validation.py" in command for command in analysis.suggested_commands
    )
    assert analysis.requires_full_regression


def test_impact_analysis_requires_full_regression_for_shared_backend_files() -> None:
    analysis = analyze_changed_files(["backend/app/core/security.py"])

    assert analysis.requires_full_regression
    assert "backend" in analysis.affected_areas
    assert "security" in analysis.affected_areas
