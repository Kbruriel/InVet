#!/usr/bin/env python3
"""Validate the OpenCode/GitHub agent catalog and its distributable mirror."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "opencode" / "agent_registry.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        item = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if item:
            result[item.group(1)] = item.group(2)
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fenced_inventory(text: str, heading: str) -> set[str]:
    pattern = rf"## {re.escape(heading)}\s+```text\s+(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return set()
    return {
        line.strip().removeprefix("/")
        for line in match.group(1).splitlines()
        if line.strip()
    }


def main() -> int:
    errors: list[str] = []
    registry = json.loads(read_text(REGISTRY_PATH))
    policy = registry["execution_policy"]
    agents = registry["agents"]

    expected_agents = {item["id"] for item in agents}
    expected_commands = {
        command: item for item in agents for command in item["commands"]
    }

    if policy != {
        "delegation": False,
        "complete_flow_agent": "invet-orchestrator",
        "manual_command_profile": True,
        "opencode_mode": "primary",
        "command_subtask": False,
        "github_permission_parity": "semantic",
    }:
        errors.append("agent_registry.json has an unsupported execution policy")

    opencode_agents = ROOT / ".opencode" / "agents"
    actual_agents = {path.stem for path in opencode_agents.glob("*.md")}
    if actual_agents != expected_agents:
        errors.append(
            f"OpenCode agents differ: missing={sorted(expected_agents - actual_agents)}, "
            f"extra={sorted(actual_agents - expected_agents)}"
        )

    for item in agents:
        path = opencode_agents / f"{item['id']}.md"
        if not path.exists():
            continue
        metadata = frontmatter(path)
        if metadata.get("mode") != policy["opencode_mode"]:
            errors.append(f"{path.relative_to(ROOT)} must use mode: primary")
        if not re.search(r"(?m)^\s{2}task:\s*deny\s*$", read_text(path)):
            errors.append(f"{path.relative_to(ROOT)} must deny task delegation")

    orchestrator = read_text(opencode_agents / f"{policy['complete_flow_agent']}.md")
    if not re.search(r"(?m)^\s{2}edit:\s*allow\s*$", orchestrator):
        errors.append("the complete-flow agent must allow in-scope edits")
    for command_pattern in (
        "python -m pytest*",
        "npm run test*",
        "npx playwright*",
        "docker compose up -d --build db backend frontend*",
        "git diff*",
    ):
        if f'    "{command_pattern}": allow' not in orchestrator:
            errors.append(
                f"the complete-flow agent is missing safe command {command_pattern!r}"
            )

    opencode_commands = ROOT / ".opencode" / "commands"
    actual_commands = {path.stem for path in opencode_commands.glob("*.md")}
    if actual_commands != set(expected_commands):
        errors.append(
            f"OpenCode commands differ: missing={sorted(set(expected_commands) - actual_commands)}, "
            f"extra={sorted(actual_commands - set(expected_commands))}"
        )

    for command, item in expected_commands.items():
        path = opencode_commands / f"{command}.md"
        if not path.exists():
            continue
        metadata = frontmatter(path)
        if metadata.get("agent") != item["id"]:
            errors.append(
                f"{path.relative_to(ROOT)} points to {metadata.get('agent')!r}"
            )
        if metadata.get("subtask") != "false":
            errors.append(f"{path.relative_to(ROOT)} must declare subtask: false")

    github_agents = ROOT / ".github" / "agents"
    actual_github_agents = {
        path.name.removesuffix(".agent.md") for path in github_agents.glob("*.agent.md")
    }
    if actual_github_agents != expected_agents:
        errors.append(
            f"GitHub agents differ: missing={sorted(expected_agents - actual_github_agents)}, "
            f"extra={sorted(actual_github_agents - expected_agents)}"
        )

    for item in agents:
        path = github_agents / f"{item['id']}.agent.md"
        if not path.exists():
            continue
        metadata = frontmatter(path)
        if metadata.get("name") != item["github_name"]:
            errors.append(f"{path.relative_to(ROOT)} has an unexpected display name")
        try:
            tools = set(ast.literal_eval(metadata.get("tools", "[]")))
        except (SyntaxError, ValueError):
            tools = set()
        if tools != {"read", "search", "edit", "execute"}:
            errors.append(
                f"{path.relative_to(ROOT)} has unexpected tools: {sorted(tools)}"
            )
        if "agent" in tools:
            errors.append(f"{path.relative_to(ROOT)} enables agent delegation")

    github_prompts = ROOT / ".github" / "prompts"
    actual_prompts = {
        path.name.removesuffix(".prompt.md")
        for path in github_prompts.glob("*.prompt.md")
    }
    if actual_prompts != set(expected_commands):
        errors.append(
            f"GitHub prompts differ: missing={sorted(set(expected_commands) - actual_prompts)}, "
            f"extra={sorted(actual_prompts - set(expected_commands))}"
        )

    for command, item in expected_commands.items():
        path = github_prompts / f"{command}.prompt.md"
        if not path.exists():
            continue
        match = re.search(r"(?m)^Use agent: `([^`]+)`\.$", read_text(path))
        if not match or match.group(1) != item["github_name"]:
            errors.append(
                f"{path.relative_to(ROOT)} does not select {item['github_name']}"
            )

    manifest = read_text(ROOT / "docs" / "opencode" / "00_installation_manifest.md")
    manifest_commands = fenced_inventory(manifest, "Comandos instalados")
    manifest_agents = fenced_inventory(manifest, "Agentes instalados")
    if manifest_commands != set(expected_commands):
        errors.append("00_installation_manifest.md has a stale command inventory")
    if manifest_agents != expected_agents:
        errors.append("00_installation_manifest.md has a stale agent inventory")

    mirrored_directories = [
        Path(".opencode/agents"),
        Path(".opencode/commands"),
        Path(".github/agents"),
        Path(".github/prompts"),
    ]
    for relative_dir in mirrored_directories:
        source_dir = ROOT / relative_dir
        mirror_dir = ROOT / "payload" / relative_dir
        source_files = {path.name for path in source_dir.iterdir() if path.is_file()}
        mirror_files = {path.name for path in mirror_dir.iterdir() if path.is_file()}
        if source_files != mirror_files:
            errors.append(f"payload/{relative_dir} has a different file inventory")
            continue
        for name in sorted(source_files):
            if sha256(source_dir / name) != sha256(mirror_dir / name):
                errors.append(
                    f"payload/{relative_dir / name} differs from the active file"
                )

    mirrored_files = [
        Path(".github/copilot-instructions.md"),
        Path("opencode.json"),
        Path("docs/opencode/README.md"),
        Path("docs/opencode/00_installation_manifest.md"),
        Path("docs/opencode/04_agent_contracts.md"),
        Path("docs/opencode/13_agents_architecture_and_gate_flow.md"),
        Path("docs/opencode/14_github_copilot_agentic_flow.md"),
        Path("docs/opencode/agent_registry.json"),
        Path("backend/scripts/validate_agent_catalog.py"),
    ]
    for relative_path in mirrored_files:
        source = ROOT / relative_path
        mirror = ROOT / "payload" / relative_path
        if not mirror.exists():
            errors.append(f"payload/{relative_path} is missing")
        elif sha256(source) != sha256(mirror):
            errors.append(f"payload/{relative_path} differs from the active file")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print(
        f"[PASS] Agent catalog: {len(expected_agents)} agents, "
        f"{len(expected_commands)} commands, direct execution, payload synchronized."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
