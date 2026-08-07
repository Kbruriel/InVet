# UI Automation Strategy

## Minimum UI coverage per slice with UI

- Happy path
- Visible negative path
- Form validation
- Loading state
- Error state
- Success state
- Empty state when applicable
- Protected route when applicable
- Redirect when applicable
- Role visibility when applicable
- One `@smoke` scenario
- Stable `@regression` scenarios

## Technical strategy

- Page objects for reusable flows
- Fixtures for environment and seeded users
- Traceability annotations for `US` and `CA`
- Cross-browser execution for regression confidence
- Mobile coverage with Pixel 7

## Current seed

The initial seed includes a login UI spec that becomes active once the frontend exposes a login route and `LOGIN_UI_ENABLED=true`.

