from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_automation_flow_is_wired_into_agentic_contracts() -> None:
    planner_agent = (REPO_ROOT / ".opencode/agents/invet-product-planner.md").read_text(
        encoding="utf-8"
    )
    orchestrator = (REPO_ROOT / ".opencode/agents/invet-orchestrator.md").read_text(
        encoding="utf-8"
    )
    execute_slice = (REPO_ROOT / ".opencode/commands/execute-slice.md").read_text(
        encoding="utf-8"
    )
    plan_task = (REPO_ROOT / ".opencode/commands/plan-task.md").read_text(
        encoding="utf-8"
    )
    qa_task = (REPO_ROOT / ".opencode/commands/qa-task.md").read_text(encoding="utf-8")
    prompt_contracts = (
        REPO_ROOT / "docs/opencode/03_task_prompt_contracts.md"
    ).read_text(encoding="utf-8")
    qa_results_template = (
        REPO_ROOT / "docs/opencode/templates/qa_results_template.md"
    ).read_text(encoding="utf-8")
    qa_findings_template = (
        REPO_ROOT / "docs/opencode/templates/qa_findings_template.md"
    ).read_text(encoding="utf-8")

    assert "US-00X-NN" in planner_agent
    assert "UIA-00X" in planner_agent
    assert "APIA-00X" in planner_agent
    assert "/implement-ui-automation-task BE-00X" in orchestrator
    assert "/implement-api-automation-task BE-00X" in orchestrator
    assert "/run-ui-checks BE-00X" in orchestrator
    assert "/implement-ui-automation-task BE-00X" in execute_slice
    assert "/implement-api-automation-task BE-00X" in execute_slice
    assert "docs/opencode/tasks/user-stories/US-00X.md" in plan_task
    assert "docs/opencode/tasks/ui-automation/UIA-00X.md" in plan_task
    assert "docs/opencode/tasks/api-automation/APIA-00X.md" in plan_task
    assert "/implement-ui-automation-task BE-00X|FE-00X|QA-00X" in prompt_contracts
    assert "/implement-api-automation-task BE-00X" in prompt_contracts
    assert "/run-ui-checks BE-00X|FE-00X|QA-00X" in prompt_contracts
    assert (
        "contenedores Docker aplicables fueron actualizados o recreados"
        in prompt_contracts
    )
    assert (
        "todos los contenedores Docker aplicables fueron actualizados o recreados"
        in qa_task
    )
    assert "## Verificacion Docker" in qa_results_template
    assert "## Verificacion Docker" in qa_findings_template
    assert "Contenedores aplicables actualizados o recreados" in qa_results_template
    assert "Contenedores aplicables actualizados o recreados" in qa_findings_template


def test_ui_and_api_automation_require_the_docker_stack() -> None:
    ui_command = (
        REPO_ROOT / ".opencode/commands/implement-ui-automation-task.md"
    ).read_text(encoding="utf-8")
    api_command = (
        REPO_ROOT / ".opencode/commands/implement-api-automation-task.md"
    ).read_text(encoding="utf-8")
    ui_checks = (REPO_ROOT / ".opencode/commands/run-ui-checks.md").read_text(
        encoding="utf-8"
    )
    checks = (REPO_ROOT / ".opencode/commands/run-checks.md").read_text(
        encoding="utf-8"
    )
    qa = (REPO_ROOT / ".opencode/commands/qa-task.md").read_text(encoding="utf-8")
    playwright = (REPO_ROOT / "InVet_UI_Automation/playwright.config.ts").read_text(
        encoding="utf-8"
    )

    for contract in (ui_command, api_command, ui_checks):
        assert "`db`, `backend` y `frontend`" in contract
        assert "BLOCKED" in contract
    assert "PLAYWRIGHT_START_FRONTEND=false" in ui_command
    assert "PLAYWRIGHT_START_FRONTEND=false" in ui_checks
    assert "npm run test:api" in checks
    assert "Evidencia host" in qa
    assert 'startFrontendSetting === "undefined"' not in playwright
    assert "startFrontendSetting === undefined" in playwright


def test_automation_recommendations_preserve_phase_ownership() -> None:
    ui_command = (
        REPO_ROOT / ".opencode/commands/implement-ui-automation-task.md"
    ).read_text(encoding="utf-8")
    api_command = (
        REPO_ROOT / ".opencode/commands/implement-api-automation-task.md"
    ).read_text(encoding="utf-8")
    ui_checks = (REPO_ROOT / ".opencode/commands/run-ui-checks.md").read_text(
        encoding="utf-8"
    )

    assert "recomienda `/implement-api-automation-task BE-00X`" in ui_command
    assert "recomienda `/qa-task QA-00X`" in api_command
    assert "`APPROVED` recomienda `/run-checks BE-00X`" in ui_checks
    assert "`BLOCKED` conserva evidencia" in ui_checks


def test_automation_contracts_are_in_sync_with_payload() -> None:
    pairs = [
        (
            REPO_ROOT / ".opencode/agents/invet-product-planner.md",
            REPO_ROOT / "payload/.opencode/agents/invet-product-planner.md",
        ),
        (
            REPO_ROOT / ".opencode/agents/invet-orchestrator.md",
            REPO_ROOT / "payload/.opencode/agents/invet-orchestrator.md",
        ),
        (
            REPO_ROOT / ".opencode/agents/invet-ui-automation-implementer.md",
            REPO_ROOT / "payload/.opencode/agents/invet-ui-automation-implementer.md",
        ),
        (
            REPO_ROOT / ".opencode/agents/invet-api-automation-implementer.md",
            REPO_ROOT / "payload/.opencode/agents/invet-api-automation-implementer.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/plan-task.md",
            REPO_ROOT / "payload/.opencode/commands/plan-task.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/execute-slice.md",
            REPO_ROOT / "payload/.opencode/commands/execute-slice.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/implement-ui-automation-task.md",
            REPO_ROOT / "payload/.opencode/commands/implement-ui-automation-task.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/implement-api-automation-task.md",
            REPO_ROOT / "payload/.opencode/commands/implement-api-automation-task.md",
        ),
        (
            REPO_ROOT / ".opencode/commands/run-ui-checks.md",
            REPO_ROOT / "payload/.opencode/commands/run-ui-checks.md",
        ),
        (
            REPO_ROOT / "docs/opencode/01_command_runbook.md",
            REPO_ROOT / "payload/docs/opencode/01_command_runbook.md",
        ),
        (
            REPO_ROOT / "docs/opencode/README.md",
            REPO_ROOT / "payload/docs/opencode/README.md",
        ),
        (
            REPO_ROOT / "docs/opencode/02_be_fe_qa_task_matrix.md",
            REPO_ROOT / "payload/docs/opencode/02_be_fe_qa_task_matrix.md",
        ),
        (
            REPO_ROOT / "docs/opencode/03_task_prompt_contracts.md",
            REPO_ROOT / "payload/docs/opencode/03_task_prompt_contracts.md",
        ),
        (
            REPO_ROOT / "docs/opencode/04_agent_contracts.md",
            REPO_ROOT / "payload/docs/opencode/04_agent_contracts.md",
        ),
        (
            REPO_ROOT / "docs/opencode/05_done_gates_by_command.md",
            REPO_ROOT / "payload/docs/opencode/05_done_gates_by_command.md",
        ),
        (
            REPO_ROOT / "docs/opencode/11_chatgpt_project_context.md",
            REPO_ROOT / "payload/docs/opencode/11_chatgpt_project_context.md",
        ),
        (
            REPO_ROOT / "docs/opencode/13_agents_architecture_and_gate_flow.md",
            REPO_ROOT / "payload/docs/opencode/13_agents_architecture_and_gate_flow.md",
        ),
        (
            REPO_ROOT / "docs/opencode/14_github_copilot_agentic_flow.md",
            REPO_ROOT / "payload/docs/opencode/14_github_copilot_agentic_flow.md",
        ),
        (
            REPO_ROOT / "docs/opencode/15_operational_manifests_flow.md",
            REPO_ROOT / "payload/docs/opencode/15_operational_manifests_flow.md",
        ),
        (
            REPO_ROOT / "docs/opencode/references/carryovers_governance.md",
            REPO_ROOT / "payload/docs/opencode/references/carryovers_governance.md",
        ),
        (
            REPO_ROOT / "docs/opencode/templates/carryovers_registry_template.md",
            REPO_ROOT
            / "payload/docs/opencode/templates/carryovers_registry_template.md",
        ),
    ]

    for primary, payload in pairs:
        assert primary.read_text(encoding="utf-8") == payload.read_text(
            encoding="utf-8"
        )


def test_automation_workspace_scaffold_exists() -> None:
    required_paths = [
        REPO_ROOT / "InVet_UI_Automation/package.json",
        REPO_ROOT / "InVet_UI_Automation/playwright.config.ts",
        REPO_ROOT
        / "InVet_UI_Automation/.opencode/agents/invet-ui-automation-implementer.md",
        REPO_ROOT
        / "InVet_UI_Automation/.opencode/agents/invet-api-automation-implementer.md",
        REPO_ROOT / "InVet_UI_Automation/tests/e2e/auth/login.spec.ts",
        REPO_ROOT / "InVet_UI_Automation/tests/api/auth/login.spec.ts",
        REPO_ROOT / "docs/opencode/tasks/user-stories/README.md",
        REPO_ROOT / "docs/opencode/tasks/ui-automation/README.md",
        REPO_ROOT / "docs/opencode/tasks/api-automation/README.md",
    ]

    for path in required_paths:
        assert path.exists(), f"Missing required automation artifact: {path}"


def test_agentic_runtime_uses_direct_execution_and_safety_controls() -> None:
    config = json.loads((REPO_ROOT / "opencode.json").read_text(encoding="utf-8"))
    agent_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / ".opencode/agents").glob("*.md")
    )
    command_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / ".opencode/commands").glob("*.md")
    )

    assert config["permission"]["task"] == "deny"
    assert config["permission"]["doom_loop"] == "deny"
    assert config["permission"]["bash"]["git status*"] == "allow"
    assert config["permission"]["bash"]["git commit*"] == "ask"
    assert (
        config["permission"]["bash"][
            "docker compose up -d --build db backend frontend*"
        ]
        == "allow"
    )
    assert "invet-command-executor" not in agent_text
    assert "invet-command-executor" not in command_text
    assert "manage_slice_task.py" in command_text
    assert "state --set" in command_text


def test_manifest_flow_preserves_agent_responsibilities_and_be_alias() -> None:
    commands = {
        path.stem: path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / ".opencode/commands").glob("*.md")
    }
    planner = (REPO_ROOT / ".opencode/agents/invet-product-planner.md").read_text(
        encoding="utf-8"
    )
    orchestrator = (REPO_ROOT / ".opencode/agents/invet-orchestrator.md").read_text(
        encoding="utf-8"
    )

    required = {
        "plan-task",
        "implement-backend-task",
        "implement-frontend-task",
        "implement-ui-automation-task",
        "implement-api-automation-task",
        "qa-task",
        "review-slice",
        "clean-architecture-review",
        "security-review",
        "run-ui-checks",
        "run-checks",
        "update-docs",
        "final-gate",
        "execute-slice",
    }
    assert required <= commands.keys()
    assert "propietario semantico" in commands["plan-task"]
    assert "manifest BE-00X --layer all" in commands["plan-task"]
    assert "verify BE-00X --layer all" in commands["plan-task"]
    for name in (
        "implement-frontend-task",
        "implement-ui-automation-task",
        "implement-api-automation-task",
        "run-ui-checks",
    ):
        assert "`BE-00X`, `FE-00X` o `QA-00X`" in commands[name]
    assert "`/final-gate BE-00X`" in commands["execute-slice"]
    assert "unico propietario semantico" in planner
    assert "manifiesto" in orchestrator.lower()
    assert "nunca sustituye evidencia real" in orchestrator
