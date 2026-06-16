# Zevar — Workforce Intelligence Module: Target Design

> **Role:** Lead Designer, Workforce Intelligence. This is the engineering-ready target spec for the Workforce Intelligence module, built on the Zevar Frappe/ERPNext stack and the **Shared Platform**. It supersedes the stale planning baseline; all claims are grounded in direct code reads (`performance.py` 1054 lines / 13 endpoints, 4 doctypes; `commission.py`; `performance_log.json`; `compensation_calculation.json`; `performance_target.json`; `hooks.py`; `permissions.js`; `router.js`; HRMS confirmed installed).

---

## (A) Module Vision & Role in the Suite

**One sentence:** Workforce Intelligence is Zevar's *payroll-grade performance, compensation, coaching, and gamification* engine — the only module that turns the live sale/repair/attendance event stream into associates who close more, get paid correctly, get coached on real gaps, and are retained.

**Why it is the highest-leverage module.** Per the audit, Workforce is **~80% of a best-in-class backend with ~0% frontend exposure** and one load-bearing wiring bug (B2). The richest backend in the suite (`performance.py`: immutable event ledger, 3-axis weighted scorecard, tiered draw-based compensation algorithm, AI-flavored quarterly-review generator) is unreachable from the UI. Building the UI *unlocks* a large existing investment rather than creating net-new backend. No competitor unifies POS + commission + payroll on one DB; Zevar's native Frappe HRMS moat makes Workforce the structural trust/cost differentiator.

**Role in the suite (what only this module owns):**

| Concern | Owner | Workforce's role |
|---|---|---|
| The **human** axis of every business event | Workforce | Sale/repair/attendance → employee attribution → scorecard → pay |
| **Commission money correctness** | Workforce (with Profit module) | Commission computed on true margin via `profit_math`, not the broken 1-bucket `valuation_rate` margin (B3) |
| **Payroll disbursement** | Workforce | `Sales Commission Split` + tiered-rate pay → HRMS `Salary Component` → `Salary Slip` (native, audit-grade) |
| **Live per-associate scoreboard** | Workforce | `associate_personal` realtime channel — the personal fan-out the shared bus enforces |
| **Coaching & retention** | Workforce | Quarterly Review + 1:1s + gamification — closes the talent-development loop no other module touches |

**Three design principles (opinionated):**

1. **Performance Log is canonical revenue.** The divergent `employee_live_monitor.py` direct-SQL path is repointed to read Performance Log (shared-platform §2.4). One number, everywhere.
2. **Pay math is shared, never duplicated.** Every commission/scorecard/what-if number flows through `profit_math.compute_invoice_margin` + the scorecard engine. The 1-bucket `commission.py:104-109` margin (B3) is retired.
3. **Relationship over transaction.** Borrowing from the research (JewelLink's "book of business" + 5–10 deep-relationship capacity), the scoreboard rewards *leading indicators* (appointments kept, follow-ups, appraisal attach, layaway conversion) and clienteling, not just lagging revenue. This is what separates a coaching product from a leaderboard.

---

## (B) Target Feature Set — grouped, each mapped to the gap/competitor it beats

### B1. Foundation: the canonical, honest event spine (fixes the payroll-affecting bug)
- **Wire `log_sale_event` / `log_sale_cancel_event`** to Sales Invoice `on_submit`/`on_cancel` (B2). Today `hooks.py:65-73` lists only `commission.calculate_commissions`, `stock_reduction`, `reservation_manager` — `log_sale_event` is *defined* but never registered, so `Sale Completed`/`Return Processed` logs never exist and **revenue (the dominant scorecard axis) is always 0**. *Beats:* no competitor has this bug, but none has a truly immutable payroll-affecting ledger either.
- **One-time backfill** `bench --site … backfill-performance-logs` from historical POS `Sales Invoice` + `Sales Commission Split`. Reconciles every comp run executed to date (underpaid associates).
- **Activate the 6 dead event types** (`Layaway Completed`, `Upsell Recorded`, `Clock In`, `Clock Out`, `Overtime`, and the layaway-completed half) via the doctype hooks that already exist for layaway/repair + new clock-in hooks. Closes the "schema promises an event model the system does not deliver" gap.

### B2. Live scoreboard + TV/kiosk mode (Spinify/LevelEleven/Ambition)
- **Real live scoreboard** replacing the N+1 `get_live_scoreboard` (which is just `get_team_performance(...,today())` looping `get_employee_performance_summary` per associate in Python). Backed by `employee_period_rollup` (shared-platform §2.5) and pushed via `bus.publish("associate_personal", ...)` + an `admin_wall` aggregate. *Beats:* RICS/The Edge scoreboards are nightly; Zevar's is sub-second via socket.io because it owns the POS event stream.
- **TV/kiosk broadcast mode**: auto-rotating slides (leaderboard → top deals → goal progress → celebrations), big-number cards, rank-change animation, celebration overlays on milestone (first $10k day, 5 high-ticket week), configurable ranking metric. **Privacy rule baked in:** underperformer details never render on the shared wall — only rank + headline metric; the bottom N rows show "—" for sensitive fields.

### B3. The Edge Salesperson Performance coaching KPI set (the canonical scoreboard)
Per-associate, live, the industry-standard coaching template:
- **ARS** (Avg Retail Sale / ATV) + Δ vs store avg
- **GP $ / GP %** (true margin via `profit_math`) — *not* the inflated valuation_rate margin
- **Returns $ GP lost** (line-item return value × that item's true margin)
- **Selling-Skills**: discount $ / count / avg-% / **Discount Ratio** (discount as % of gross)
- **UPT** (units per transaction), **conversion** (needs `Store Traffic Log`, shared-platform §7), **attach rate**, **customer-capture-rate**, **margin generated**
- **Revenue-per-hour-worked** (HotStats GOPPAR analogue applied to associates) — fixes the hardcoded `scheduled_hours=0` once clock-in lands.

### B4. Multi-tier commission engine in ONE plan (CaptivateIQ/Spiff/Xactly)
Zevar already has tiered-rate scaffolding + partial draw. Extended:
- **Base rate + attainment-based ACCELERATORS** (stepped `Commission Range` rates above quota thresholds)
- **Recoverable / non-recoverable DRAW** (already partially modeled via `guaranteed_pay`/`performance_deduction`)
- **SPIFF / bonus overlays** → HRMS `Employee Incentive` / `Additional Salary`
- **Multi-associate splits** (templates + overlay credits) — already read from `custom_salesperson_splits`
- **Commission TRACING**: drill any payout → exact deal/line/rule that produced it (new `commission_trace` child table)
- **Estimated-vs-realized projection** (Commission Estimator below)
- **Margin-corrected commission** (B3 fix): `commission.py` calls `profit_math.compute_invoice_margin`; "By Profit Margin" rules pay on *true* 6-bucket margin. *Beats:* generic POS flat-% and even Xactly lack jewelry-grade COGS-aware commission.

### B5. Composite scorecard, cascading & per-role (Ambition/LevelEleven)
- **Weighted multi-dimensional composite**, weights configurable **per role** (Associate vs Bench Jeweler vs Manager each weight different KPIs). Zevar already has the 3-axis (Revenue/Activity/Quality, sum=100) engine; extend to per-role weight templates.
- **Leading indicators surfaced**: sessions handled, appraisals created, repair intake, follow-ups completed, appointments kept — not just lagging revenue.

### B6. Quota/target management with cascade + what-if (Xactly Plan / CaptivateIQ Guided Plan Builder)
- Cascade **store → team → associate** via HRMS **Goal tree** ↔ `Performance Target`.
- **Plan rollover / cloning** (one click copies a target set into the next period).
- **Scenario/what-if simulation** before period start: model a rate/weight change, preview projected payout, no commit. New `pay_simulation` endpoint (idempotent, non-persisting).

### B7. Commission Estimator — the associate's "what do I need to hit" (Spiff)
- Quota-retirement **progress ring** (revenue achieved ÷ revenue target)
- **Projected-on-pace attainment** = run-rate × remaining days
- **Projected period payout** + **next-tier rate teaser** ("2 more high-ticket sales unlocks +$X/hr")
- Personal scoreboard, associate role only.

### B8. Structured 1:1 coaching module (Ambition) — *Zevar's biggest competitive gap*
- Recurring **cadence calendar**, coaching plan with **SMART goals**
- **Talking-points AUTO-GENERATED from scorecard gaps** (e.g. "ATV 12% below target last 3 weeks", "discount ratio in top quartile") — extends `_generate_review_insights` (`performance.py:1009`)
- **Action items** with owner + due date, **coaching-notes history**
- Pairs with the existing `Quarterly Performance Review` (the `development_plan` text field becomes a real loop).

### B9. Gamification ledger on the immutable event stream (Centrical/Spinify)
- **Points Ledger** on Performance Log (new `point_value`, `badge_earned`, `contest_reference` fields)
- **Badges** (first $10k day, 5 high-ticket week, 30-day punctuality streak)
- **Time-boxed contests** (store-vs-store championships)
- **Celebration triggers** firing to POS/TV/associate app via `bus.publish`
- **Virtual rewards store** (points → real gift cards/vouchers). **Jewelry-specific behaviors** (appraisal attach, layaway conversion, high-ticket close), not generic calls/demos.

### B10. Behavior-triggered smart notifications (Centrical)
- After an associate's Nth sale, push a context-aware nudge ("you just sold 5 high-margin items, 2 away from today's bonus") with deep-link to microlearning. **Real-time because Zevar owns the POS event stream** — competitors relying on nightly CRM sync cannot.

### B11. Scheduling + clock-in (Deputy/When I Work/Homebase + JewelLink seasonality)
- **Demand-based smart scheduling**: forecast labor from Zevar's own `pos_session` sales history (no integration needed) → coverage-vs-demand view
- Drag-and-drop shift grid, **shift swapping with approval**, **geo-fenced + facial-recognition kiosk clock-in** (anti buddy-punch)
- Auto-producing **`Clock In`/`Clock Out` Performance Logs** + worked hours → populates `total_hours_worked` and **kills the hardcoded `scheduled_hours=0` / `attendance_%=0`**.
- Map to HRMS **Shift Type / Shift Assignment / Employee Checkin**.

### B12. Clienteling as relationship ecosystem (JewelLink)
- Per-associate **book of business** with relationship-tier tracking and the 5–10 deep-relationship capacity concept
- Customer timeline unifying POS + texts + notes + appointments, **appointment scheduling/tracking** (bridal/timepiece)
- **Follow-up tasks** with overdue alerts, lead routing, personality-trait evaluation + AI roleplay.

### B13. Adaptive spaced-repetition microlearning (Axonify/JewelLink Academy)
- Daily 3–5 question bursts **tied to new-inventory launches** (auto-push a gemstone/bridal quiz worth points when new stock arrives), video-pitch submission, onboarding milestone tracking.

### B14. Payroll-grade disbursement + ASC 606/IFRS 15 (Xactly/Spiff + Frappe HRMS)
- Wire `Commission Rule` / `Sales Commission Split` → HRMS **Salary Component** → **Salary Slip** natively
- **ASC 606 / IFRS 15 commission expense recognition** (recognized-period / deferred fields) on `Compensation Calculation` for multi-store finance compliance.

### B15. Audit-ready immutable rule-edit history (Spiff Deep Audit Trail)
- `commission_rule_history` (effective_date, changed_by, before/after JSON) — eliminates pay disputes by transparency
- **In-line dispute/comment thread** on each commission payout with @-mentions.

### B16. Manager "Lead with insights" Team Console (Centrical/Spiff)
- One screen: every associate's training status, sales-this-period, goal attainment, **one-click actions** (nudge / assign task / invite to 1:1 / send feedback template) + team pacing + forecast bands.

---

## (C) Information Architecture — screens, layout, role-aware variants

### C1. Route map (all under `/reports/dashboards/...`, SPA, single `<router-view>` shell — shared-platform §4)

| Route | Component | Role variant |
|---|---|---|
| `/workforce` | `WorkforceIntelligence.vue` (rebuilt) | **Manager/Owner Team Console** OR **Associate self-view** (same route, role-aware) |
| `/workforce/associate/:employeeId` | `AssociateDetailPerformance.vue` (rebuilt) | Manager drills an associate; associate with own id = self |
| `/workforce/me` | alias → `/workforce` for associate role | Associate personal scoreboard |
| `/workforce/tv` | `WorkforceTV.vue` (new) | **TV/kiosk broadcast** — owner-managed, store-scoped, auto-rotating |

Existing routes preserved: `router.js:475` (`WorkforceIntelligence`), `:481` (`AssociateDetailPerformance`). The `EmployeeLiveMonitor` route (`router.js:224`) is **kept** as the associate's lightweight live "My Dashboard" but its data source is reconciled to Performance Log (B2 fix).

### C2. Owner / Manager Team Console (`WorkforceIntelligence.vue`)
```
┌─────────────────────────────────────────────────────────────────────┐
│ [timeStore bar]  [store ▼]  [period ▼]  [Compare: prior ▼]   🔄 Live │
├─────────────────── Team pacing strip (KpiSparkline cards) ──────────┤
│  Revenue-to-date │ Quota attainment % │ Team GP$ │ Active now │ Hours│
├────────────── Live ranked scoreboard (real-time, sortable) ─────────┤
│ Rank │ Associate │ ARS │ GP% │ UPT │ Conv │ Disc% │ Cap% │ Hrs │$Hr │
│  1   │ …         │ …   │ …   │ …   │ …    │ …     │ …   │ …  │ …  │
│  ⬆2  │ …         │                                                                     │  ← rank-change animation
│ ... (bottom 3 sensitive fields masked on TV) ...                     │
├────────────── Goal cascade (store→team→associate bars) ─────────────┤
│  [progress bars] [pace-to-period-end forecast bands]                 │
├────────────────── Gamification ───────────┬── Alerts / nudges ───────┤
│  Active contest leaderboard (store-vs-store)│ Team anomalies (idle,  │
│  Badge wall (recently earned)               │ discount-abuse, return │
│                                             │ clusters) → one-click  │
├────────────────── Actions ─────────────────┴──── nudge/1:1/assign ───┤
│  [Run comp ▼ period] [Plan rollover] [What-if sim] [Bulk finalize]   │
└─────────────────────────────────────────────────────────────────────┘
```

Widgets:
- **LiveScoreboardTable.vue** — rows update via `associate_personal` (manager sees store aggregate), sorted by configurable ranking metric (ARS / GP$ / UPT / conversion). Reads `employee_period_rollup`.
- **GoalCascade.vue** — HRMS Goal tree rendered as nested progress bars; pace forecast band from run-rate.
- **ContestPanel.vue** + **BadgeWall.vue** — gamification (B9).
- **CompActions.vue** — `run_compensation_calculation` (made idempotent), `bulk_calculate_compensation`, plan rollover, what-if.

### C3. Associate self-view (`AssociateDetailPerformance.vue`, role=associate)
```
┌─────────────────────────────────────────────────────────────────────┐
│ My Scoreboard — [today | week | month | quarter ▼]                   │
├─────────── KPI hero cards (TrendLineChart sparkline overlays) ───────┤
│ Revenue │ Quota ring (on-pace) │ UPT │ Conversion │ Disc% │ Hrs worked│
├────────────── Commission Estimator (Spiff) ──────────────────────────┤
│  ◯ Quota retirement ring   Projected payout $X   Next tier: +$Y/hr   │
│  "You need 2 more high-ticket sales to unlock the bonus tier"        │
├────────────── My performance trend (multi-series) ───────────────────┤
│  TrendLineChart: revenue vs prior period vs YoY, UPT overlay         │
├────────────────── Latest Quarterly Review ───────────────────────────┤
│  Tier badge │ strengths │ improvements (auto) │ [Acknowledge]         │
├────────────────── My 1:1s & action items ────────────────────────────┤
│  Next 1:1 date │ talking points │ action items w/ due │ dev plan      │
├────────────────── My gamification ───────────────────────────────────┤
│  Points balance │ badges │ contest rank │ rewards store              │
└─────────────────────────────────────────────────────────────────────┘
```
**Privacy:** associate sees **only own data** (backend `isOwnSalesOnly()` + `_resolve_employee_from_user`). No peer PII, no peer commission amounts.

### C4. TV / Kiosk mode (`WorkforceTV.vue`)
- Full-screen, large-font, high-contrast, auto-rotating slides (Leaderboard → Top Deals → Goal Progress → Celebrations), ~12s/slide, sticky-pin override during a contest climax.
- **Live via `admin_wall` realtime** (no polling), visible "last updated" + stale-data warning.
- **Privacy by construction:** only rank + headline metric; sensitive fields masked; no customer PII; no individual commission dollars for bottom performers; celebrations require manager approval before broadcast.

### C5. Shared chrome
All variants reuse shared-platform primitives: `timeStore` (§4.3), `useDashboardData`/`useRealtime`/`usePolling`/`useBackfill` (§1.6), `utils/format.js` + `utils/status-colors.js` (§3.3-3.4), ECharts components (§3.2), `KPICard.vue`.

---

## (D) Data Model — new/changed doctypes + materialized tables

### D1. EXISTING doctypes to reuse (do NOT rebuild) — extended only

| Doctype | Status | Changes in this module |
|---|---|---|
| **Performance Log** (immutable, `PLOG-YYMMDD-#####`) | keep, extend | Add fields: `point_value` (Int), `badge_earned` (Link→`Gamification Badge`), `contest_reference` (Link→`Gamification Campaign`), `store` (Link→Warehouse, mirror of `store_location`), `event_subtype` (Data, e.g. high-ticket vs layaway). **Immutability stays enforced** in `performance_log.py`. |
| **Performance Target** (submittable) | keep, extend | Add: `draw_type` (Select: `None/Recoverable/Non-Recoverable`), `draw_amount` (Currency), `is_manager_target` (Check), `parent_goal` (Link→HRMS `Goal`) for cascade. Keep existing comp fields (`guaranteed/target/superior_hourly_rate`, `minimum_performance_pct`, `termination_threshold_pct`, weights, thresholds). |
| **Compensation Calculation** (submittable, Employee-readable) | keep, fix | **Stop hardcoding zeros** (B-populate, see KPIs): `scheduled_hours`, `attendance_percentage` from clock-in; `high_ticket_sales` from item lines > `target.high_ticket_threshold`; `upsells` from multi-item invoices; `layaway_default_rate` from Layaway Contract. Add: `commission_traces` (Table→`Commission Trace`), `recognition_status` (Select: `Recognized/Deferred`), `recognized_period` (for ASC 606). Add `margin_generated` (Currency) via `profit_math`. |
| **Quarterly Performance Review** (submittable) | keep, extend | Populate the currently-blank fields (`activity_score`, `quality_score`, `quarterly_target`, `revenue_achievement_pct`, `recommended_rate`, `bonus_recommendation`). Add `coaching_sessions` (Table→`Coaching Session` link). |
| **Sales Commission Split** | keep | Becomes the *output* of the commission engine (margin-corrected), feeds HRMS Salary Component. Add `commission_rule` (Link), `trace_id` (Link→Commission Trace). |
| HRMS **Employee Checkin / Shift Type / Shift Assignment** | reuse | Produce `Clock In/Out` Performance Logs + worked hours. No rebuild. |
| HRMS **Salary Component / Salary Slip / Additional Salary / Employee Incentive** | reuse | Payroll disbursement (B14). No rebuild. |
| HRMS **Appraisal Cycle / Appraisal Template / Goal / Employee Performance Feedback** | reuse | Quarterly Review ↔ Appraisal; target cascade ↔ Goal; coaching ↔ Feedback. No rebuild. |

### D2. NEW doctypes (under `…/unified_retail_management_system/doctype/`)

| Doctype | Key fields | Purpose |
|---|---|---|
| **Coaching Session** | `employee` (Link→Employee), `manager`, `date`, `cadence` (Weekly/Bi-weekly/Monthly), `agenda` (Text Editor), `talking_points` (auto, JSON), `notes`, `action_items` (Table: owner, due_date, status), `linked_review` (Link→QPR), `next_session_date` | B8 — structured 1:1s |
| **Gamification Campaign** | `name`, `type` (Contest/SPIFF/Streak), `store_scope`, `period_start/end`, `rule_set` (Table→`Points Rule`), `status`, `leaderboard_metric` | B9 — time-boxed contests |
| **Gamification Badge** | `name`, `icon`, `description`, `criteria` (JSON), `point_value`, `jewelry_specific` (Check: appraisal-attach/layaway-conv/high-ticket) | B9 badges |
| **Badge Award** | `employee`, `badge` (Link), `awarded_at`, `awarded_by`, `performance_log` (Link), `celebrated` (Check) | immutable badge ledger |
| **Reward Catalog Item** | `name`, `points_cost`, `type` (Gift Card/Voucher/Time-Off), `vendor`, `value` | B9 rewards store |
| **Reward Redemption** | `employee`, `reward` (Link), `points_spent`, `status`, `fulfilled_by/at` | B9 |
| **Commission Trace** | `commission_split` (Link), `invoice`, `line_item`, `rule_id`, `rule_version` (Link→Rule Edit History), `margin_basis` (from `profit_math`), `amount`, `calc_log` (JSON) | B4/B15 — per-payout reproducibility |
| **Commission Rule Edit History** | `rule` (Link→Commission Rule), `effective_date`, `changed_by`, `before_json`, `after_json` | B15 — immutable, audit-ready |
| **Labor Forecast** | `store`, `date`, `hour`, `forecasted_traffic`, `forecasted_revenue`, `recommended_staff`, `confidence` | B11 — demand-based scheduling (feeds `Store Traffic Log` history) |
| **Customer Appointment** | `customer`, `associate` (Employee), `type` (Bridal/Timepiece/Repair/Appraisal), `scheduled_at`, `status`, `outcome`, `linked_sale` | B12 clienteling |
| **Follow-up Task** | `customer`, `associate`, `due_date`, `type`, `status`, `linked_appointment` | B12 |
| **Customer Relationship** (book of business) | `associate`, `customer`, `relationship_tier` (1-5), `lifetime_value`, `last_contact`, `capacity_flag` | B12 |

### D3. Materialized rollup tables (shared-platform §2.5 — Workforce consumes)

**`employee_period_rollup`** (replaces `get_team_performance` N+1) — **the spine of the live scoreboard**:

| Column | Type | Notes |
|---|---|---|
| `employee` | varchar(140) | PK part |
| `period_type` | varchar(20) | PK — `daily/weekly/monthly/quarterly` |
| `period_start` | date | PK part |
| `period_end` | date | |
| `store` | varchar(20) | |
| `revenue_amount` | decimal(18,4) | from Performance Log |
| `item_count` / `txn_count` / `customer_count` | int | |
| `upt` | decimal(8,3) | units/txn |
| `high_ticket_count` / `upsell_count` | int | |
| `return_count` / `return_value` | int / decimal | |
| `margin_generated` | decimal(18,4) | from `profit_math` via SCB |
| `commission_earned` | decimal(18,4) | |
| `hours_worked` | decimal(8,2) | from clock-in logs |
| `attendance_pct` | decimal(5,2) | |
| `points_earned` | int | gamification ledger |
| `rank` | int | computed on insert |
| `updated_at` | datetime | |

PK: `(employee, period_type, period_start)`. Refreshed on every Performance Log insert (upsert) + nightly safety rebuild. **Fixes the O(employees×logs) Python loop.**

Also consumes `daily_store_sales_rollup` (cross-store leaderboard, channel split), `store_traffic_log` (conversion), and `live_event_log` (24h backfill).

---

## (E) API Surface — endpoint name + purpose + method

### E1. Existing endpoints (unlocked by the UI build) — `zevar_core.api.performance`

| Endpoint | Method | Purpose | Status change |
|---|---|---|---|
| `get_employee_performance_summary` | GET | per-associate revenue/activity/quality/achievement | repoint to rollup |
| `get_team_performance` | GET | team scoreboard (was N+1) | **repoint to `employee_period_rollup`** |
| `get_live_scoreboard` | GET | today's ranked scoreboard | backed by rollup + realtime |
| `get_performance_history` / `get_performance_trend` | GET | trend series | unchanged |
| `run_compensation_calculation` | POST | single comp run | **make idempotent** (force/recompute instead of throw) |
| `bulk_calculate_compensation` | POST | batch comp | **make idempotent** |
| `get_quarterly_review` / `finalize_review` / `acknowledge_review` / `get_review_history` / `get_team_review_summary` | GET/POST | review lifecycle | **add role gate to `acknowledge_review`** |

### E2. NEW endpoints — `zevar_core.api.workforce` (new module; refactor performance.py into it)

| Endpoint | Method | Purpose |
|---|---|---|
| `workforce.get_scoreboard(store, period, metric, compare)` | GET | ranked scoreboard from rollup + comparison overlay |
| `workforce.get_quota_progress(employee, period)` | GET | quota retirement ring + on-pace projection (Commission Estimator) |
| `workforce.project_payout(employee, period, scenario?)` | GET | projected period payout + next-tier teaser |
| `workforce.simulate_pay(employee, period, override)` | POST | **what-if** pay sim (non-persisting, idempotent) |
| `workforce.cascade_targets(store, period)` | GET | store→team→associate goal tree (HRMS Goal) |
| `workforce.clone_target_plan(from_period, to_period, employees)` | POST | plan rollover |
| `workforce.get_coaching_sessions(employee)` | GET / POST | 1:1 cadence + action items |
| `workforce.generate_talking_points(employee)` | GET | auto talking-points from scorecard gaps (extends `_generate_review_insights`) |
| `workforce.get_contests(store)` / `create_contest` / `contest_leaderboard` | GET/POST | gamification campaigns |
| `workforce.award_badge(employee, badge, perf_log)` | POST | badge award (immutable) + celebration publish |
| `workforce.get_points_ledger(employee)` | GET | points history |
| `workforce.redeem_reward(employee, reward)` | POST | rewards store redemption |
| `workforce.get_book_of_business(employee)` | GET | clienteling book + capacity flag |
| `workforce.schedule_appointment(...)` / `complete_follow_up(...)` | POST | clienteling actions |
| `workforce.get_labor_forecast(store, date)` / `build_forecast` | GET/POST | demand-based scheduling |
| `workforce.clock_in(employee, store, geo?, biometric?)` / `clock_out` | POST | kiosk clock-in → Performance Log + Checkin |
| `workforce.get_shift_grid(store, week)` / `propose_swap` / `approve_swap` | GET/POST | scheduling |
| `workforce.push_compensation_to_payroll(period)` | POST | Commission → HRMS Salary Component → Salary Slip (B14) |
| `workforce.get_commission_trace(split)` | GET | drill payout → deal/line/rule (B4/B15) |
| `workforce.dispute_commission(split, comment, mentions)` | POST | in-line dispute thread (B15) |

### E3. Wiring endpoints (shared-platform)
- `realtime.hooks.on_invoice_submit` → `workforce.log_sale_event` + rebuild rollup + `bus.publish("associate_personal", ...)` (per-employee fan-out, **never global**).
- `realtime.hooks.on_invoice_cancel` → `workforce.log_sale_cancel_event`.
- `realtime.hooks.run_anomaly_push` includes workforce anomalies (idle associate, discount-abuse cluster, return cluster).
- `backfill-performance-logs` bench command (one-time, idempotent on `(employee, event_date, reference_document)`).

---

## (F) Realtime & KPI Wiring (per shared platform)

### F1. Channels consumed/produced

| Channel | Scope | Workforce producer/consumer |
|---|---|---|
| `associate_personal` | `user=<employee_user_id>` (**never global** — the iron rule) | **Producer**: sale/repair/attendance/badge events fan-out per employee. **Consumer**: associate self-view + detail. Replaces the broken `publish_employee_event` broadcast (B4). |
| `sales_tick` | `room="admin_wall"` + `room="store_<wh>"` | Consumer: live scoreboard aggregate (team revenue/txn ticks), TV mode. |
| `command_center` | `room="admin_wall"` | Consumer: Team Console pacing strip + team anomaly tiles. |
| `anomaly_alert` | `room="admin_wall"` | Producer (workforce rules: idle associate, discount-abuse, return cluster, no-show) + Consumer: Team Console alerts panel + one-click nudge. |
| `system_health` | `room="admin_wall"` | Consumer: clock-in kiosk health, register-online feeds "Active now" count. |

### F2. Event payloads (from shared `events_schema.py`)
- `SaleCompletedData.employees` drives the `associate_personal` per-employee fan-out (the same `custom_salesperson_splits.employees` list).
- `associate_personal` payloads for workforce: `sale.completed` (revenue, GP via SCB, commission), `badge.awarded`, `contest.progress`, `milestone.reached` (celebration), `attendance.clocked_in/out`.

### F3. Rollup tables read
- `employee_period_rollup` — scoreboard, quota progress, comp runs (replaces N+1).
- `daily_store_sales_rollup` — cross-store leaderboard, channel mix.
- `store_traffic_log` — conversion numerator.
- `live_event_log` — 24h backfill on TV/console open (`useBackfill`).

### F4. Refresh triggers (shared-platform §2.6)
- Performance Log insert → `workforce.rebuild_employee_rollup(employee, period)` upsert → `bus.publish("associate_personal", ...)`.
- Invoice submit/cancel → `log_sale_event/cancel` → rollup rebuild → `sales_tick`.
- Badge award → `Badge Award` insert → rollup `points_earned` upsert → celebration publish (manager-approved if TV-bound).

---

## (G) KPIs with PRECISE formulas

> All revenue/margin figures use `profit_math.compute_invoice_margin` (shared-platform §2.2). Revenue is **canonical from Performance Log**, not divergent `Sales Commission Split` direct SQL.

| KPI | Formula | Source | Today |
|---|---|---|---|
| **ARS / ATV** | `SUM(Sale Completed.revenue_amount) / COUNT(Sale Completed logs)` | `employee_period_rollup` | computed |
| **GP $ (associate)** | `SUM(SCB.gross_profit WHERE salesperson=employee)` | SCB via `profit_math` | **wrong basis** (B3) |
| **GP % (associate)** | `GP$ / revenue` | SCB | wrong basis |
| **Returns $ GP lost** | `SUM(returned_qty × item.gross_profit_per_unit)` | SCB + return logs | absent |
| **UPT** | `SUM(item_count) / COUNT(Sale Completed logs)` | rollup | **absent** (qty unused) |
| **Conversion** | `COUNT(Sale Completed logs) / SUM(Store Traffic Log.visitors_in)` for same store+hour | traffic log + rollup | **impossible today** |
| **Attach rate** | `COUNT(invoices with >1 item) / COUNT(invoices)` | rollup | absent |
| **Customer-capture-rate** | `COUNT(distinct new customers) / COUNT(Store Traffic Log.visitors_in)` (Lightspeed jewelry-critical) | traffic log + invoices | impossible today |
| **Discount $ / count / avg-%** | `SUM(discount_amount)`, `COUNT(discounted invoices)`, `discount$/count`, **Discount Ratio** = `discount$ / gross_sales` | Sales Invoice | absent |
| **Revenue-per-hour-worked** | `revenue / SUM(hours_worked)` | rollup (clock-in fixes `hours_worked`) | **div/0** (scheduled_hours=0) |
| **High-ticket count** | `COUNT(Sale Completed logs WHERE invoice total > target.high_ticket_threshold)` | target threshold + invoices | **hardcoded 0** |
| **Upsells** | `COUNT(Sale Completed logs WHERE item_count ≥ 2)` (configurable) | rollup | **hardcoded 0** |
| **Layaway conversion** | `COUNT(Layaway Completed) / COUNT(Layaway Created)` | Performance Log | absent |
| **Layaway default rate** | `COUNT(Layaway Contract forfeited) / COUNT(Layaway Created)` | Layaway Contract | **hardcoded 0** |
| **Attendance %** | `hours_worked / scheduled_hours` | clock-in + Shift Assignment | **hardcoded 0** |
| **Quota attainment %** | `revenue_achieved / revenue_target × 100` (per axis; weighted composite) | target + rollup | computed (but revenue=0) |
| **On-pace projected attainment** | `attainment_today × (period_days / elapsed_days)` (run-rate extrapolation) | rollup | absent |
| **Effective hourly rate (tiered)** | `superior_rate if score≥100; else guaranteed + (score-min_pct)/(100-min_pct)×(target-guaranteed); else guaranteed` | `performance.py:591-612` (keep) | computed |
| **Final pay** | `hours × effective_rate + commission − draw (if recoverable)` | comp engine | computed |
| **Composite score** | `rev_ach%×rev_w + act_ach%×act_w + qual_ach%×qual_w` (weights per role, sum=100) | `performance.py` (extend per-role) | computed (3-axis) |

**Hardcoded-zero fields to populate (audit tech-debt):** `high_ticket_sales`, `upsells`, `customer_satisfaction` (survey-driven later), `layaway_default_rate`, `scheduled_hours`, `attendance_percentage`, quarterly `activity_score`/`quality_score`/`recommended_rate`/`bonus_recommendation`.

---

## (H) UX Patterns Worth Copying (from research)

| Pattern | Source | Application in Workforce |
|---|---|---|
| **Relationship-tier book of business + 5–10 capacity** | JewelLink | `Customer Relationship` doctype; capacity flag prevents over-assignment; associate rewarded for depth not breadth |
| **Auto-generated coaching talking points from scorecard gaps** | Ambition + Zevar's own `_generate_review_insights` | `generate_talking_points` extends the existing insight generator |
| **Quota-retirement ring + next-tier teaser** | Spiff | Commission Estimator (associate self-view) |
| **Per-role weighted scorecard (associate vs bench vs manager)** | LevelEleven / Ambition | Per-role weight templates on `Performance Target` |
| **Live celebration overlays + rank-change animation** | Spinify / LevelEleven | TV mode + POS-side celebration (manager-approved) |
| **Demand-based scheduling from own sales history** | Deputy + JewelLink seasonality | `Labor Forecast` from `pos_session` history (no integration) |
| **Geo-fenced + facial-recognition kiosk clock-in** | Homebase / Deputy | anti buddy-punch; produces `Clock In/Out` Performance Logs |
| **Spaced-repetition microlearning tied to new inventory** | Axonify / JewelLink Academy | auto-push gemstone/bridal quiz worth points on new-stock arrival |
| **Deep Audit Trail + in-line dispute thread** | Spiff | `Commission Rule Edit History` immutable + dispute comments with @-mention |
| **Composite coaching scoreboard (ARS/GP/UPT/Selling-Skills)** | The Edge Salesperson Performance Report | the canonical scoreboard (B3) |
| **"Lead with insights" one-click manager actions** | Centrical | Team Console nudge / 1:1 / assign / feedback-template buttons |

---

## (I) Permissions & Privacy — associate-data isolation (critical)

### I1. Role matrix (reconciled with backend `only_for` per shared-platform §5.4)

| Surface | Frontend helper | Backend roles |
|---|---|---|
| Team Console (manager/owner) | `canAccessWorkforce()` (new) | System Manager, HR Manager, Store Manager |
| Associate self-view | `isOwnSalesOnly()` | Employee, Employee Self Service, Sales User |
| TV/Kiosk broadcast | `canAccessWorkforce()` | System Manager, Store Manager (owns TV content) |
| Compensation run / payroll push | `canAccessWorkforce()` + finance gate | System Manager, HR Manager, Accounts Manager |
| Quarterly Review finalize | `canAccessWorkforce()` | System Manager, HR Manager, Store Manager |
| Quarterly Review acknowledge | `isOwnSalesOnly()` (ownership-proof) | the review's own employee |

### I2. Privacy rules (enforced backend, never just client)
1. **`associate_personal` channel is ALWAYS user-scoped** (`user=<employee_user_id>`, never global). This is the shared-bus iron rule and fixes the current `publish_employee_event` broadcast (B4) that undermined `employee_live_monitor.py`'s claimed isolation.
2. **Associate sees only own data**: revenue, commission, attendance, book-of-business. No peer PII, no peer commission dollars, no peer customer lists. Enforced via `_resolve_employee_from_user` + `only_for`.
3. **TV mode masks sensitive fields**: bottom-N performers show "—" for commission/ARs; celebrations require manager approval before broadcast; no customer PII ever on the wall.
4. **Manager scope = own stores**: a Store Manager sees only their `store_location` set; multi-store rollup is owner/HR-only. (Cross-store volume leak bug in `employee_live_monitor.get_store_activity` — aggregating all stores — is fixed: respect employee's store.)
5. **Compensation/payout visibility**: HR/Accounts + the employee themselves (Compensation Calculation is Employee-readable via `if_owner`); never visible to peer associates.
6. **Audit-grade immutability**: Performance Log, Badge Award, Commission Rule Edit History are immutable (controller-enforced, mirroring `performance_log.py`). Enables pay-dispute defense.

---

## (J) Integration with the Other 3 Modules + Native Frappe Stack

### J1. Cross-module integration
| Module | Integration |
|---|---|
| **Live Monitor (Command Center)** | Workforce feeds the live employee-activity grid (status/time-in-state), the scoreboard tile, and workforce anomaly rules into the Command Center's `admin_wall`. Shares `useRealtime`/`useBackfill`. |
| **Sales Monitor** | Workforce is the **people dimension** of Sales Monitor. Both read `daily_store_sales_rollup`; salesperson leaderboard (Sales) and associate scoreboard (Workforce) share the `employee_period_rollup`. `Store Traffic Log` (Sales §7) provides Workforce's conversion denominator. |
| **Profit Intelligence** | **B3 fix is the load-bearing integration.** `commission.py` pays on `profit_math.compute_invoice_margin` (not `valuation_rate`); GP$/% per associate reads SCB; what-if pay sim and what-if price sim share `compute_invoice_margin` so numbers reconcile. Margin generated becomes a workforce KPI. |

### J2. Native Frappe/ERPNext/HRMS stack (leverage, don't rebuild)
- **HRMS Appraisal Cycle/Template** ↔ Quarterly Performance Review (one review = one appraisal entry).
- **HRMS Goal tree** ↔ Performance Target cascade (store→team→associate).
- **HRMS Employee Checkin/Shift Type/Shift Assignment** ↔ clock-in → Performance Log + worked hours.
- **HRMS Salary Structure/Salary Slip** ↔ `Sales Commission Split` + tiered pay → Salary Component → Salary Slip (native, audit-grade).
- **HRMS Employee Incentive / Additional Salary** ↔ SPIFF/bonus overlays and gamification payouts.
- **HRMS Attendance** ↔ `attendance_pct` (fixes hardcoded 0).
- **HRMS Employee Performance Feedback** ↔ coaching-session feedback records.
- **ERPNext report `sales_person_target_variance_based_on_item_group`** ↔ mirror logic for associate variance.
- **ERPNext report `customer_acquisition_and_loyalty`** ↔ customer-capture-rate KPI.
- **Frappe Insights Workbooks** ↔ deep no-code owner BI on workforce (no custom code); custom API reserved for realtime + role-aware console only (shared-platform §9.1 rule).
- **Frappe Number Card / Dashboard Chart** ↔ glance tiles on the Workforce Workspace.

---

## (K) Phased Build WITHIN this module — P0 / P1 / P2

> **Dependency:** Phase-1 of the shared platform (profit_math + SCB hook + `log_sale_event` wiring + rollup tables + `bus.py` + composables) must land first; Workforce P0 consumes it. Platform B1/B2/B3/B4 are Workforce's load-bearing fixes.

### P0 — MUST (unblocks the whole module; payroll-affecting)
1. **Wire `log_sale_event` → Sales Invoice `on_submit` and `log_sale_cancel_event` → `on_cancel`** in `hooks.py` (after `commission.calculate_commissions`). `zevar_core/hooks.py:65-73`.
2. **Backfill** `bench backfill-performance-logs` from historical POS invoices + `Sales Commission Split`. Idempotent on `(employee, event_date, reference_document)`.
3. **B3 fix for commission**: repoint `commission.py:104-109` to `profit_math.compute_invoice_margin`; "By Profit Margin" rules pay on true 6-bucket margin.
4. **Create `employee_period_rollup`** + `workforce.rebuild_employee_rollup` trigger on Performance Log insert. Repoint `get_team_performance` / `get_live_scoreboard` to read the rollup (kills N+1).
5. **Reconcile the two revenue paths**: `employee_live_monitor.py` reads Performance Log (not direct `Sales Commission Split` SQL). One canonical number.
6. **Build the Team Console UI** (`WorkforceIntelligence.vue` rebuilt): live ranked scoreboard (ARS/GP/UPT/conv/disc%/cap%), quota-attainment bars, store toggle, comp-run trigger, multi-store. Against existing + new rollup endpoints.
7. **Build the Associate Detail UI** (`AssociateDetailPerformance.vue` rebuilt): KPI heroes, trend chart (`get_performance_trend`), Compensation Calculation history, latest Quarterly Review with Acknowledge, dev plan.
8. **Populate the hardcoded-zero fields**: `high_ticket_sales` (item lines > `target.high_ticket_threshold`), `upsells` (multi-item invoices), `layaway_conversions`/`default_rate` (Layaway Contract), quarterly `activity_score`/`quality_score`/`recommended_rate`/`bonus_recommendation`.
9. **Add role gate to `acknowledge_review`** (`frappe.only_for` + clean `_resolve_employee_from_user` error path).
10. **Make `run_compensation_calculation` / `bulk_calculate_compensation` idempotent** (force/recompute instead of throw on existing).
11. **Client-side route guards** (shared-platform §5.3) — render `<NoAccess/>` instead of flashing UI before 403.

### P1 — SHOULD (the differentiation layer)
12. **Realtime live scoreboard + TV/kiosk mode** (`WorkforceTV.vue`): `associate_personal` per-employee fan-out + `admin_wall` aggregate; auto-rotating slides; rank-change animation; celebration overlays (manager-approved); privacy masking.
13. **Commission Estimator** (`workforce.project_payout` / `get_quota_progress`): quota-retirement ring, on-pace projection, next-tier teaser — associate self-view.
14. **What-if pay simulation** (`workforce.simulate_pay`, non-persisting): model rate/weight changes before committing.
15. **Structured 1:1 Coaching** (`Coaching Session` doctype + endpoints + `generate_talking_points` extending `_generate_review_insights`): cadence calendar, SMART goals, action items with owner+due, notes history, linked Quarterly Review.
16. **Gamification ledger**: points (`point_value` on Performance Log), `Gamification Badge` + `Badge Award`, `Gamification Campaign` (contests/SPIFFs), celebration triggers via `bus.publish`, rewards store.
17. **Commission Trace + Rule Edit History + dispute thread** (`Commission Trace`, `Commission Rule Edit History`, `dispute_comment`): drill any payout → deal/line/rule; immutable effective-dated edits; in-line @-mention disputes.
18. **Per-role weighted composite scorecard** (extend 3-axis engine with role templates: associate vs bench jeweler vs manager).
19. **Zero-cost KPIs surfaced**: UPT, attach rate, revenue-per-hour, customer-capture-rate (once `Store Traffic Log` lands in Sales P1).
20. **Quota/target cascade + plan rollover** via HRMS Goal tree; `clone_target_plan`.

### P2 — NICE (maturity / compliance)
21. **Scheduling + clock-in** (`Labor Forecast`, `Shift` via HRMS Shift Type/Assignment, kiosk clock-in with geo-fence/biometric): demand-based scheduling from `pos_session` history; produces `Clock In/Out` Performance Logs; populates `scheduled_hours`/`attendance_pct`.
22. **Clienteling book of business** (`Customer Relationship`, `Customer Appointment`, `Follow-up Task`): relationship tiers, 5–10 capacity, bridal/timepiece appointments, overdue follow-ups, lead routing.
23. **Payroll push to HRMS** (`push_compensation_to_payroll`): Commission → Salary Component → Salary Slip; **ASC 606/IFRS 15** recognition fields (recognized/deferred period) on Compensation Calculation.
24. **Adaptive microlearning**: spaced-repetition quizzes tied to new-inventory launches (Axonify pattern), points-awarded.
25. **Behavior-triggered smart notifications**: context-aware nudges after Nth sale with microlearning deep-link (real-time via `associate_personal`).
26. **Tests**: unit tests for tiered-rate interpolation, review-tier mapping, rollup rebuild idempotency, commission-trace reproducibility; integration test for the full sale→log→rollup→comp→payroll chain. (Today: zero test coverage for performance.py.)
27. **Frappe Insights Workbooks** for deep no-code owner BI on workforce analytics (custom API stays realtime-only).

---

## (L) Success Metrics / Acceptance Criteria (proving best-in-class)

| # | Criterion | How to prove |
|---|---|---|
| L1 | **Revenue axis is never 0.** Every associate with a submitted POS invoice this period has a `Sale Completed` Performance Log with non-zero `revenue_amount`. | After P0-1/2: `SELECT COUNT(*) FROM tabPerformance Log WHERE event_type='Sale Completed'` ≈ submitted POS invoice count for the same window. |
| L2 | **Commission pays on true margin.** A "By Profit Margin" commission rule's payout for an invoice equals `rate × SCB.gross_profit` (not `rate × (net − valuation_rate×qty)`). | Unit test: commission on a sample invoice reconciles to `profit_math.compute_invoice_margin(...).gross_profit × rule_rate` within $0.01. |
| L3 | **Manager and associate never disagree.** `employee_live_monitor.get_my_performance` revenue == `workforce.get_scoreboard` revenue for the same employee+day (both read Performance Log). | Integration test asserts equality across the two paths for a fixture employee. |
| L4 | **Scoreboard scales.** `get_team_performance` for 50 associates × 1 year of logs returns < 200ms. | Benchmark against `employee_period_rollup` (vs the old N+1 Python loop). |
| L5 | **Realtime, not polling.** A sale posted at the POS appears on the associate's self-view and the manager's scoreboard within 1 second over `associate_personal`/`sales_tick`, no manual refresh. | E2E test via the shared-bus publisher + `useRealtime` subscriber. |
| L6 | **Privacy holds.** Associate A's socket never receives Associate B's `associate_personal` event; TV mode shows "—" for bottom-3 sensitive fields; no customer PII on the wall. | Socket-capture test + TV render test. |
| L7 | **Idempotent comp.** `run_compensation_calculation` twice for the same period does not throw and produces one finalized calc (or a clean recompute with `force`). | Re-run test; assert single non-duplicate result. |
| L8 | **Payout is payroll-grade & auditable.** Any commission dollar traces to invoice + line + rule + rule-version via `Commission Trace`; rule edits are immutable with before/after JSON. | Drill-down test from a Salary Slip component back to the source invoice/line/rule. |
| L9 | **Zero hardcoded-zero fields remain.** `high_ticket_sales`, `upsells`, `scheduled_hours`, `attendance_percentage`, `layaway_default_rate`, quarterly `activity_score`/`quality_score`/`recommended_rate` are populated from real sources (or null-with-reason, never a misleading 0). | Schema assertion over a populated Compensation Calculation. |
| L10 | **Coaching loop is real.** A 1:1 with auto talking-points references a specific scorecard gap; action items carry owner+due; the Quarterly Review's `development_plan` is fed by the coaching cadence. | Fixture: generate talking-points for an associate whose ATV is 12% below target → assert the gap is named in the points. |
| L11 | **Gamification is jewelry-native.** Points accrue for appraisal-attach, layaway conversion, high-ticket close (not generic calls/demos); a celebration fires to TV/POS on a milestone. | Award a "5 high-ticket week" badge → assert Performance Log `point_value` + celebration publish. |
| L12 | **The UI unlocks the backend.** All 13 pre-existing `performance.py` endpoints + the new `workforce.*` set are reachable from the SPA (no "coming soon" stubs). | Grep: `WorkforceIntelligence.vue` and `AssociateDetailPerformance.vue` contain zero `construction` placeholders; every endpoint has a calling component. |

---

### Key file-path index (Workforce-specific, absolute)

- Backend (refactor `performance.py` into): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/workforce.py` (new) + keep `performance.py` for the legacy 13 endpoints during migration.
- Hooks (must edit): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/hooks.py` — add `zevar_core.api.workforce.log_sale_event` to `Sales Invoice.on_submit`, `log_sale_cancel_event` to `on_cancel`.
- Commission B3 fix: `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/commission.py:104-109` → call `profit_math.compute_invoice_margin`.
- Profit math (shared, consumed): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/services/profit_math.py` (new, platform P0).
- Doctype extensions: `…/doctype/performance_log/performance_log.json`, `…/performance_target/performance_target.json`, `…/compensation_calculation/compensation_calculation.json`, `…/quarterly_performance_review/quarterly_performance_review.json`.
- New doctypes dir: `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/unified_retail_management_system/doctype/` — `coaching_session`, `gamification_campaign`, `gamification_badge`, `badge_award`, `reward_catalog_item`, `reward_redemption`, `commission_trace`, `commission_rule_edit_history`, `labor_forecast`, `customer_appointment`, `follow_up_task`, `customer_relationship`.
- Frontend (rebuild stubs): `…/frontend/zevar_ui/src/pages/dashboards/WorkforceIntelligence.vue`, `…/AssociateDetailPerformance.vue`; new `…/pages/dashboards/WorkforceTV.vue`; components under `…/src/components/workforce/` (`LiveScoreboardTable.vue`, `GoalCascade.vue`, `CommissionEstimator.vue`, `ContestPanel.vue`, `BadgeWall.vue`, `CoachingSessionCard.vue`).
- Routes (existing, keep): `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/router.js:475,481`; add `/workforce/tv`.
- Permission helper (extend): `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/utils/permissions.js` — add `canAccessWorkforce()`.
