---
description: Append-only architectural decision log - Never delete or modify entries
---

# Decision Log

## Decisions

### DEC-001: State Freezing Protocol Implementation
- **Date**: 2026-03-03
- **Context**: Agent accuracy degrades over long sessions due to context pollution
- **Decision**: Implement Three-Layer State Model for AI agent sessions
- **Consequences**: All sessions start with explicit state injection
- **Commit**: TBD

### DEC-002: HRMS Portal - Gameplan Integration for Tasks
- **Date**: 2026-03-04
- **Context**: Employee portal needs task management functionality
- **Decision**: Use Gameplan integration for tasks and todos instead of building custom
- **Consequences**: 
  - Reuse Gameplan APIs for task management
  - Embed or link to Gameplan from portal
  - Single source of truth for tasks
- **Commit**: TBD

### DEC-003: HRMS Portal - Helpdesk Integration for Issues
- **Date**: 2026-03-04
- **Context**: Employees need to report attendance/manager issues
- **Decision**: Integrate Helpdesk for issue reporting and escalation
- **Consequences**:
  - Helpdesk tickets for attendance disputes
  - Manager escalations through Helpdesk
  - Team communication via Helpdesk
- **Commit**: TBD

### DEC-004: Clock In/Out - Roster-Based Configuration
- **Date**: 2026-03-04
- **Context**: Different employees have different shift requirements
- **Decision**: Support both fixed hours (8h full-time, 4h part-time) and roster-based configurable hours
- **Consequences**:
  - Employer can set roster per employee
  - System validates clock out based on roster
  - Overtime calculation from roster baseline
- **Commit**: TBD

---

## Archive Notice

When this file exceeds 50 decisions, archive the oldest 25 to `.agents/state/archived/decisions-YYYY-MM-DD.md`

### DEC-005: Code Review and Core File Cleanup
- **Date**: 2026-03-04
- **Context**: Need to audit codebase for:
  - Modified core Frappe/ERPNext/HRMS files (should not happen)
  - Unnecessarily long code that needs optimization
  - Changes that should be in zevar_core custom app
- **Decision**: 
  1. Review all modified core files and revert them
  2. Move customizations to zevar_core properly using hooks
  3. Trim long code without breaking functionality
  4. Follow Frappe standards for all customizations
- **Consequences**:
  - Core files remain pristine (easier updates)
  - All customizations in zevar_core
  - Cleaner, more maintainable code
  - Proper use of hooks and custom fields
- **Commit**: TBD

### DEC-006: Prioritize HRMS Employee Portal Development
- **Date**: 2026-03-05
- **Context**: Need to focus on fully functional employee portal with all features working
- **Decision**: 
  1. Prioritize employee portal over other tasks
  2. Address all gaps and limitations systematically
  3. Ensure all 7 key features work: clock in/out, leave, payroll, tasks, helpdesk, role-based nav
  4. Fix broken authentication and access issues
- **Consequences**:
  - Employee portal becomes primary focus
  - Systematic gap analysis and fixes
  - All integrations (Gameplan, Helpdesk) implemented
  - Role-based navigation fully functional
- **Commit**: TBD

### DEC-007: Fix POS create_pos_invoice ValidationError
- **Date**: 2026-03-06
- **Context**: POS checkout failing with "Order failed: /api/method/zevar_core.api.create_pos_invoice ValidationError"
- **Decision**: Debug and fix the ValidationError in create_pos_invoice API
- **Consequences**: POS checkout must work for business operations
- **Commit**: TBD

### DEC-EOD-001: End-of-Day Automation & Accounting Guardrails
- **Date**: 2026-04-28
- **Context**: Transitioning from manual Excel JCS EOD workflow to automated Frappe POS EOD
- **Decision**: 
  1. Enforce a $300 fixed float for POS registers.
  2. Each financier (Synchrony, AFF, CIMA, Progressive, Snap) maps to a dedicated A/R GL account via its Mode of Payment.
  3. Repairs and layaways never post to `Sales — Jewelry` income account.
- **Consequences**: 
  - Prevents revenue streams from mixing.
  - Automates reconciliation of the cash drawer without calculator math.
  - Ensures correct accounting for layaway liability and financier receivables.
- **Commit**: TBD
