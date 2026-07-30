# 05 - Done Gates by Command

## Command Execution Requirements

### `/plan-task BE-00X`
- [x] Slice requirements understood
- [x] Task breakdown completed
- [x] Scope defined properly
- [x] Technical feasibility validated
- [x] Plan saved in `docs/opencode/plans/BE-00X-plan.md`
- [x] Numbered checklist includes objective, measurable acceptance criteria, and `Paralelismo[P]`

### `/implement-backend-task BE-00X`
- [x] Backend code implemented following Clean Architecture
- [x] All requirements from task definition satisfied
- [x] Backend tasks from `docs/opencode/plans/BE-00X-plan.md` implemented
- [x] Completed backend tasks marked as `- [x]` only after acceptance criteria were verified
- [x] Unit tests written for all components
- [x] Code reviewed and linted
- [x] Security considerations applied

### `/implement-frontend-task FE-00X`
- [x] Frontend code implemented
- [x] Frontend tasks from `docs/opencode/plans/BE-00X-plan.md` implemented
- [x] Completed frontend tasks marked as `- [x]` only after acceptance criteria were verified
- [x] Component structure follows design guidelines
- [x] API communication working properly
- [x] Tests covering functionality
- [x] Responsive and accessible UI

### `/qa-task QA-00X`
- [x] QA tests executed for all endpoints
- [x] QA cases derived from plan objectives and acceptance criteria
- [x] Results documented with traceability to plan tasks
- [x] Completed QA tasks marked as `- [x]` only after validation evidence exists
- [x] Positive and negative cases validated
- [x] Regression testing completed
- [x] Permission validation checked
- [x] Security considerations verified
- [x] Evidence of testing provided in `docs/opencode/qa/QA-00X-results.md`

### `/review-slice BE-00X|FE-00X`
- [x] Review of implementation against requirements
- [x] Architecture compliance validated
- [x] Security issues identified and documented
- [x] Quality standards reviewed
- [x] Findings captured in `docs/opencode/reviews/BE-00X-review.md`

### `/implement-findings BE-00X`
- [x] All findings from review implemented
- [x] Corrections documented in `docs/opencode/reviews/BE-00X-corrections.md`
- [x] Changes made to source code or documentation only
- [x] No new functionality added outside of scope
- [x] Validation performed on implemented fixes

### `/clean-architecture-review`
- [x] Backend layers properly separated (API, Application, Domain, Infrastructure)
- [x] No business logic in routers
- [x] Domain entities remain independent from infrastructure concerns
- [x] Interfaces properly defined as ports/abstractions
- [x] Dependencies injected through proper patterns
- [x] Findings captured in `docs/opencode/reviews/BE-00X-clean-architecture-review.md` when applicable
- [x] Corrections can be consumed by `/implement-findings`

### `/security-review`
- [x] Authentication, authorization and IDOR/BOLA controls evaluated
- [x] Tokens, logs and public exposure reviewed
- [x] Findings captured in `docs/opencode/reviews/BE-00X-security-review.md` when applicable
- [x] Corrections can be consumed by `/implement-findings`

### `/run-checks`
- [x] Code quality checks passed
- [x] Linting and formatting validated
- [x] Type checking passed
- [x] Tests execute successfully

### `/update-docs`
- [x] All documentation updated with current status
- [x] Endpoints, components, variables properly documented
- [x] Decision logs updated
- [x] Risk matrix updated with current status
- [x] Changelogs and task status reflected

## Current Status - BE-004

### Historical Example
This section is kept as an example of how the gate contract is documented for a slice.
Current security or architecture findings should be recorded in the dedicated review files:
- `docs/opencode/reviews/BE-004-review.md`
- `docs/opencode/reviews/BE-004-clean-architecture-review.md`
- `docs/opencode/reviews/BE-004-security-review.md`

### Completed Gate Requirements:
- All previous gates have been completed for BE-004
- Clean Architecture implemented properly
- QA validation complete
- Findings addressed
- Tests passing

## Implementation Notes:

### Backend Changes (BE-004):
- **Endpoints**:
  - `GET /api/v1/clinics/branches/{branch_id}` - Public profile without auth
  - `GET /api/v1/clinics/{clinic_id}/{branch_id}` - Protected profile with auth

- **Architectural improvements**:
  - Implemented dependency injection in `app/api/dependencies.py`
  - Routers free of business logic
  - Separation of concerns maintained

- **Entities**:
  - `Branch`, `Service`, `Schedule`, `Rating` models using Pydantic v2
  - Entities properly separated from ORM concerns

### Security Considerations:
While Clean Architecture and functionality are solid, security findings should now be captured in the dedicated review file for the slice and resolved through `/implement-findings`.
