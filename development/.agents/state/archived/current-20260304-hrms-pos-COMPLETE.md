---
description: Active session state - RESET this file at the start of every new session
---

# Current Session State

## Session Metadata
- **Session ID**: sess-20260304-001
- **Started**: 2026-03-04 04:40 UTC
- **Branch**: main
- **Commit**: TBD

## Current Goal
Fix POS bugs and develop full HRMS Employee Portal

## Current Plan

### Phase 1: POS Bug Fixes (Priority)
- [ ] Fix POS customer creation failed error
- [ ] Fix POS product checkout failure
- [ ] Test complete POS flow end-to-end

### Phase 2: HRMS Employee Portal Development

#### 2.1 Clock In/Out System
- [ ] Full-time: 8 hours or roster-based (employer configurable)
- [ ] Part-time: 4 hours or roster-based (employer configurable)
- [ ] Clock in/out UI with location/timestamp
- [ ] Backend API for attendance logging

#### 2.2 Task Management (Integrate Gameplan)
- [ ] View assigned tasks from Gameplan
- [ ] Add/create todo items
- [ ] Task status tracking

#### 2.3 Leave Management
- [ ] Apply for leave (form)
- [ ] Track leave status
- [ ] View leave balance
- [ ] Leave history

#### 2.4 Payroll
- [ ] Generate payroll view
- [ ] Download payslips
- [ ] Payroll history

#### 2.5 Role-Based Navigation
- [ ] Permission check on login
- [ ] Redirect to Desk for admins/managers
- [ ] Show allowed modules based on role/profile
- [ ] Module access control

#### 2.6 Attendance & Reporting
- [ ] Track attendance in portal
- [ ] Report attendance to HRMS backend
- [ ] Manager view for team attendance
- [ ] Helpdesk integration for issues/escalations

## Working Set - POS (frappe-bench/apps/zevar_core/frontend/zevar_ui/src/)
- `pages/POS.vue`
- `components/CheckoutModal.vue`
- `components/CartSidebar.vue`
- `components/POSProductModal.vue`
- `components/CustomerModal.vue` (if exists)
- Backend: `frappe-bench/apps/zevar_core/zevar_core/api.py`

## Working Set - HRMS Portal (frappe-bench/apps/hrms/frontend/src/)
- `views/Login.vue` - Auth & role-based redirect
- `views/Home.vue` - Dashboard
- `views/Profile.vue` - Employee profile
- `views/attendance/` - Clock in/out
- `views/leave/` - Leave management
- `views/salary_slip/` - Payroll
- `data/session.js` - Auth state
- `data/employee.js` - Employee data
- `router/index.js` - Routes & permissions
- `components/CheckInPanel.vue` - Clock UI

## Integrations Needed
- Gameplan (for tasks/todos)
- Helpdesk (for issue reporting)
- HRMS backend (attendance, leaves, payroll)
- ERPNext (for role permissions)

## Known Issues
1. POS: Customer creation fails
2. POS: Product checkout fails
3. HRMS Portal: Frontend exists but not fully functional
4. HRMS Portal: Needs clock in/out system
5. HRMS Portal: Needs Gameplan integration
6. HRMS Portal: Needs Helpdesk integration
