"""Bootstrap a local QA environment for InVet test execution."""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path

REQUIRED_MODULES = (
    "fastapi",
    "sqlalchemy",
    "pydantic",
    "pydantic_settings",
    "pytest",
    "httpx",
    "ruff",
    "black",
    "mypy",
    "jose",
    "passlib",
)

DEFAULT_QA_ENV = {
    "PROJECT_NAME": "InVet",
    "API_V1_STR": "/api/v1",
    "DATABASE_URL": "sqlite:///./qa-test.db",
    "SECRET_KEY": "qa-test-secret-key",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
}


def backend_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    return backend_root().parent


def qa_env_path() -> Path:
    return backend_root() / ".env.qa"


def find_missing_modules() -> list[str]:
    missing: list[str] = []
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            missing.append(module_name)
    return missing


def install_dependencies() -> None:
    editable_command = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]
    requirements_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        "requirements.txt",
    ]

    if _run_command(editable_command, cwd=backend_root()).returncode == 0:
        return

    result = _run_command(requirements_command, cwd=backend_root())
    if result.returncode != 0:
        raise RuntimeError("No fue posible instalar las dependencias de backend.")


def ensure_qa_env_file() -> tuple[Path, str]:
    env_path = qa_env_path()
    existing_values = _read_env_file(env_path)
    merged_values = {**DEFAULT_QA_ENV, **existing_values}

    action = "unchanged"
    if not env_path.exists():
        action = "created"
    elif merged_values != existing_values:
        action = "updated"

    if action != "unchanged":
        contents = "\n".join(f"{key}={value}" for key, value in merged_values.items())
        env_path.write_text(contents + "\n", encoding="utf-8")

    return env_path, action


def validate_database_connectivity() -> str:
    validation_script = (
        "from sqlalchemy import text\n"
        "from app.core.config import settings\n"
        "from app.infrastructure.database.session import SessionLocal\n"
        "session = SessionLocal()\n"
        "session.execute(text('SELECT 1'))\n"
        "session.close()\n"
        "print(settings.DATABASE_URL)\n"
    )
    result = _run_command(
        [sys.executable, "-c", validation_script],
        cwd=backend_root(),
    )
    if result.returncode != 0:
        raise RuntimeError("No fue posible validar una base de datos utilizable.")

    return result.stdout.strip().splitlines()[-1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepara un entorno local de QA para InVet."
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Instala dependencias si faltan en el interprete actual.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Valida el entorno sin instalar dependencias faltantes.",
    )
    args = parser.parse_args()

    print(f"Repo root: {repo_root()}")
    print(f"Backend root: {backend_root()}")
    print(f"Python: {sys.executable}")

    missing_modules = find_missing_modules()
    if missing_modules:
        print("Missing modules:", ", ".join(missing_modules))
        if args.validate_only:
            return 1
        if not args.install_deps:
            print("Use --install-deps para instalar dependencias antes de ejecutar QA.")
            return 1

        print("Installing backend dependencies...")
        install_dependencies()
        missing_modules = find_missing_modules()
        if missing_modules:
            print("Still missing modules:", ", ".join(missing_modules))
            return 1
    else:
        print("Python dependencies: OK")

    env_path, env_action = ensure_qa_env_file()
    print(f"QA env file: {env_action} -> {env_path}")

    database_url = validate_database_connectivity()
    print(f"Database connectivity: OK -> {database_url}")
    print("QA environment is ready.")
    return 0


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
