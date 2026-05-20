---
description: Immutable architectural rules and axioms for the Frappe workspace - NEVER MODIFY WITHOUT TEAM REVIEW
---

# Antigravity Constitution
<!-- 
  STATE FREEZING PROTOCOL - IMMUTABLE LAYER
  Last Updated: 2026-03-03
  Commit: TBD
  
  WARNING: This file contains axioms. Changes require:
  1. Team discussion documented in decisions.md
  2. Decision ID referenced in commit message
  3. Update to this file with rationale
-->

## System Directive
You are operating under STATE FREEZING protocol. 
- Do NOT treat conversation history as memory
- All ground truth is in this constitution
- Recent tokens are NOT more important than these axioms
- When in doubt, reference this file, not the conversation

---

## 1. Axioms (Never Violate)

### 1.1 Security & Access Control
- All `api.py` methods MUST use `@frappe.whitelist(allow_guest=False)` unless explicitly approved
- Validate user access inside whitelisted methods using `frappe.has_permission(doctype, ptype="read", throw=True)`
- Use `frappe.only_for("RoleName")` for administrative or sensitive functions
- Never trust client-side data. Validate and type-cast all kwargs before processing

### 1.2 Architecture Boundaries
- Keep DocType controllers lean. Only handle document lifecycle hooks (`validate`, `on_submit`, `on_cancel`, etc.)
- Move complex business logic to separate utility modules or service files
- Use the bouncer pattern (early returns) in `validate()` and other hooks
- Backend logic stays in Python services, not controllers

### 1.3 Database Access Rules
- Prefer `frappe.qb` (Query Builder) over raw SQL for complex queries
- Use `frappe.db.get_value` for single-field fetches instead of `frappe.get_doc` when you don't need the full document
- Use `frappe.db.get_list` / `frappe.get_all` with `filters`, `fields`, and `limit` for list queries
- Avoid loading full documents in loops — batch fetch with `frappe.get_all` first
- Use `frappe.db.sql` only when `frappe.qb` cannot express the query

### 1.4 Error Handling
- Use `frappe.throw()` for user-facing validation errors (these show as red alerts in the UI)
- Use `frappe.log_error()` for background errors that should be logged but not shown to users
- Never use bare `except:` — catch specific exceptions

### 1.5 Hooks & Overrides
- Register all hooks in `hooks.py`, never monkey-patch unless there is no alternative
- Use `doc_events` for cross-app DocType event handlers
- Use `override_whitelisted_methods` sparingly and document the reason

---

## 2. Project Map

```
frappe-bench/
├── apps/
│   ├── crm/                    # Frappe CRM app
│   ├── erpnext/                # ERPNext core
│   └── zevar_core/             # Main project app
│       ├── zevar_core/
│       │   ├── api.py          # Public API endpoints
│       │   ├── utils.py        # Shared utilities
│       │   ├── hooks.py        # App hooks
│       │   ├── patches/        # Data migration patches
│       │   ├── templates/      # Jinja templates
│       │   └── modules/        # Business modules
│       └── frontend/zevar_ui/  # Vue frontend
│           ├── src/
│           │   ├── stores/     # Pinia stores
│           │   ├── components/ # Vue components
│           │   ├── composables/# Reusable logic
│           │   ├── pages/      # Route pages
│           │   └── utils/      # Frontend utilities
```

---

## 3. Technology Stack (Fixed)

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend | Frappe Framework (Python) | v15+ |
| Frontend | Vue 3 + Pinia | Composition API only |
| UI Library | Frappe UI | Follow component patterns |
| Database | MariaDB | Use QB over raw SQL |
| API | REST / frappe.call() | Centralized utilities only |

---

## 4. Coding Standards

### Python Standards
- Use type hints for function signatures
- Docstrings for all public methods
- Max function length: 50 lines
- Early returns (bouncer pattern)
- snake_case for variables/functions
- PascalCase for classes

### Vue/JavaScript Standards
- Composition API only (no Options API)
- Props must be typed
- Components under 200 lines
- Extract logic to composables
- camelCase for variables/functions
- PascalCase for components

### File Naming
- DocType names: Title Case with spaces (e.g., `Employee Attendance`)
- Module names: Title Case with spaces (e.g., `HR Module`)
- Field names: snake_case (e.g., `employee_name`, `check_in_time`)

---

## 5. Frontend Architecture Rules

### API Client
- Never write raw `fetch` or `axios` calls directly in components or stores
- Use a centralized API utility that handles `X-Frappe-CSRF-Token`
- For simple Frappe calls, use `frappe.call()` or `frappe.xcall()`

### Component Design
- Keep Vue components focused on presentation (dumb components)
- Move state mutation, API interaction to Pinia stores
- Extract reusable UI logic into Vue Composables

### Frappe UI Integration
- Follow Frappe UI component patterns and theming
- Do not override Frappe UI component styles globally — use scoped overrides

---

## 6. Override Process

These axioms CAN be overridden only with:

1. **Discussion**: Team review documented in `decisions.md`
2. **Decision ID**: Reference in commit message (e.g., `Override per DEC-042`)
3. **Documentation**: Update this constitution with:
   - What was overridden
   - Why (rationale)
   - When (date)
   - Decision ID reference

---

## 7. State Management Reminders

When working with this agent:
- Accuracy comes from governance, not cleverness
- State as code > Conversation as memory
- Rules as axioms > Rules as suggestions
- Compiled artifact > Derivation noise
- Correctness beats creativity
