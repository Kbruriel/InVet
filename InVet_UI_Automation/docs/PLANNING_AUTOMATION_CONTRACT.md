# Planning Automation Contract

## Purpose

The automation planner must map each slice to user stories and automation coverage.

## Mandatory IDs

- User story: `US-00X-NN`
- Backend slice: `BE-00X`
- Frontend slice: `FE-00X`
- QA slice: `QA-00X`
- UI automation slice: `UIA-00X`
- API automation slice: `APIA-00X`

## Planner outputs

The planner must create or update:

- `docs/opencode/tasks/user-stories/US-00X.md`
- `docs/opencode/tasks/backend/BE-00X.md`
- `docs/opencode/tasks/frontend/FE-00X.md`
- `docs/opencode/tasks/qa/QA-00X.md`
- `docs/opencode/tasks/ui-automation/UIA-00X.md`
- `docs/opencode/tasks/api-automation/APIA-00X.md`

## Coverage matrix

Each criterion must map to implementation and one of:

- UI automation
- API automation
- Manual coverage with explicit justification

No orphan criteria are allowed.

