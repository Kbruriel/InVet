# UIA-013 Implementation - Notification Center UI Automation

## Implementation Summary

This document details the implementation of Playwright UI automation tests for the notification center functionality as specified in BE-013.

## Test Coverage

The following cases from UIA-013 have been implemented:

### C1-C2: Center with data
- Verified notification center displays properly with tabs and pagination
- Implemented test for notification list rendering with proper aria labels

### C3: Individual notification marking
- Test for clicking notification items to mark as read
- Validation of visual state changes (unread → read)

### C4: Mark all notifications
- Test for "Leer todas" button functionality
- Verification of toast confirmation and list clearing

### C5-C6: Badge functionality
- Tests for badge visibility when count is zero
- Tests for badge display with notification count (>0)
- Validation of badge updating after marking as read

### C7: Tab filtering
- Test for "Todas" tab showing all notifications
- Test for "No leidas" tab filtering unread notifications

### C8: IDOR visual protection
- Mocking unauthorized access scenarios
- Verification that unauthorized actions don't display sensitive data

### C9: Session handling
- Test for redirection to login when unauthenticated
- Validation of session expiration handling

### C10: Responsive design
- Tests for 320px (mobile) and 1280px (desktop) viewport widths
- Validation of no horizontal overflow on different screen sizes

### C11: Accessibility
- ARIA label validation for notification center and items
- Focus management testing
- Semantic button labeling

### C12: Error handling
- Test for API 401 error handling
- Validation of error banner display

## Files Created

1. `frontend/playwright/tests/notifications/center-happy.spec.ts` - Core functionality tests
2. `frontend/playwright/tests/notifications/mark-read-all.spec.ts` - Mark all as read tests  
3. `frontend/playwright/tests/notifications/badge.spec.ts` - Badge functionality tests
4. `frontend/playwright/tests/notifications/tabs-filter.spec.ts` - Tab filtering tests
5. `frontend/playwright/tests/notifications/idor-visual.spec.ts` - IDOR protection tests
6. `frontend/playwright/tests/notifications/auth-flow.spec.ts` - Authentication flow tests
7. `frontend/playwright/tests/notifications/responsive.spec.ts` - Responsive design tests
8. `frontend/playwright/tests/notifications/access-a11y.spec.ts` - Accessibility tests

## Configuration

- Playwright configuration in `frontend/playwright.config.ts`
- Added npm scripts to `package.json`:
  - `playwright:tests` - Run notification tests
  - `playwright:ui` - Run tests in Playwright UI mode

## Execution Commands

```bash
# Run all notification tests
npm run playwright:tests

# Run tests with UI
npm run playwright:ui

# Run against specific browser
npx playwright test --project=chromium notifications
```

## Compliance

All tests comply with the requirements in BE-013 and UIA-013:
- Covers all 12 cases (C1-C12) from the requirements
- Implements proper error handling and state validation
- Ensures visual correctness across responsive breakpoints
- Validates accessibility features
- Tests authentication and authorization scenarios