"""Create compact slice manifests and enforce task-scoped implementation controls."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from validate_slice_plan import PlanTask, _parse_tasks, normalize_slice_id

LAYERS = ("backend", "frontend", "qa", "ui-automation", "api-automation")
STATES = {
    "reading": "leyendo",
    "editing": "editando",
    "testing": "ejecutando pruebas",
    "waiting-permission": "esperando permiso",
    "cancelled": "generacion cancelada",
    "failed": "pruebas fallidas",
    "blocked": "bloqueada",
    "completed": "completada",
}
PLAN_LAYER_PREFIX = {"backend": "BE", "frontend": "FE", "qa": "QA"}
AUTOMATION_LAYER_PREFIX = {"UIA": "ui-automation", "APIA": "api-automation"}
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
PATH_RE = re.compile(r"`([^`]*(?:/|\\)[^`]*)`")
ROUTER_RE = re.compile(r"\b[\w.]+\.include_router\((.+?)\)\s*$")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_path(repo_root: Path, value: str) -> str:
    normalized = value.strip().replace("\\", "/").lstrip("./")
    if normalized.startswith("alembic/") and (repo_root / "backend/alembic").exists():
        normalized = f"backend/{normalized}"
    return normalized


def _looks_like_file_path(value: str) -> bool:
    if value.startswith(("http://", "https://", "/api/")):
        return False
    return "/" in value and ("." in PurePosixPath(value).name or value.endswith("/"))


def _paths_from_deliverables(repo_root: Path, task: PlanTask) -> list[str]:
    deliverables = task.fields.get("entregables", "")
    paths = {
        _repo_path(repo_root, match)
        for match in PATH_RE.findall(deliverables)
        if _looks_like_file_path(match)
    }
    if "main router" in deliverables.lower() or "registro en" in deliverables.lower():
        paths.add("backend/app/api/v1/router.py")
    expanded: set[str] = set()
    for path in paths:
        expanded.add(f"{path}**" if path.endswith("/") else path)
        if "[" in path or "component" in deliverables.lower():
            expanded.add(f"{PurePosixPath(path).parent.as_posix()}/**")
    return sorted(expanded)


def _operational_paths(slice_id: str, layer: str) -> list[str]:
    paths = [
        f"docs/opencode/plans/{slice_id}-plan.md",
        f"docs/opencode/checkpoints/{slice_id}-{layer}.json",
        f"docs/opencode/manifests/{slice_id}-{layer}.md",
    ]
    if layer == "backend":
        paths.extend(["backend/app/tests/**", "backend/tests/**"])
    elif layer == "frontend":
        paths.extend(["frontend/**/*.test.*", "frontend/**/*.spec.*"])
    elif layer == "qa":
        paths.extend(["docs/opencode/qa/**", "backend/app/tests/**"])
    elif layer == "ui-automation":
        paths.extend(
            [
                "InVet_UI_Automation/tests/e2e/**",
                f"docs/opencode/tasks/ui-automation/UIA-{slice_id[-3:]}.md",
            ]
        )
    elif layer == "api-automation":
        paths.extend(
            [
                "InVet_UI_Automation/tests/api/**",
                f"docs/opencode/tasks/api-automation/APIA-{slice_id[-3:]}.md",
            ]
        )
    return paths


def _load_plan(repo_root: Path, slice_id: str) -> tuple[Path, str, list[PlanTask]]:
    ids = normalize_slice_id(slice_id)
    path = repo_root / "docs/opencode/plans" / f"{ids.backend}-plan.md"
    text = path.read_text(encoding="utf-8")
    return path, text, _parse_tasks(text)


def _tasks_for_layer(tasks: list[PlanTask], layer: str) -> list[PlanTask]:
    prefix = PLAN_LAYER_PREFIX.get(layer)
    if prefix is None:
        return []
    return [task for task in tasks if task.task_id.startswith(f"{prefix}-")]


def _source_for_layer(repo_root: Path, index: str, layer: str) -> Path:
    mapping = {
        "backend": repo_root / f"docs/opencode/tasks/backend/BE-{index}.md",
        "frontend": repo_root / f"docs/opencode/tasks/frontend/FE-{index}.md",
        "qa": repo_root / f"docs/opencode/tasks/qa/QA-{index}.md",
        "ui-automation": repo_root
        / f"docs/opencode/tasks/ui-automation/UIA-{index}.md",
        "api-automation": repo_root
        / f"docs/opencode/tasks/api-automation/APIA-{index}.md",
    }
    return mapping[layer]


def _manifest_lines(
    repo_root: Path, slice_id: str, layer: str, tasks: list[PlanTask]
) -> list[str]:
    ids = normalize_slice_id(slice_id)
    source = _source_for_layer(repo_root, ids.index, layer)
    plan = repo_root / "docs/opencode/plans" / f"{ids.backend}-plan.md"
    allowlist = sorted(
        {
            path
            for task in tasks
            for path in _paths_from_deliverables(repo_root, task)
        }
        | set(_operational_paths(ids.backend, layer))
    )
    docker_controls: list[str] = []
    if layer in {"ui-automation", "api-automation"}:
        docker_controls = [
            "## Entorno Docker obligatorio",
            "",
            "- El sistema bajo prueba es `db`, `backend` y `frontend` de Docker Compose.",
            "- Docker ausente o un servicio no disponible produce `BLOCKED`; no existe fallback host.",
        ]
        if layer == "ui-automation":
            docker_controls.append(
                "- Ejecutar Playwright con `PLAYWRIGHT_START_FRONTEND=false` contra el frontend publicado."
            )
        else:
            docker_controls.append(
                "- Ejecutar Playwright API contra el backend publicado por Docker."
            )
        docker_controls.append("")
    lines = [
        "---",
        "manifest_version: 1",
        f"slice: \"{ids.index}\"",
        f"layer: {layer}",
        f"generated_at: {_now()}",
        f"source_plan: docs/opencode/plans/{ids.backend}-plan.md",
        f"source_plan_sha256: {_file_sha256(plan)}",
        f"source_task: {source.relative_to(repo_root).as_posix()}",
        f"source_task_sha256: {_file_sha256(source) if source.exists() else 'MISSING'}",
        "---",
        "",
        f"# {ids.backend} - manifiesto compacto {layer}",
        "",
        "## Uso",
        "",
        "- Este archivo es el contexto operativo de la capa; el plan completo queda como fuente canonica.",
        "- Ejecutar una tarea a la vez y cerrar con `finish --result pass|failed|blocked`; solo `pass` completa el checkpoint.",
        "- Ejecutar comandos, pruebas y logs directamente en el agente activo; no iniciar subagentes.",
        "- Estados visibles: leyendo, editando, ejecutando pruebas, esperando permiso, generacion cancelada.",
        "- Tiempo maximo por generacion: 30 minutos. Sin actividad del proveedor por 3 minutos, cancelar y conservar checkpoint.",
        "",
        *docker_controls,
        "## Fuente de capa",
        "",
        f"- Estado: {'DISPONIBLE' if source.exists() else 'FALTANTE'}",
        f"- Archivo: `{source.relative_to(repo_root).as_posix()}`",
        "",
        "## Archivos permitidos",
        "",
    ]
    lines.extend(f"- `{path}`" for path in allowlist)
    lines.extend(["", "## Tareas", ""])
    if not tasks:
        lines.extend(
            [
                "- No hay tareas atomicas de esta capa en el plan canonico.",
                "- El agente debe bloquear la implementacion si el sidecar de la capa esta FALTANTE.",
            ]
        )
    for task in tasks:
        lines.extend(
            [
                f"### {task.task_id} - {'COMPLETADA' if task.done else 'PENDIENTE'}",
                f"- Tipo: {task.fields.get('tipo', 'missing')}",
                f"- Criterio: {task.fields.get('historia o criterio', 'missing')}",
                f"- Objetivo: {task.fields.get('objetivo', 'missing')}",
                f"- Depende de: {task.fields.get('depende de', 'missing')}",
                f"- Contexto: {task.fields.get('contexto necesario', 'missing')}",
                f"- Contratos: {task.fields.get('contratos usados', 'missing')}",
                f"- Entregables: {task.fields.get('entregables', 'missing')}",
                f"- Aceptacion: {task.fields.get('criterios de aceptacion', 'missing')}",
                f"- Validacion: {task.fields.get('validacion', 'missing')}",
                f"- Resultado: {task.fields.get('resultado esperado', 'missing')}",
                "",
            ]
        )
    if len(lines) < 94 and source.exists():
        lines.extend(["## Brief de capa", ""])
        for source_line in source.read_text(encoding="utf-8").splitlines():
            stripped = source_line.strip()
            if not stripped or stripped.startswith("# "):
                continue
            lines.append(stripped)
            if len(lines) >= 94:
                break
    lines.extend(
        [
            "## Controles de cierre",
            "",
            "- Ningun archivo fuera de la allowlist cambio durante la tarea.",
            "- No se eliminaron archivos ni lineas existentes sin justificacion explicita.",
            "- Los registros `include_router(...)` existentes permanecen presentes.",
            "- La validacion declarada fue ejecutada y su evidencia quedo en el checkpoint.",
            "- El plan canonico se actualizo solo despues de verificar la tarea.",
        ]
    )
    return lines


def generate_manifests(repo_root: Path, slice_id: str, layer: str) -> list[Path]:
    ids = normalize_slice_id(slice_id)
    _, _, all_tasks = _load_plan(repo_root, ids.backend)
    layers = LAYERS if layer == "all" else (layer,)
    output_dir = repo_root / "docs/opencode/manifests"
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for current_layer in layers:
        tasks = _tasks_for_layer(all_tasks, current_layer)
        lines = _manifest_lines(repo_root, ids.backend, current_layer, tasks)
        path = output_dir / f"{ids.backend}-{current_layer}.md"
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        written.append(path)
    return written


def _manifest_metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Frontmatter ausente: {path}")
    frontmatter = text.split("---", 2)[1]
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def verify_manifests(repo_root: Path, slice_id: str, layer: str) -> list[str]:
    ids = normalize_slice_id(slice_id)
    layers = LAYERS if layer == "all" else (layer,)
    errors: list[str] = []
    plan = repo_root / "docs/opencode/plans" / f"{ids.backend}-plan.md"
    if not plan.exists():
        return [f"Plan canonico faltante: {plan.relative_to(repo_root)}"]
    plan_hash = _file_sha256(plan)
    for current_layer in layers:
        manifest = (
            repo_root / "docs/opencode/manifests" / f"{ids.backend}-{current_layer}.md"
        )
        source = _source_for_layer(repo_root, ids.index, current_layer)
        if not source.exists():
            errors.append(
                f"Sidecar faltante para {current_layer}: {source.relative_to(repo_root)}"
            )
            continue
        if not manifest.exists():
            errors.append(f"Manifiesto faltante: {manifest.relative_to(repo_root)}")
            continue
        try:
            metadata = _manifest_metadata(manifest)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        expected = {
            "manifest_version": "1",
            "slice": ids.index,
            "layer": current_layer,
            "source_plan": f"docs/opencode/plans/{ids.backend}-plan.md",
            "source_plan_sha256": plan_hash,
            "source_task": source.relative_to(repo_root).as_posix(),
            "source_task_sha256": _file_sha256(source),
        }
        for key, value in expected.items():
            if metadata.get(key) != value:
                errors.append(
                    f"Manifiesto stale/invalido {manifest.relative_to(repo_root)}: "
                    f"{key}={metadata.get(key)!r}, esperado={value!r}"
                )
    return errors


def _checkpoint_path(repo_root: Path, slice_id: str, layer: str) -> Path:
    return repo_root / "docs/opencode/checkpoints" / f"{slice_id}-{layer}.json"


def _runtime_path(repo_root: Path, task_id: str) -> Path:
    return repo_root / ".opencode/runtime" / f"{task_id}.json"


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def _snapshot(repo_root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in repo_root.rglob("*"):
        if not path.is_file() or _is_ignored(path.relative_to(repo_root)):
            continue
        relative = path.relative_to(repo_root).as_posix()
        if relative.startswith(".opencode/runtime/"):
            continue
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _router_invariants(repo_root: Path) -> dict[str, list[str]]:
    invariants: dict[str, list[str]] = {}
    for path in repo_root.rglob("*.py"):
        if _is_ignored(path.relative_to(repo_root)):
            continue
        values = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = ROUTER_RE.search(line.strip())
            if match:
                values.append(re.sub(r"\s+", "", match.group(0)))
        if values:
            invariants[path.relative_to(repo_root).as_posix()] = sorted(set(values))
    return invariants


def _matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        return path.startswith(pattern[:-3].rstrip("/"))
    return PurePosixPath(path).match(pattern) or path == pattern


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def start_task(repo_root: Path, slice_id: str, task_id: str) -> dict:
    ids = normalize_slice_id(slice_id)
    _, _, tasks = _load_plan(repo_root, ids.backend)
    normalized_task_id = task_id.upper()
    task = next((item for item in tasks if item.task_id == normalized_task_id), None)
    if task is not None:
        layer = task.fields.get("capa", "").lower()
        if layer not in PLAN_LAYER_PREFIX:
            raise ValueError(f"Capa no soportada para {task.task_id}: {layer}")
        allowlist = sorted(
            set(_paths_from_deliverables(repo_root, task))
            | set(_operational_paths(ids.backend, layer))
        )
    else:
        automation_match = re.fullmatch(r"(UIA|APIA)-(\d{3})", normalized_task_id)
        if not automation_match or automation_match.group(2) != ids.index:
            raise ValueError(f"Tarea o fase inexistente: {task_id}")
        layer = AUTOMATION_LAYER_PREFIX[automation_match.group(1)]
        source = _source_for_layer(repo_root, ids.index, layer)
        if not source.exists():
            raise ValueError(f"Sidecar faltante: {source.relative_to(repo_root)}")
        allowlist = sorted(set(_operational_paths(ids.backend, layer)))
    baseline_hashes = _snapshot(repo_root)
    baseline_contents = {}
    for relative_path in baseline_hashes:
        if not any(_matches(relative_path, pattern) for pattern in allowlist):
            continue
        path = repo_root / relative_path
        try:
            baseline_contents[relative_path] = path.read_text(
                encoding="utf-8", errors="strict"
            )
        except (OSError, UnicodeError):
            # Binary or unreadable files remain protected by their snapshot hash.
            continue
    runtime = {
        "slice": ids.backend,
        "task": task.task_id if task is not None else normalized_task_id,
        "layer": layer,
        "state": "reading",
        "state_label": STATES["reading"],
        "started_at": _now(),
        "updated_at": _now(),
        "allowed_files": allowlist,
        "baseline_hashes": baseline_hashes,
        "baseline_contents": baseline_contents,
        "router_invariants": _router_invariants(repo_root),
    }
    _write_json(_runtime_path(repo_root, runtime["task"]), runtime)
    return runtime


def set_state(repo_root: Path, task_id: str, state: str, note: str = "") -> dict:
    path = _runtime_path(repo_root, task_id.upper())
    runtime = _read_json(path)
    runtime.update(
        {
            "state": state,
            "state_label": STATES[state],
            "note": note,
            "updated_at": _now(),
        }
    )
    _write_json(path, runtime)
    return runtime


def _removed_lines(before: str, after: str) -> list[str]:
    return [
        line[1:]
        for line in difflib.ndiff(before.splitlines(), after.splitlines())
        if line.startswith("- ") and line[2:].strip()
    ]


def finish_task(
    repo_root: Path,
    task_id: str,
    evidence: str,
    deletion_justification: str,
    outcome: str = "pass",
) -> tuple[dict, list[str]]:
    runtime_path = _runtime_path(repo_root, task_id.upper())
    runtime = _read_json(runtime_path)
    current = _snapshot(repo_root)
    baseline = runtime["baseline_hashes"]
    changed = sorted(
        path
        for path in set(baseline) | set(current)
        if baseline.get(path) != current.get(path)
        and not path.startswith(".opencode/runtime/")
    )
    errors: list[str] = []
    for path in changed:
        if not any(_matches(path, pattern) for pattern in runtime["allowed_files"]):
            errors.append(f"Archivo fuera de Entregables/allowlist: {path}")
    deleted_files = sorted(path for path in baseline if path not in current)
    if deleted_files and not deletion_justification:
        errors.append("Archivos existentes eliminados sin justificacion: " + ", ".join(deleted_files))
    removed: dict[str, list[str]] = {}
    for path, before in runtime.get("baseline_contents", {}).items():
        current_path = repo_root / path
        if current_path.is_file():
            lines = _removed_lines(
                before,
                current_path.read_text(encoding="utf-8", errors="replace"),
            )
            if lines:
                removed[path] = lines[:20]
    if removed and not deletion_justification:
        errors.append(
            "Lineas existentes eliminadas sin justificacion: "
            + ", ".join(f"{path} ({len(lines)})" for path, lines in removed.items())
        )
    current_routers = _router_invariants(repo_root)
    lost_routers: list[str] = []
    for path, registrations in runtime.get("router_invariants", {}).items():
        missing = sorted(set(registrations) - set(current_routers.get(path, [])))
        lost_routers.extend(f"{path}: {item}" for item in missing)
    if lost_routers:
        errors.append("Invariantes de router eliminados: " + "; ".join(lost_routers))

    if outcome == "failed":
        errors.append("La validacion o las pruebas de la tarea fallaron.")
    elif outcome == "blocked":
        errors.append("La tarea quedo bloqueada por entorno, dependencia o permiso.")

    checkpoint_path = _checkpoint_path(
        repo_root, runtime["slice"], runtime["layer"]
    )
    checkpoint = _read_json(checkpoint_path) if checkpoint_path.exists() else {
        "slice": runtime["slice"],
        "layer": runtime["layer"],
        "tasks": {},
    }
    if not errors:
        final_state = "completed"
    elif outcome == "blocked":
        final_state = "blocked"
    elif outcome == "failed":
        final_state = "failed"
    else:
        final_state = "cancelled"
    checkpoint["tasks"][runtime["task"]] = {
        "state": final_state,
        "state_label": STATES[final_state],
        "started_at": runtime["started_at"],
        "finished_at": _now(),
        "evidence": evidence,
        "outcome": outcome,
        "changed_files": changed,
        "deletion_justification": deletion_justification,
        "errors": errors,
    }
    checkpoint["updated_at"] = _now()
    _write_json(checkpoint_path, checkpoint)
    runtime.update(
        {"state": final_state, "state_label": STATES[final_state], "errors": errors}
    )
    _write_json(runtime_path, runtime)
    return checkpoint, errors


def main() -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    subparsers = parser.add_subparsers(dest="command", required=True)

    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("slice_id")
    manifest.add_argument("--layer", choices=("all",) + LAYERS, default="all")

    verify = subparsers.add_parser("verify")
    verify.add_argument("slice_id")
    verify.add_argument("--layer", choices=("all",) + LAYERS, default="all")

    start = subparsers.add_parser("start")
    start.add_argument("slice_id")
    start.add_argument("--task", required=True)

    state = subparsers.add_parser("state")
    state.add_argument("--task", required=True)
    state.add_argument("--set", choices=tuple(STATES), required=True, dest="new_state")
    state.add_argument("--note", default="")

    finish = subparsers.add_parser("finish")
    finish.add_argument("--task", required=True)
    finish.add_argument("--evidence", required=True)
    finish.add_argument(
        "--result", choices=("pass", "failed", "blocked"), default="pass"
    )
    finish.add_argument("--allow-deletions", default="", dest="deletion_justification")

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        if args.command == "manifest":
            paths = generate_manifests(repo_root, args.slice_id, args.layer)
            for path in paths:
                line_count = len(path.read_text(encoding="utf-8").splitlines())
                print(f"[MANIFIESTO] {path.relative_to(repo_root)} ({line_count} lineas)")
        elif args.command == "verify":
            errors = verify_manifests(repo_root, args.slice_id, args.layer)
            if errors:
                for error in errors:
                    print(f"[ERROR] {error}")
                return 1
            print(f"[PASS] manifiestos coherentes para {normalize_slice_id(args.slice_id).backend}")
        elif args.command == "start":
            runtime = start_task(repo_root, args.slice_id, args.task)
            print(f"[ESTADO] {runtime['state_label']} | {runtime['task']}")
            print("[ALLOWLIST] " + ", ".join(runtime["allowed_files"]))
        elif args.command == "state":
            runtime = set_state(repo_root, args.task, args.new_state, args.note)
            print(f"[ESTADO] {runtime['state_label']} | {runtime['task']}")
        elif args.command == "finish":
            checkpoint, errors = finish_task(
                repo_root,
                args.task,
                args.evidence,
                args.deletion_justification,
                args.result,
            )
            task = checkpoint["tasks"][args.task.upper()]
            print(f"[ESTADO] {task['state_label']} | {args.task.upper()}")
            for error in errors:
                print(f"- {error}")
            return 1 if errors else 0
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
