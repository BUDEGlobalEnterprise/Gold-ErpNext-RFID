---
description: Active session state - RESET this file at the start of every new session
---

# Current Session State

## Session Metadata
- **Session ID**: sess-20260304-002
- **Started**: 2026-03-04 07:15 UTC
- **Branch**: main
- **Commit**: TBD

## Current Goal
Conduct thorough code review, optimize code, and ensure no core Frappe files are modified

## Current Plan

### Phase 1: Identify Modified Core Files
- [ ] Check which Frappe core files have been modified
- [ ] List all changes in frappe/, erpnext/, hrms/ core files
- [ ] Document what was changed and why

### Phase 2: Review zevar_core Custom App
- [ ] Review all files in zevar_core app
- [ ] Identify unnecessarily long code
- [ ] Check for code duplication
- [ ] Verify no core overrides exist (should use hooks/custom fields)

### Phase 3: Optimize Code
- [ ] Trim long functions without breaking functionality
- [ ] Remove unused imports and variables
- [ ] Simplify complex logic
- [ ] Ensure proper error handling
- [ ] Follow Frappe coding standards

### Phase 4: Move Core Changes to Custom App
- [ ] For each core file change:
  - [ ] Remove from core file (revert)
  - [ ] Implement properly in zevar_core using:
    - Custom fields
    - Server scripts
    - Client scripts
    - Hooks (doc_events, override_doctype_class, etc.)
    - Custom DocTypes
- [ ] Ensure no monkey-patching
- [ ] All changes go through hooks.py

### Phase 5: Final Verification
- [ ] Test all functionality still works
- [ ] Verify core files are clean
- [ ] Run bench migrate successfully
- [ ] No errors in console/logs

## Working Set - Core Files to Check
- `frappe-bench/apps/frappe/` (check for any custom changes)
- `frappe-bench/apps/erpnext/` (check for any custom changes)
- `frappe-bench/apps/hrms/` (check for any custom changes)

## Working Set - zevar_core App to Review
- `frappe-bench/apps/zevar_core/zevar_core/` (backend)
- `frappe-bench/apps/zevar_core/frontend/zevar_ui/src/` (frontend)

## Known Issues
- Core files may have been modified directly (bad practice)
- Code may be unnecessarily long/complex
- Functions may need optimization
- Changes need to be moved to custom app properly

## Notes
- NEVER modify core Frappe/ERPNext/HRMS files
- Use hooks.py for all overrides
- Use Custom Fields for DocType modifications
- Use Server Scripts for backend logic
- Use Client Scripts for frontend logic
- Keep zevar_core as the single place for all customizations
