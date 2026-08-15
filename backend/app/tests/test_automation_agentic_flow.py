from __future__ import annotations

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
    qa_task = (REPO_ROOT / ".opencode/commands/qa-task.md").read_text(
        encoding="utf-8"
    )
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
    assert "/implement-ui-automation-task FE-00X" in orchestrator
    assert "/implement-api-automation-task BE-00X" in orchestrator
    assert "/run-ui-checks FE-00X" in orchestrator
    assert "/implement-ui-automation-task FE-00X" in execute_slice
    assert "/implement-api-automation-task BE-00X" in execute_slice
    assert "docs/opencode/tasks/user-stories/US-00X.md" in plan_task
    assert "docs/opencode/tasks/ui-automation/UIA-00X.md" in plan_task
    assert "docs/opencode/tasks/api-automation/APIA-00X.md" in plan_task
    assert "/implement-ui-automation-task FE-00X" in prompt_contracts
    assert "/implement-api-automation-task BE-00X" in prompt_contracts
    assert "/run-ui-checks FE-00X" in prompt_contracts
    assert "contenedores Docker aplicables fueron actualizados o recreados" in prompt_contracts
    assert "todos los contenedores Docker aplicables fueron actualizados o recreados" in qa_task
    assert "## Verificacion Docker" in qa_results_template
    assert "## Verificacion Docker" in qa_findings_template
    assert "Contenedores aplicables actualizados o recreados" in qa_results_template
    assert "Contenedores aplicables actualizados o recreados" in qa_findings_template


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
            REPO_ROOT / "docs/opencode/references/carryovers_governance.md",
            REPO_ROOT / "payload/docs/opencode/references/carryovers_governance.md",
        ),
        (
            REPO_ROOT / "docs/opencode/templates/carryovers_registry_template.md",
            REPO_ROOT / "payload/docs/opencode/templates/carryovers_registry_template.md",
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
