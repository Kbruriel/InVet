# Codebase Memory MCP Implementation Plan

## Objective

Integrate `codebase-memory-mcp` into the InVet workflow as a local code memory layer for structural search, impact analysis, and review support, without replacing the existing OpenCode gates, tests, or manual code reading.

## Recommended route

Use a two-layer rollout:

1. Local workspace setup for the agent runtime.
2. InVet repo updates for agent guidance and operating contracts.

This keeps the tool usable for day-to-day work while avoiding product churn.

## Scope

### In scope

- Install `codebase-memory-mcp` locally and connect it to the agent environment.
- Configure the server so it indexes `C:\InVet`.
- Add a short operating contract to InVet docs that explains when the memory graph should be used.
- Update the OpenCode agents that benefit most from structural context.
- Define a small validation set of representative questions for InVet.
- Record a fallback path when the memory graph is missing or stale.

### Out of scope

- Changing InVet product behavior.
- Rewriting backend or frontend architecture.
- Replacing `rg`, file reads, tests, or QA gates.
- Adding telemetry, cloud sync, or external storage for code contents.

## Assumptions

- `codebase-memory-mcp` continues to run locally on the same machine as InVet.
- The tool can index the current workspace without requiring a remote service.
- The user wants the integration to help agents reason about callers, callees, routes, modules, and impact, not to become a source of product truth.

## Implementation phases

| Phase | Goal | Deliverables | Validation |
| --- | --- | --- | --- |
| 1 | Local setup | MCP server installed and pointing at `C:\InVet` | Server starts and returns the workspace graph |
| 2 | Repo contract | InVet docs explain when to use the memory layer | Docs mention the intended use and fallback rules |
| 3 | Agent wiring | Orchestrator, executor, and reviewers know when to consult the graph first | Agent prompts reflect the new priority order |
| 4 | Validation set | A short list of structural queries for InVet | Queries return consistent answers across runs |
| 5 | Rollout | Integration is stable enough for normal slice work | Memory graph helps without blocking normal flows |

## File change plan

### Local environment

- `C:\Users\Precision 7520\.config\opencode\opencode.jsonc`

Use this only if the local OpenCode installation is the agent entrypoint you want to keep using.

### InVet repo

- `C:\InVet\docs\opencode\11_chatgpt_project_context.md`
- `C:\InVet\docs\opencode\13_agents_architecture_and_gate_flow.md`
- `C:\InVet\.opencode\agents\invet-orchestrator.md`
- Agentes activos que ejecutan consultas estructurales directamente.
- `C:\InVet\.opencode\agents\invet-slice-reviewer.md`
- `C:\InVet\.opencode\agents\invet-qa-validator.md`
- `C:\InVet\.opencode\agents\invet-findings-implementer.md`

## Task breakdown

### T01 - Install and register the local memory server

Goal: make `codebase-memory-mcp` available to the local agent runtime.

Work:

- Install the server locally.
- Register the MCP entry in the local agent configuration.
- Point the indexer at `C:\InVet`.
- Confirm the graph builds without touching InVet product code.

Acceptance criteria:

- The server is visible to the local agent runtime.
- The workspace `C:\InVet` is indexed.
- A simple structural query returns useful results.

### T02 - Add an operating contract for InVet

Goal: document when agents should use the memory graph.

Work:

- Add a short section to `docs/opencode/11_chatgpt_project_context.md`.
- Explain the preferred use cases: callers, callees, routes, impact analysis, dead-code checks, and duplicate-module detection.
- Add the fallback rule: if the graph is stale or incomplete, fall back to `rg`, file reads, and existing gates.

Acceptance criteria:

- The docs tell agents when to use the tool and when not to.
- The docs do not replace existing checks or reviews.

### T03 - Update agent priorities

Goal: make the most relevant agents consult the graph first for structural questions.

Work:

- Update `invet-orchestrator` with the new routing rule.
- Update active agents with a direct structural-query workflow without subagents.
- Update `invet-slice-reviewer` and `invet-qa-validator` to use the memory graph for impact and coverage questions.
- Keep the existing fallback to standard file search.

Acceptance criteria:

- The agents mention the memory graph as the first stop for structural questions.
- The agents still preserve the normal OpenCode gates and repository checks.

### T04 - Define validation queries

Goal: prove the tool is helping on InVet instead of just being installed.

Work:

- Create a small checklist of InVet-specific queries.
- Include at least one backend chain, one frontend chain, and one cross-layer impact question.
- Save the answers or notes in a short operational record.

Acceptance criteria:

- The validation set covers backend, frontend, and cross-layer analysis.
- The answers are specific enough to guide code work.

### T05 - Verify rollout quality

Goal: make sure the integration improves work rather than adding noise.

Work:

- Test the tool on a few real InVet questions.
- Compare the result with manual search and file reading.
- Note where the memory graph is useful and where it misses context.

Acceptance criteria:

- The tool helps on structural questions.
- The fallback path remains necessary and documented.

## Suggested validation scenarios

| Scenario | Example question | Expected value |
| --- | --- | --- |
| Backend trace | "What use cases and routers depend on this repository method?" | Clear caller/callee chain |
| Frontend trace | "Which UI pages consume this API client?" | Route and component chain |
| Impact check | "What files are affected if this model or schema changes?" | Narrow blast-radius summary |
| Dead code check | "Is this module still referenced?" | Useful signal or a clear miss |
| Cross-layer review | "Does this FE change reach the right backend endpoint?" | End-to-end mapping |

## Risks

- The graph may miss generated code or unusual file layouts.
- The tool can become stale if the repo changes and the index is not refreshed.
- Agents may over-trust the graph if the fallback rules are not explicit.
- Local configuration can drift from repo docs if the contract is not written down.

## Fallback rules

- If the memory graph is missing, stale, or incomplete, use `rg`, file reads, and the existing OpenCode gates.
- If the graph gives a shallow answer, do not treat it as final proof.
- If a question is about product correctness, use tests and reviews as the final authority.

## Done criteria

- The local memory server is installed and indexing `C:\InVet`.
- The repo docs explain how the tool should be used.
- The main agents know when to consult it first.
- The validation set shows practical value on InVet.
- The fallback path remains intact.

## Next step recommended

Implement T01 first, then T02 and T03, and only after that run the validation scenarios from T04 and T05.
