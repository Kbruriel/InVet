"""Deterministic QA validation models used by the InVet QA agent contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Sequence
from xml.etree import ElementTree


class TraceabilityStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FinalDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class TestLevel(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    CONTRACT = "contract"
    END_TO_END = "end-to-end"
    REGRESSION = "regression"
    SECURITY = "security"
    FRONTEND = "frontend"
    MODELS_AND_DATA = "models-and-data"


class DefectSeverity(str, Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class RegressionClassification(str, Enum):
    PREEXISTING = "preexisting"
    NEW = "new"
    ENVIRONMENT = "environment"
    FLAKY = "flaky"


class ExecutionIssue(str, Enum):
    ZERO_TESTS_EXECUTED = "zero-tests-executed"
    EXECUTED_COUNT_MISMATCH = "executed-count-mismatch"
    EXIT_CODE_MISMATCH = "exit-code-mismatch"
    COLLECTION_ERRORS = "collection-errors"
    SETUP_ERRORS = "setup-errors"
    REPORT_MISSING = "report-missing"
    STALE_REPORT = "stale-report"
    ASSERTIONLESS_SUITE = "assertionless-suite"
    RETRIES_DETECTED = "retries-detected"


@dataclass(frozen=True)
class AcceptanceCriterionResult:
    criterion_id: str
    description: str
    status: TraceabilityStatus
    evidence: tuple[str, ...] = ()
    justification: str | None = None
    risk: str | None = None
    test_case: str | None = None
    test_level: TestLevel | None = None
    suite: str | None = None
    command: str | None = None
    result_summary: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence", tuple(self.evidence))
        if self.status is TraceabilityStatus.PASS and not self.evidence:
            raise ValueError("PASS criteria require reproducible evidence.")
        if (
            self.status
            in {
                TraceabilityStatus.BLOCKED,
                TraceabilityStatus.NOT_APPLICABLE,
            }
            and not self.justification
        ):
            raise ValueError(
                f"{self.status.value} criteria require a concrete justification."
            )


@dataclass(frozen=True)
class Defect:
    defect_id: str
    severity: DefectSeverity
    summary: str
    resolved: bool = False


@dataclass(frozen=True)
class RegressionFinding:
    finding_id: str
    classification: RegressionClassification
    summary: str


@dataclass(frozen=True)
class SuiteExecution:
    suite_name: str
    command: str
    exit_code: int
    collected: int
    executed: int
    passed: int
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    xfailed: int = 0
    xpassed: int = 0
    duration_seconds: float | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    report_path: Path | None = None
    report_generated_at: datetime | None = None
    target_identifiers: tuple[str, ...] = ()
    collection_errors: int = 0
    setup_errors: int = 0
    used_retries: bool = False
    has_assertions: bool = True
    critical: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_identifiers", tuple(self.target_identifiers))
        if self.report_path is not None:
            object.__setattr__(self, "report_path", Path(self.report_path))

    @classmethod
    def from_junit_xml(
        cls,
        *,
        suite_name: str,
        command: str,
        exit_code: int,
        report_path: Path,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        critical: bool = True,
    ) -> "SuiteExecution":
        try:
            root = ElementTree.parse(report_path).getroot()
        except ElementTree.ParseError as exc:
            raise ValueError(f"Invalid JUnit XML report: {report_path}") from exc

        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
        if not suites:
            raise ValueError("JUnit report does not contain any testsuite nodes.")

        collected = _sum_suite_attr(suites, "tests")
        failed = _sum_suite_attr(suites, "failures")
        errors = _sum_suite_attr(suites, "errors")
        skipped = _sum_suite_attr(suites, "skipped")
        passed = max(collected - failed - errors - skipped, 0)

        timestamp_value = next(
            (
                suite.attrib["timestamp"]
                for suite in suites
                if suite.attrib.get("timestamp")
            ),
            None,
        )
        report_generated_at = _parse_datetime(timestamp_value)
        if report_generated_at is None:
            report_generated_at = datetime.fromtimestamp(
                report_path.stat().st_mtime,
                tz=timezone.utc,
            )

        duration_value = next(
            (suite.attrib["time"] for suite in suites if suite.attrib.get("time")),
            None,
        )
        duration_seconds = float(duration_value) if duration_value is not None else None

        return cls(
            suite_name=suite_name,
            command=command,
            exit_code=exit_code,
            collected=collected,
            executed=collected,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            duration_seconds=duration_seconds,
            started_at=started_at,
            finished_at=finished_at,
            report_path=report_path,
            report_generated_at=report_generated_at,
            critical=critical,
        )

    def validation_issues(self) -> tuple[ExecutionIssue, ...]:
        issues: list[ExecutionIssue] = []
        if self.executed == 0:
            issues.append(ExecutionIssue.ZERO_TESTS_EXECUTED)
        if self._has_count_mismatch():
            issues.append(ExecutionIssue.EXECUTED_COUNT_MISMATCH)
        if self.collection_errors > 0:
            issues.append(ExecutionIssue.COLLECTION_ERRORS)
        if self.setup_errors > 0:
            issues.append(ExecutionIssue.SETUP_ERRORS)
        if self._has_exit_code_mismatch():
            issues.append(ExecutionIssue.EXIT_CODE_MISMATCH)
        if self.report_path is not None and not self.report_path.exists():
            issues.append(ExecutionIssue.REPORT_MISSING)
        if self._has_stale_report():
            issues.append(ExecutionIssue.STALE_REPORT)
        if not self.has_assertions:
            issues.append(ExecutionIssue.ASSERTIONLESS_SUITE)
        if self.used_retries:
            issues.append(ExecutionIssue.RETRIES_DETECTED)
        return tuple(issues)

    def _has_count_mismatch(self) -> bool:
        return self.collected < self.executed or self._outcome_total() != self.executed

    def _has_exit_code_mismatch(self) -> bool:
        if self.exit_code == 0:
            return self._has_execution_errors()
        return not self._has_execution_errors()

    def _has_execution_errors(self) -> bool:
        return any(
            (
                self.failed > 0,
                self.errors > 0,
                self.collection_errors > 0,
                self.setup_errors > 0,
            )
        )

    def _has_stale_report(self) -> bool:
        return (
            self.report_generated_at is not None
            and self.started_at is not None
            and self.report_generated_at < self.started_at
        )

    def _outcome_total(self) -> int:
        return (
            self.passed
            + self.failed
            + self.errors
            + self.skipped
            + self.xfailed
            + self.xpassed
        )


@dataclass(frozen=True)
class DecisionSummary:
    decision: FinalDecision
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ImpactAnalysis:
    changed_files: tuple[str, ...]
    affected_areas: tuple[str, ...]
    suggested_levels: tuple[TestLevel, ...]
    suggested_commands: tuple[str, ...]
    requires_full_regression: bool


@dataclass(frozen=True)
class UnitTestCoverageGap:
    source_file: str
    layer: str
    expected_test_files: tuple[str, ...]
    reason: str = "Missing explicit unit tests for the changed source file."

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_file", _normalize_path(self.source_file))
        object.__setattr__(self, "expected_test_files", tuple(self.expected_test_files))


@dataclass(frozen=True)
class UnitTestCoverageReport:
    required_source_files: tuple[str, ...]
    discovered_test_files: tuple[str, ...]
    missing_gaps: tuple[UnitTestCoverageGap, ...]

    @property
    def is_satisfied(self) -> bool:
        return not self.missing_gaps


def classify_slice_decision(
    *,
    criteria: Sequence[AcceptanceCriterionResult],
    suite_executions: Sequence[SuiteExecution],
    defects: Sequence[Defect] = (),
    regressions: Sequence[RegressionFinding] = (),
    unit_test_gaps: Sequence[UnitTestCoverageGap] = (),
    secret_exposure: bool = False,
    pii_exposure: bool = False,
    required_suite_names: Sequence[str] = (),
    justified_out_of_scope: Sequence[str] = (),
) -> DecisionSummary:
    rejected_reasons, blocked_reasons = _collect_decision_reasons(
        criteria=criteria,
        suite_executions=suite_executions,
        defects=defects,
        regressions=regressions,
        unit_test_gaps=unit_test_gaps,
        secret_exposure=secret_exposure,
        pii_exposure=pii_exposure,
        required_suite_names=required_suite_names,
        justified_out_of_scope=justified_out_of_scope,
    )

    if rejected_reasons:
        return DecisionSummary(FinalDecision.REJECTED, tuple(rejected_reasons))
    if blocked_reasons:
        return DecisionSummary(FinalDecision.BLOCKED, tuple(blocked_reasons))
    return DecisionSummary(FinalDecision.APPROVED, ("All approval gates passed.",))


def can_mark_qa_task_completed(
    *,
    task_kind: str,
    criterion_status: TraceabilityStatus,
    evidence_links: Sequence[str],
    required_tests_executed: bool,
    unresolved_defects: Sequence[Defect] = (),
) -> bool:
    normalized_task_kind = task_kind.strip().lower()
    if normalized_task_kind not in {"qa", "validation"}:
        return False
    if criterion_status is not TraceabilityStatus.PASS:
        return False
    if not evidence_links or not required_tests_executed:
        return False
    return not any(
        not defect.resolved and defect.severity is DefectSeverity.BLOCKER
        for defect in unresolved_defects
    )


def analyze_changed_files(changed_files: Iterable[str]) -> ImpactAnalysis:
    normalized_files = tuple(_normalize_path(path) for path in changed_files)
    affected_areas: set[str] = set()
    suggested_levels: set[TestLevel] = set()
    suggested_commands: list[str] = []
    requires_full_regression = False

    def add_command(command: str) -> None:
        if command not in suggested_commands:
            suggested_commands.append(command)

    for path in normalized_files:
        path_parts = PurePosixPath(path).parts
        _apply_primary_impact(
            path=path,
            affected_areas=affected_areas,
            suggested_levels=suggested_levels,
            add_command=add_command,
        )
        _apply_targeted_impact(
            path=path,
            affected_areas=affected_areas,
            suggested_levels=suggested_levels,
        )
        if _is_shared_surface(path_parts):
            requires_full_regression = True

    return ImpactAnalysis(
        changed_files=normalized_files,
        affected_areas=tuple(sorted(affected_areas)),
        suggested_levels=tuple(sorted(suggested_levels, key=lambda level: level.value)),
        suggested_commands=tuple(suggested_commands),
        requires_full_regression=requires_full_regression,
    )


def analyze_unit_test_coverage(
    changed_files: Iterable[str],
    discovered_test_files: Iterable[str],
) -> UnitTestCoverageReport:
    normalized_changed = tuple(_normalize_path(path) for path in changed_files)
    normalized_tests = tuple(_normalize_path(path) for path in discovered_test_files)
    required_source_files: list[str] = []
    missing_gaps: list[UnitTestCoverageGap] = []

    for source_file in normalized_changed:
        if not _requires_unit_test_gate(source_file):
            continue

        required_source_files.append(source_file)
        if _has_matching_unit_test(source_file, normalized_tests):
            continue

        missing_gaps.append(
            UnitTestCoverageGap(
                source_file=source_file,
                layer=_layer_for_source_file(source_file),
                expected_test_files=_expected_unit_test_files(source_file),
            )
        )

    return UnitTestCoverageReport(
        required_source_files=tuple(required_source_files),
        discovered_test_files=normalized_tests,
        missing_gaps=tuple(missing_gaps),
    )


def _is_shared_surface(path_parts: tuple[str, ...]) -> bool:
    shared_prefixes = {
        ("backend", "app", "core"),
        ("backend", "app", "infrastructure"),
        ("frontend", "src", "shared"),
        (".opencode", "agents"),
        (".opencode", "commands"),
        ("docs", "opencode", "templates"),
    }
    return any(path_parts[: len(prefix)] == prefix for prefix in shared_prefixes)


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def _collect_decision_reasons(
    *,
    criteria: Sequence[AcceptanceCriterionResult],
    suite_executions: Sequence[SuiteExecution],
    defects: Sequence[Defect],
    regressions: Sequence[RegressionFinding],
    unit_test_gaps: Sequence[UnitTestCoverageGap],
    secret_exposure: bool,
    pii_exposure: bool,
    required_suite_names: Sequence[str],
    justified_out_of_scope: Sequence[str],
) -> tuple[list[str], list[str]]:
    rejected_reasons: list[str] = []
    blocked_reasons: list[str] = []

    applicable_criteria = [
        criterion
        for criterion in criteria
        if criterion.status is not TraceabilityStatus.NOT_APPLICABLE
    ]
    if not applicable_criteria:
        blocked_reasons.append("No applicable acceptance criteria were validated.")

    rejected_reasons.extend(_criterion_failures(applicable_criteria))
    blocked_reasons.extend(_criterion_blocks(applicable_criteria))
    rejected_reasons.extend(_blocking_defects(defects))
    rejected_reasons.extend(_regression_rejections(regressions))
    rejected_reasons.extend(_unit_test_gap_rejections(unit_test_gaps))
    blocked_reasons.extend(_regression_blocks(regressions))
    blocked_reasons.extend(
        _missing_required_suites(
            suite_executions=suite_executions,
            required_suite_names=required_suite_names,
            justified_out_of_scope=justified_out_of_scope,
        )
    )
    rejected_reasons.extend(_suite_rejections(suite_executions))
    blocked_reasons.extend(_suite_blocks(suite_executions))

    if secret_exposure or pii_exposure:
        rejected_reasons.append("Security validation detected secret or PII exposure.")

    return rejected_reasons, blocked_reasons


def _criterion_failures(
    criteria: Sequence[AcceptanceCriterionResult],
) -> list[str]:
    return [
        f"{criterion.criterion_id} failed."
        for criterion in criteria
        if criterion.status is TraceabilityStatus.FAIL
    ]


def _criterion_blocks(criteria: Sequence[AcceptanceCriterionResult]) -> list[str]:
    return [
        f"{criterion.criterion_id} is blocked: {criterion.justification}"
        for criterion in criteria
        if criterion.status is TraceabilityStatus.BLOCKED
    ]


def _blocking_defects(defects: Sequence[Defect]) -> list[str]:
    return [
        f"Unresolved {defect.severity.value} defect: {defect.defect_id}"
        for defect in defects
        if not defect.resolved
        and defect.severity in {DefectSeverity.BLOCKER, DefectSeverity.CRITICAL}
    ]


def _regression_rejections(regressions: Sequence[RegressionFinding]) -> list[str]:
    return [
        f"New regression: {regression.finding_id}"
        for regression in regressions
        if regression.classification is RegressionClassification.NEW
    ]


def _regression_blocks(regressions: Sequence[RegressionFinding]) -> list[str]:
    return [
        f"{regression.classification.value} regression: {regression.finding_id}"
        for regression in regressions
        if regression.classification
        in {RegressionClassification.ENVIRONMENT, RegressionClassification.FLAKY}
    ]


def _unit_test_gap_rejections(
    unit_test_gaps: Sequence[UnitTestCoverageGap],
) -> list[str]:
    return [
        "Missing required unit tests for "
        f"{gap.source_file} ({gap.layer}); expected one of: "
        + ", ".join(gap.expected_test_files)
        for gap in unit_test_gaps
    ]


def _missing_required_suites(
    *,
    suite_executions: Sequence[SuiteExecution],
    required_suite_names: Sequence[str],
    justified_out_of_scope: Sequence[str],
) -> list[str]:
    suites_by_name = {suite.suite_name: suite for suite in suite_executions}
    missing_suites = sorted(
        set(required_suite_names) - set(justified_out_of_scope) - set(suites_by_name)
    )
    if not missing_suites:
        return []
    return ["Missing required suites: " + ", ".join(missing_suites)]


def _suite_rejections(suite_executions: Sequence[SuiteExecution]) -> list[str]:
    return [
        f"Suite {suite.suite_name} has failing tests."
        for suite in suite_executions
        if suite.failed > 0 or suite.errors > 0
    ]


def _suite_blocks(suite_executions: Sequence[SuiteExecution]) -> list[str]:
    blocked_reasons: list[str] = []
    for suite in suite_executions:
        blocked_reasons.extend(_suite_specific_blocks(suite))
        blocked_reasons.extend(
            [
                f"Suite {suite.suite_name} has invalid evidence: {issue.value}"
                for issue in suite.validation_issues()
            ]
        )
    return blocked_reasons


def _suite_specific_blocks(suite: SuiteExecution) -> list[str]:
    if not suite.critical or suite.skipped == 0:
        return []
    return [f"Suite {suite.suite_name} skipped critical tests ({suite.skipped})."]


def _requires_unit_test_gate(path: str) -> bool:
    normalized = _normalize_path(path)
    suffix = PurePosixPath(normalized).suffix.lower()

    if normalized.startswith("backend/app/"):
        return (
            suffix == ".py"
            and "/tests/" not in normalized
            and not normalized.endswith("__init__.py")
        )

    if normalized.startswith("frontend/src/"):
        return (
            suffix in {".ts", ".tsx"}
            and not normalized.endswith(".d.ts")
            and not _is_frontend_test_file(normalized)
        )

    return False


def _layer_for_source_file(path: str) -> str:
    normalized = _normalize_path(path)
    if normalized.startswith("backend/"):
        return "backend"
    if normalized.startswith("frontend/"):
        return "frontend"
    return "unknown"


def _expected_unit_test_files(path: str) -> tuple[str, ...]:
    normalized = _normalize_path(path)
    stem = PurePosixPath(normalized).stem
    if normalized.startswith("backend/"):
        return (f"test_{stem}.py", f"{stem}_test.py")
    return (
        f"{stem}.test.ts",
        f"{stem}.test.tsx",
        f"{stem}.spec.ts",
        f"{stem}.spec.tsx",
    )


def _has_matching_unit_test(source_file: str, test_files: Sequence[str]) -> bool:
    expected_names = {name.lower() for name in _expected_unit_test_files(source_file)}
    for test_file in test_files:
        test_name = PurePosixPath(test_file).name.lower()
        if test_name in expected_names:
            return True
    return False


def _is_frontend_test_file(path: str) -> bool:
    normalized = _normalize_path(path).lower()
    test_suffixes = (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")
    return normalized.endswith(test_suffixes)


def _apply_primary_impact(
    *,
    path: str,
    affected_areas: set[str],
    suggested_levels: set[TestLevel],
    add_command: Callable[[str], None],
) -> None:
    if path.startswith("backend/"):
        affected_areas.add("backend")
        suggested_levels.update(
            {TestLevel.UNIT, TestLevel.INTEGRATION, TestLevel.REGRESSION}
        )
        for command in (
            "python -m pytest app/tests -q",
            "python -m ruff check .",
            "python -m black --check .",
            "python -m mypy app",
        ):
            add_command(command)
    if path.startswith("frontend/"):
        affected_areas.add("frontend")
        suggested_levels.update({TestLevel.FRONTEND, TestLevel.REGRESSION})
        for command in ("npm run test", "npm run lint", "npm run build"):
            add_command(command)
    if path.startswith(".opencode/") or path.startswith("docs/opencode/"):
        affected_areas.add("qa-automation")
        suggested_levels.update({TestLevel.UNIT, TestLevel.REGRESSION})
        add_command(
            "python -m pytest app/tests/test_qa_validation.py "
            "app/tests/test_qa_agent_contracts.py -q"
        )


def _apply_targeted_impact(
    *,
    path: str,
    affected_areas: set[str],
    suggested_levels: set[TestLevel],
) -> None:
    if path.startswith("backend/alembic/"):
        affected_areas.add("migrations")
        suggested_levels.add(TestLevel.MODELS_AND_DATA)
    if "api/" in path:
        affected_areas.add("api-contracts")
        suggested_levels.add(TestLevel.CONTRACT)
    if "domain/" in path or "models/" in path:
        affected_areas.add("domain-models")
        suggested_levels.add(TestLevel.MODELS_AND_DATA)
    if "security" in path:
        affected_areas.add("security")
        suggested_levels.add(TestLevel.SECURITY)


def _sum_suite_attr(
    suites: Sequence[ElementTree.Element],
    attribute_name: str,
) -> int:
    total = 0
    for suite in suites:
        raw_value = suite.attrib.get(attribute_name, "0")
        total += int(raw_value or "0")
    return total


def _parse_datetime(raw_value: str | None) -> datetime | None:
    if raw_value is None:
        return None
    parsed_value = raw_value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(parsed_value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
