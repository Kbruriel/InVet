"""Validate InVet slice plans and the gates required before each stage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SLICE_ID_RE = re.compile(r"^(BE|FE|QA)-(?P<index>\d{3})$", re.IGNORECASE)
TASK_RE = re.compile(
    r"^- \[(?P<done>[ xX])\] " r"(?P<id>(?:BE|FE|QA)-\d{3}-T\d{2})\s+-\s+\S.*$"
)
FIELD_RE = re.compile(r"^\s{2,}(?P<name>[^:]+):\s*(?P<value>.*)$")

REQUIRED_SECTIONS = (
    "objetivo del slice",
    "alcance mvp",
    "fuera de alcance",
    "entidades y reglas de negocio",
    "endpoints esperados",
    "contrato de implementacion frontend",
    "pruebas qa",
    "riesgos de seguridad/idor/bola",
    "checklist tecnico",
    "checklist de tareas",
    "definition of done",
)

REQUIRED_FRONTEND_SECTIONS = (
    "rutas y acceso",
    "flujos y estados ux",
    "contratos api por accion",
    "formularios y validacion",
    "arquitectura de componentes",
    "responsive y accesibilidad",
    "estrategia de pruebas frontend",
)

REQUIRED_TASK_FIELDS = (
    "capa",
    "objetivo",
    "depende de",
    "entregables",
    "criterios de aceptacion",
    "validacion",
    "evidencia",
    "paralelismo[p]",
)

FINAL_STAGES = {"review", "checks", "docs"}
RESOLVED_FINDING_STATES = {"RESOLVED", "ACCEPTED_RISK"}
REVIEW_SUFFIXES = ("review", "clean-architecture-review", "security-review")
SECURE_PERSISTENCE_KEYWORDS = (
    "alembic",
    "auditoria",
    "audit",
    "base de datos",
    "bola",
    "database",
    "db",
    "idor",
    "infraestructura",
    "migration",
    "migracion",
    "migraciones",
    "modelo",
    "modelos",
    "orm",
    "ownership",
    "permisos",
    "persistencia",
    "repository",
    "repositorio",
    "repositorios",
    "sqlalchemy",
    "tenant",
)


@dataclass(frozen=True)
class SliceIds:
    index: str
    backend: str
    frontend: str
    qa: str


@dataclass
class PlanTask:
    task_id: str
    done: bool
    line_number: int
    fields: dict[str, str]


def normalize_slice_id(value: str) -> SliceIds:
    match = SLICE_ID_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"ID invalido: {value!r}. Usa BE-00X, FE-00X o QA-00X.")

    index = match.group("index")
    return SliceIds(
        index=index,
        backend=f"BE-{index}",
        frontend=f"FE-{index}",
        qa=f"QA-{index}",
    )


def _normalize_label(value: str) -> str:
    return re.sub(r"[`*]", "", value).strip().lower()


def _extract_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for line in text.splitlines():
        if line.startswith("#"):
            headings.add(_normalize_label(line.lstrip("#").strip()))
    return headings


def _parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[_normalize_label(key)] = value.strip().strip("\"'")
    return values


def _parse_tasks(text: str) -> list[PlanTask]:
    tasks: list[PlanTask] = []
    current: PlanTask | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        task_match = TASK_RE.match(line)
        if task_match:
            current = PlanTask(
                task_id=task_match.group("id").upper(),
                done=task_match.group("done").lower() == "x",
                line_number=line_number,
                fields={},
            )
            tasks.append(current)
            continue

        if current is None:
            continue

        if line.startswith("#") or (line.startswith("- [") and not task_match):
            current = None
            continue

        field_match = FIELD_RE.match(line)
        if field_match:
            name = _normalize_label(field_match.group("name"))
            current.fields[name] = field_match.group("value").strip()

    return tasks


def _validate_plan_metadata(
    text: str,
    expected: SliceIds,
) -> list[str]:
    errors: list[str] = []
    frontmatter = _parse_frontmatter(text)
    headings = _extract_headings(text)

    if frontmatter.get("schema_version") != "2":
        errors.append("El frontmatter debe declarar schema_version: 2.")
    if frontmatter.get("slice") != expected.index:
        errors.append(f'El frontmatter debe declarar slice: "{expected.index}".')
    if frontmatter.get("canonical_plan", "").upper() != expected.backend:
        errors.append(
            f"El frontmatter debe declarar canonical_plan: {expected.backend}."
        )

    for section in REQUIRED_SECTIONS:
        if section not in headings:
            errors.append(f"Falta la seccion obligatoria: {section}.")

    for section in REQUIRED_FRONTEND_SECTIONS:
        if section not in headings:
            errors.append(f"Falta la subseccion frontend: {section}.")

    return errors


def _validate_dependencies(task: PlanTask, task_ids: set[str]) -> list[str]:
    dependency_value = task.fields.get("depende de", "")
    if _normalize_label(dependency_value) in {"ninguna", "ninguno"}:
        return []

    errors: list[str] = []
    dependencies = {
        value.upper()
        for value in re.findall(
            r"(?:BE|FE|QA)-\d{3}-T\d{2}",
            dependency_value,
            flags=re.IGNORECASE,
        )
    }
    if not dependencies:
        return [
            f"Linea {task.line_number}: Depende de debe usar IDs de tarea " "o Ninguna."
        ]

    for dependency in dependencies:
        if dependency == task.task_id:
            errors.append(
                f"Linea {task.line_number}: una tarea no puede depender de si misma."
            )
        elif dependency not in task_ids:
            errors.append(
                f"Linea {task.line_number}: dependencia inexistente {dependency}."
            )
    return errors


def _validate_task(
    task: PlanTask,
    task_ids: set[str],
    expected: SliceIds,
    expected_prefixes: dict[str, str],
) -> tuple[list[str], str]:
    errors: list[str] = []
    prefix = task.task_id.split("-T", 1)[0]
    if prefix not in expected_prefixes.values():
        errors.append(
            f"Linea {task.line_number}: {task.task_id} no pertenece al slice "
            f"{expected.index}."
        )

    for field in REQUIRED_TASK_FIELDS:
        if not task.fields.get(field):
            errors.append(
                f"Linea {task.line_number}: {task.task_id} no define {field}."
            )

    layer = _normalize_label(task.fields.get("capa", ""))
    expected_prefix = expected_prefixes.get(layer)
    if layer and expected_prefix is None:
        errors.append(f"Linea {task.line_number}: capa invalida {layer!r}.")
    elif layer and prefix != expected_prefix:
        errors.append(
            f"Linea {task.line_number}: {task.task_id} no coincide con "
            f"la capa {layer}."
        )

    errors.extend(_validate_dependencies(task, task_ids))

    parallelism = _normalize_label(task.fields.get("paralelismo[p]", ""))
    if parallelism not in {"si", "no"}:
        errors.append(f"Linea {task.line_number}: Paralelismo[P] debe ser Si o No.")

    evidence = _normalize_label(task.fields.get("evidencia", ""))
    if task.done and evidence in {"", "pending", "pendiente", "ninguna", "n/a"}:
        errors.append(
            f"Linea {task.line_number}: {task.task_id} esta completada sin "
            "evidencia verificable."
        )

    return errors, layer


def validate_plan_text(text: str, expected: SliceIds) -> list[str]:
    errors = _validate_plan_metadata(text, expected)
    tasks = _parse_tasks(text)
    if not tasks:
        errors.append("El plan no contiene tareas con el formato BE|FE|QA-00X-TNN.")
        return errors

    task_ids = [task.task_id for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        errors.append("Los IDs de tarea deben ser unicos.")

    task_id_set = set(task_ids)
    expected_prefixes = {
        "backend": expected.backend,
        "frontend": expected.frontend,
        "qa": expected.qa,
    }
    found_layers: set[str] = set()

    for task in tasks:
        task_errors, layer = _validate_task(
            task,
            task_id_set,
            expected,
            expected_prefixes,
        )
        errors.extend(task_errors)
        if layer:
            found_layers.add(layer)

    for layer in expected_prefixes:
        if layer not in found_layers:
            errors.append(f"El plan debe incluir al menos una tarea de capa {layer}.")

    return errors


def validate_plan_file(repo_root: Path, slice_ids: SliceIds) -> list[str]:
    plan_path = (
        repo_root / "docs" / "opencode" / "plans" / f"{slice_ids.backend}-plan.md"
    )
    if not plan_path.exists():
        return [
            f"No existe {plan_path.relative_to(repo_root)}. "
            f"Ejecuta /plan-task {slice_ids.backend}."
        ]
    return validate_plan_text(plan_path.read_text(encoding="utf-8"), slice_ids)


def _read_plan_tasks(repo_root: Path, slice_ids: SliceIds) -> list[PlanTask]:
    plan_path = (
        repo_root / "docs" / "opencode" / "plans" / f"{slice_ids.backend}-plan.md"
    )
    if not plan_path.exists():
        return []
    return _parse_tasks(plan_path.read_text(encoding="utf-8"))


def _task_matches_secure_persistence(task: PlanTask) -> bool:
    if _normalize_label(task.fields.get("capa", "")) != "backend":
        return False

    searchable = " ".join(
        (
            task.task_id,
            task.fields.get("objetivo", ""),
            task.fields.get("entregables", ""),
            task.fields.get("criterios de aceptacion", ""),
            task.fields.get("validacion", ""),
        )
    )
    normalized = _normalize_label(searchable)
    return any(keyword in normalized for keyword in SECURE_PERSISTENCE_KEYWORDS)


def validate_secure_persistence_gate(repo_root: Path, slice_ids: SliceIds) -> list[str]:
    tasks = [
        task
        for task in _read_plan_tasks(repo_root, slice_ids)
        if _task_matches_secure_persistence(task)
    ]
    if not tasks:
        return [
            "El plan debe incluir al menos una tarea backend de persistencia segura "
            "con entregables verificables."
        ]

    errors: list[str] = []
    for task in tasks:
        evidence = _normalize_label(task.fields.get("evidencia", ""))
        if not task.done:
            errors.append(
                f"{task.task_id} pertenece a persistencia segura y sigue pendiente."
            )
        elif evidence in {"", "pending", "pendiente", "ninguna", "n/a"}:
            errors.append(
                f"{task.task_id} pertenece a persistencia segura y no tiene "
                "evidencia verificable."
            )
    return errors


def _read_qa_decision(results_path: Path) -> str | None:
    if not results_path.exists():
        return None
    text = results_path.read_text(encoding="utf-8")
    patterns = (
        r"decision\s*:\s*`?(APPROVED|REJECTED|BLOCKED)`?",
        r"resultado de validaci[oó]n[^:\n]*:\s*\*{0,2}" r"(APPROVED|REJECTED|BLOCKED)",
        r"decisi[oó]n final[^A-Z]+(APPROVED|REJECTED|BLOCKED)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def _read_finding_state(findings_path: Path) -> str | None:
    if not findings_path.exists():
        return None
    text = findings_path.read_text(encoding="utf-8")
    match = re.search(
        r"(?im)^-\s*Estado:\s*`?([A-Z_]+)`?\s*$",
        text,
    )
    return match.group(1).upper() if match else "OPEN"


def validate_previous_slice_gate(repo_root: Path, slice_ids: SliceIds) -> list[str]:
    current_index = int(slice_ids.index)
    if current_index <= 1:
        return []

    previous_index = f"{current_index - 1:03d}"
    qa_dir = repo_root / "docs" / "opencode" / "qa"
    results_path = qa_dir / f"QA-{previous_index}-results.md"
    findings_path = qa_dir / f"QA-{previous_index}-findings.md"
    errors: list[str] = []

    decision = _read_qa_decision(results_path)
    if decision != "APPROVED":
        shown = decision or "MISSING"
        errors.append(
            f"QA-{previous_index} debe estar APPROVED antes de iniciar el slice "
            f"{slice_ids.index}; estado actual: {shown}."
        )

    finding_state = _read_finding_state(findings_path)
    if finding_state and finding_state not in RESOLVED_FINDING_STATES:
        errors.append(
            f"QA-{previous_index}-findings.md sigue abierto con estado "
            f"{finding_state}."
        )

    return errors


def validate_current_qa_gate(repo_root: Path, slice_ids: SliceIds) -> list[str]:
    qa_dir = repo_root / "docs" / "opencode" / "qa"
    results_path = qa_dir / f"{slice_ids.qa}-results.md"
    findings_path = qa_dir / f"{slice_ids.qa}-findings.md"
    errors: list[str] = []

    decision = _read_qa_decision(results_path)
    if decision != "APPROVED":
        shown = decision or "MISSING"
        errors.append(
            f"{slice_ids.qa} debe estar APPROVED para este gate; "
            f"estado actual: {shown}."
        )

    finding_state = _read_finding_state(findings_path)
    if finding_state and finding_state not in RESOLVED_FINDING_STATES:
        errors.append(
            f"{slice_ids.qa}-findings.md sigue abierto con estado {finding_state}."
        )

    return errors


def _read_approved_decision(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"(?im)^-\s*Decision:\s*`?(APPROVED|REJECTED)`?\s*$",
        text,
    )
    return match.group(1).upper() if match else None


def validate_review_gates(repo_root: Path, slice_ids: SliceIds) -> list[str]:
    review_dir = repo_root / "docs" / "opencode" / "reviews"
    errors: list[str] = []
    for suffix in REVIEW_SUFFIXES:
        path = review_dir / f"{slice_ids.backend}-{suffix}.md"
        decision = _read_approved_decision(path)
        if decision != "APPROVED":
            errors.append(
                f"{path.name} debe existir con Decision: APPROVED; "
                f"estado actual: {decision or 'MISSING'}."
            )
    return errors


def validate_checks_gate(repo_root: Path, slice_ids: SliceIds) -> list[str]:
    path = repo_root / "docs" / "opencode" / "checks" / f"{slice_ids.backend}-checks.md"
    decision = _read_approved_decision(path)
    if decision == "APPROVED":
        return []
    return [
        f"{path.name} debe existir con Decision: APPROVED; "
        f"estado actual: {decision or 'MISSING'}."
    ]


def validate_stage(repo_root: Path, slice_ids: SliceIds, stage: str) -> list[str]:
    if stage == "previous":
        return validate_previous_slice_gate(repo_root, slice_ids)

    errors = validate_plan_file(repo_root, slice_ids)
    errors.extend(validate_previous_slice_gate(repo_root, slice_ids))
    if stage == "secure-persistence":
        errors.extend(validate_secure_persistence_gate(repo_root, slice_ids))
    if stage in FINAL_STAGES:
        errors.extend(validate_current_qa_gate(repo_root, slice_ids))
    if stage in {"checks", "docs"}:
        errors.extend(validate_review_gates(repo_root, slice_ids))
    if stage == "docs":
        errors.extend(validate_checks_gate(repo_root, slice_ids))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida el plan y los gates de un slice InVet."
    )
    parser.add_argument("slice_id", help="BE-00X, FE-00X o QA-00X")
    parser.add_argument(
        "--stage",
        choices=(
            "previous",
            "plan",
            "backend",
            "frontend",
            "secure-persistence",
            "qa",
            "findings",
            "review",
            "checks",
            "docs",
        ),
        default="plan",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        slice_ids = normalize_slice_id(args.slice_id)
    except ValueError as exc:
        parser.error(str(exc))

    repo_root = args.repo_root.resolve()
    errors = validate_stage(repo_root, slice_ids, args.stage)
    result = {
        "slice": slice_ids.index,
        "canonical_plan": slice_ids.backend,
        "stage": args.stage,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }

    if args.as_json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(
            f"[{result['status']}] {slice_ids.backend}/{slice_ids.frontend}/"
            f"{slice_ids.qa} stage={args.stage}"
        )
        for error in errors:
            print(f"- {error}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
