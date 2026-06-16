# Zevar Monitor Suite — Phased Implementation Roadmap

> **Role:** Delivery Architect. This roadmap turns the 4-module + shared-platform spec into an executable, dependency-ordered plan. Every claim below is grounded in a direct code read of this bench (verified, not inherited from the stale baseline).

---

## 0. Grounding — what the code actually says today (verified, evidence-backed)

These supersede the stale `module_audit_raw.json`. They are the load-bearing facts the sequencing rests on.

| # | Fact | Evidence (read directly) |
|---|---|---|
| F1 | **SCB hook is unwired** — `calculate_sale_cost_breakdown` exists at `profit_intelligence.py:21` but is only self-called (`:734`). `hooks.py` `on_submit` lists only `commission.calculate_commissions`, `stock_reduction`, `reservation_manager`. → **no SCB rows ever created → all profit endpoints return empty.** | `zevar_core/hooks.py` `doc_events["Sales Invoice"]["on_submit"]` |
| F2 | **`log_sale_event`/`log_sale_cancel_event` are unwired** — defined at `performance.py:100,143`, never registered. → **workforce revenue axis is structurally always 0** (payroll-affecting). | `hooks.py` (no `log_sale_event` anywhere) |
| F3 | **Margin defined 7 ways** — `commission.py:104-109` uses `valuation_rate` only → pays commission on inflated margin. | `commission.py:104-109` read directly |
| F4 | **Dead publishers / global broadcast** — `publish_anomaly_alert` and `publish_employee_event` have **zero callers**; all 3 `publish_realtime` calls in `live_monitor.py:30,39,55` broadcast globally (no `room=`/`user=`). | grep over `zevar_core/` |
| F5 | **ReportsHub full-page reload** — 3 `window.location.href` at `ReportsHub.vue:211,215,245` tear down the SPA on every dashboard switch. | read directly |
| F6 | **Role logic triplicated** — `router.js:4-29` (`ROLE_TIERS`/`getAccessTier`/`canAccess`), `utils/permissions.js`, `Dashboards.vue` inline. | grep confirmed |
| F7 | **17 duplicated `fmt()`**, 4 fragmented live screens, no chart library, no shared time context. | `grep -rc` |
| F8 | **Workforce backend is rich and dark** — `performance.py` = 1054 lines, 12 whitelisted endpoints, 4 doctypes (Performance Log immutable, 3-axis weighted scorecard, tiered comp engine, quarterly-review generator) — **~0% UI exposure**. | `wc -l` + `@frappe.whitelist` count |
| F9 | **`services/` package exists** — clean home for `profit_math.py`. | `ls zevar_core/services/` |

These 9 facts drive the entire ordering below.

---

## 1. Recommended Module Sequencing (the headline decision)

**Order: Shared Platform (Phase 0) → Profit Intelligence (Phase 1) → Sales Monitor (Phase 2) → Workforce Intelligence (Phase 3) → Live Monitor / Command Center (Phase 4) → Polish & Scale (Phase 5).**

### Why this order — the leverage analysis

| Module | Backend readiness | Output today | What unblocks it | Why it lands here |
|---|---|---|---|---|
| **Shared Platform** | N/A — the spine | 4 fragmented screens, 7-way margin, dead realtime | itself | **All 7 P0 bugs live here** (F1–F7). Nothing else is correct until `profit_math`, the wired SCB hook, `log_sale_event`, rollups, and `bus.py` exist. Sequenced first, non-negotiable. |
| **Profit Intelligence (1st module)** | **Strong design, zero output** | entirely blank (F1) | platform `profit_math` + SCB hook | **Highest fix-value-per-effort and the trust spine.** Everything else reads margin from SCB. Without the wired hook, the whole suite shows zeros. Land it first so commission, sales, and workforce all build on one true number. |
| **Sales Monitor (2nd module)** | No data layer; 5-way "today's sales" drift | fragmented | platform rollups + `sales_monitor.py` | Depends on Profit's `profit_math` for the margin column and on the rollup tables the platform introduces. Provides the **volume/revenue spine** Workforce and Live both read. |
| **Workforce Intelligence (3rd module)** | **Richest backend in the suite, dark** (F8) | unreachable | platform `log_sale_event` hook + rollup (B2) | The B2 wiring bug (F2) is payroll-affecting and **must land in the platform first**; then the existing 1054-line backend is *unlocked* rather than built. Defers to Profit only because commission correctness depends on `profit_math`. |
| **Live Monitor (4th module)** | 4 prototypes, not a product | dead realtime (F4) | platform `bus.py` + Sales + Workforce feeds | Consumes `sales_tick`, `associate_personal`, `price_shock`, `anomaly_alert` — i.e. the *outputs* of the three preceding modules. Putting it earlier means a wall with no live sales feed and no scoreboard. It is the capstone, not the foundation. |

### The single sentence of rationale
**The platform kills the 7 P0 bugs; Profit becomes the one true margin the other three read; Sales owns the volume spine; Workforce unlocks a rich-but-dark backend on a corrected pay basis; Live is the capstone that makes all of it realtime.**

> **Alternative considered:** Workforce-first ("rich backend, just wire it"). Rejected because Workforce's commission engine pays on the wrong margin (F3) until Profit's `profit_math` exists — landing Workforce first would lock in *more* wrong payouts. The platform + Profit-first ordering fixes the pay basis before any comp run is trusted.

---

## 2. Dependency-Ordered Phase Plan

Effort bands: **S** = 1 sprint (~2 eng-weeks), **M** = 2 sprints, **L** = 3+ sprints.

### Phase 0 — Shared Platform (the spine)  [Effort: L]

**Scope.** Kill all 7 P0 bugs and stand up the contract layer every module reads.

**Entry criteria.** F1–F7 confirmed (done — §0). Bench boots; `services/` exists.

**Deliverables (concrete, absolute paths).**
- `zevar_core/services/profit_math.py` — `get_item_cogs(item)` + `compute_invoice_margin(invoice, *, include_overhead, include_payment, include_labor)`. The **single** margin definition.
- `zevar_core/api/realtime/events_schema.py` (`SCHEMA_VERSION`, `EventEnvelope`, typed payloads) + `scripts/gen_realtime_types.py` → `frontend/zevar_ui/src/types/realtime-events.ts` (CI-gated, no drift).
- `zevar_core/api/realtime/bus.py` — `publish(channel, event_type, data, *, store, employees, broadcast_admin, broadcast_store)`; room/user scoping; `_persist_backfill` to `live_event_log`.
- `zevar_core/api/realtime/hooks.py` — `on_invoice_submit/on_cancel`, `on_repair_update`, `on_gold_purchase_submit`, `run_anomaly_push` (`*/2`), `run_health_heartbeat` (`*/5`).
- `hooks.py` deltas: wire SCB `on_submit` + `on_cancel`; wire `log_sale_event`/`log_sale_cancel_event`; add schedulers.
- Delete `publish_anomaly_alert`/`publish_employee_event` (`live_monitor.py:37-60`); migrate `publish_repair_event` → `bus.publish`.
- Materialized tables: `daily_store_sales_rollup`, `employee_period_rollup`, `metal_rate_history`, `live_event_log` (24h backfill).
- Refactor the 7 margin sites to call `profit_math` (F3): `commission.py:104`, `top_profitability_by_product.py:70`, `analytics_hub.py:1012`, `pricing_tools.py:210`, `repair_accounting.py:704`, `gemstone_value_service.py:125`, `finance.py:351`.
- Frontend: `composables/{useRealtime.js,useDashboardData.js,usePolling.js,useBackfill.js}`; `utils/format.js` (replaces 17 `fmt()`); `utils/status-colors.js`; `stores/time.js`.
- SPA shell fix: delete `ReportsHub.vue:211,215,245` `window.location.href` → `router.push`; `<router-view>` mount. Single permission helper (`utils/permissions.js`); delete `router.js:4-29` `ROLE_TIERS`.

**Exit criteria / demo.** `bench --site x zevar-backfill-scb` populates SCB for all history; `gross_margin_pct` is identical on commission payout, `top_profitability_by_product`, analytics hero, and a sample SCB row (the "one number, five surfaces" assertion test passes). A socket push reaches a subscribed client < 3s. `grep "function fmt("` in `pages/dashboards/` returns 0.

**Dependencies.** None (entry point).

---

### Phase 1 — Profit Intelligence (the trust spine)  [Effort: M]

**Scope.** Turn the strong-but-silent COGS design into a working module: real margin everywhere, exec views, simulator that reconciles to posted SCB.

**Entry criteria.** Phase 0 shipped (SCB hook wired, `profit_math` exists, margin sites refactored).

**Deliverables.**
- Extend `sale_cost_breakdown` schema: `making_charge`, `alloy_wastage_amount`, `store`, `item_group`, `net_contribution_margin_pct`.
- `profit_intelligence.get_margin_waterfall`, `get_pvm_bridge` (price/volume/mix/new-disc/cost + residual), `simulate_whatif` (calls `compute_invoice_margin`; margin curve + confidence band; persists `What-if Simulation Run`), `get_gold_pass_through`, `get_unrealized_gain_loss` (MTM via `metal_rate_history`), `create_recommendation` (fixes 404), case-insensitive `review_recommendation`.
- **Rewrite `get_margin_heatmap` to pivoted shape** matching `MarginHeatmap.vue`.
- Multi-store: convert `Cost Center Allocation` singleton → per-store; add `group_by='store'|'category'`.
- New doctypes: `what_if_simulation_run`, `margin_floor_rule`, `overhead_driver` (ABC), `interchange_tier`.
- Schedule `tasks.generate_pricing_recommendations` (`7 2 * * *`).
- Frontend: rebuild `ProfitIntelligence.vue` shell + tabs (Overview / Margin Analysis / PVM / What-If / Pricing Actions / Inventory MTM); new `components/charts/WaterfallChart.vue`.

**Exit / demo.** Owner opens Profit module and sees a non-zero Margin Waterfall and a PVM bridge for the prior quarter; a What-If slider move recomputes margin in < 200ms and equals the posted SCB margin for that item.

**Dependencies.** Phase 0.

---

### Phase 2 — Sales Monitor (the volume spine)  [Effort: M]

**Scope.** The first module a store actually *uses daily*. Collapse 5-way "today's sales" drift into one sub-100ms spine; deliver UPT/run-rate/projected-close that the data already supports.

**Entry criteria.** Phase 0 (rollups, `timeStore`, `utils/format.js`, SPA shell). Reads Profit's `gross_profit` column from the rollup.

**Deliverables.**
- `zevar_core/api/sales_monitor.py` — `get_summary`, `get_hourly` (24h zero-bucketed), `get_trend` (prior/YoY/WoW overlay), `get_breakdown`, `get_leaderboard`, `get_pace`, `get_conversion`, `get_velocity`, `run_query` (report-builder engine), `rebuild_rollup`.
- Refactor to delegate: `revenue_dashboard.py`, `reports._eod_revenue`, `analytics_hub` sales hero, `sales_history.get_sales_summary`. Delete duplicate SQL.
- Custom field `Sales Invoice.custom_sales_channel`; new doctypes `store_traffic_log`, `sales_target`, `saved_report`; `integrations/hardware/people_counter.py` (v1: manual POS-staff entry).
- Frontend: `pages/dashboards/SalesMonitor.vue` shell + route `/reports/dashboards/sales-monitor`; KPI strip (8 `KPICard`s incl. **UPT, run-rate, projected-close** — first time they exist); `TrendLineChart`, `HourlyBarChart` (replaces hardcoded 9–21 window), `AssociateLeaderboard.vue`, `components/reports/ReportBuilder.vue` (shared filter grammar).

**Exit / demo.** EOD Z-report, the wall, and `get_summary` agree to the penny on today's total; a store manager switches Sales Monitor to "7d" and the whole module re-fetches with no reload; conversion funnel renders (once `store_traffic_log` has data).

**Dependencies.** Phase 0 (strong), Phase 1 margin column (weak — leaderboard margin reads SCB via rollup).

---

### Phase 3 — Workforce Intelligence (unlock the rich backend)  [Effort: M–L]

**Scope.** Wire the payroll-affecting bug (F2), point the existing 1054-line engine at a corrected pay basis, and finally give it a UI.

**Entry criteria.** Phase 0 (`log_sale_event` wired + `employee_period_rollup` + B3-fixed commission on `profit_math`).

**Deliverables.**
- Repoint `employee_live_monitor.py` to read Performance Log (kill the two divergent revenue paths). `backfill-performance-logs` bench command (idempotent on `(employee, event_date, reference_document)`).
- Populate the hardcoded-zero fields: `high_ticket_sales`, `upsells`, `scheduled_hours`, `attendance_percentage`, `layaway_default_rate`, quarterly `activity_score`/`quality_score`/`recommended_rate`/`bonus_recommendation`.
- Make `run_compensation_calculation` / `bulk_calculate_compensation` idempotent (force/recompute, not throw). Add role gate to `acknowledge_review`.
- New `zevar_core/api/workforce.py` (refactor `performance.py`): `get_scoreboard`, `get_quota_progress`, `project_payout`, `simulate_pay`, `cascade_targets`, `clone_target_plan`, coaching + gamification + commission-trace endpoints.
- New doctypes: `coaching_session`, `gamification_campaign`, `gamification_badge`, `badge_award`, `reward_catalog_item`, `reward_redemption`, `commission_trace`, `commission_rule_edit_history`.
- Frontend: rebuild `WorkforceIntelligence.vue` (Manager Team Console: live ranked scoreboard, quota bars, comp-run trigger) + `AssociateDetailPerformance.vue` (self-view: KPI heroes, Commission Estimator, Quarterly Review + Acknowledge); new `WorkforceTV.vue`.

**Exit / demo.** An associate with a submitted POS invoice today shows a non-zero `Sale Completed` Performance Log and non-zero revenue on their self-view; a manager's scoreboard updates sub-second when a sale posts (via `associate_personal`, never global); the same commission dollar traces to invoice + line + rule.

**Dependencies.** Phase 0 (F2 + B3 are Workforce's load-bearing fixes).

---

### Phase 4 — Live Monitor / Command Center (the capstone)  [Effort: M]

**Scope.** Collapse 4 screens into one role-aware, push-first wall that surfaces live sales, repairs, alerts, health, associates, gold, memo, conversion.

**Entry criteria.** Phases 1–3 producing the event streams (`sales_tick`, `associate_personal`, `price_shock`, `anomaly_alert`).

**Deliverables.**
- `zevar_core/api/command_center.py` (replaces `live_monitor.py`): `get_wall_state`, `get_backfill`, `get_sales_ticker`, `get_repair_lane`, `get_associate_grid`, `get_health`, `get_margin_risk`, `get_pace`, ack/snooze/resolve alerts, save/get layout.
- New doctype `Operations Alert` (severity/type/status ack-snooze-resolve/assigned/correlation_id/evidence/timeline/MTTA-MTTR).
- Rebuild `pages/dashboards/CommandCenter.vue` as the role-aware wall; **delete** `pages/LiveMonitor.vue` (redirect) + `pages/dashboards/AdminMonitor.vue` (merge → delete); keep `EmployeeLiveMonitor.vue` as the associate variant inside the same route.
- TV/kiosk mode (`?tv=1`): slide rotation, sticky-pin on critical, visible "last updated" + stale-data warning (amber >60s, red >180s).
- Live SALES in the wall (the #1 owner metric, today absent) via `sales_monitor.get_summary`; never omit a quiet store (fixes `_get_store_metrics` skip).

**Exit / demo.** Owner mounts the wall on a TV, walks away, and the first time gold spikes 3% they learn it from Zevar's margin-at-risk alert — not the evening news, not a 30-minute-stale poll. A sale posts and the ticker + hero KPI update < 3s.

**Dependencies.** Phases 1–3 (consumes their event producers).

---

### Phase 5 — Polish & Scale  [Effort: L, parallelizable]

**Scope.** Differentiators, compliance, scale-out.

**Deliverables.**
- Profit: Margin Floor enforcement at POS; AIMS aged-inventory engine (spiffs + markdowns + signage); markdown optimization; interchange-tier payment cost; Pricing Recommendation as continuous monitors.
- Sales: People-counter device integration; Slack/WhatsApp saved-report push; TV mode; basket affinity; velocity Grid (Col×Row) matrix.
- Workforce: Scheduling + geo-fenced/biometric kiosk clock-in; clienteling book-of-business; payroll push to HRMS Salary Slip; ASC 606/IFRS 15 recognition fields; spaced-repetition microlearning tied to new inventory.
- Live: Live Monitor Layout editor; offline/resilience cache; predictive (seasonality-aware) anomaly baselines; EOD overnight digest.
- Scale: partition/prune `live_event_log`; Insights Workbooks for deep no-code owner BI (custom API stays realtime-only — no duplication).

**Exit / demo.** Full feature-coverage checklist vs the spec's B-list passes; multi-store scale test (5 stores × 3 years) holds sub-100ms rollup reads.

---

## 3. Phase Summary Table

| Phase | Module | Effort | Entry | Headline exit | Key files (new/edit) |
|---|---|---|---|---|---|
| 0 | Shared Platform | L | F1–F7 confirmed | One margin, wired hooks, rollups, bus, SPA shell | `services/profit_math.py`; `api/realtime/{bus,events_schema,hooks}.py`; `hooks.py`; `composables/*`; `utils/format.js`; `stores/time.js`; `ReportsHub.vue` |
| 1 | Profit Intelligence | M | Phase 0 | Non-zero waterfall + reconciled what-if | `api/profit_intelligence.py`; SCB schema; `charts/WaterfallChart.vue`; `ProfitIntelligence.vue` |
| 2 | Sales Monitor | M | Phase 0 (+1 weak) | 5-way drift dead; UPT/run-rate live | `api/sales_monitor.py`; `store_traffic_log`, `sales_target`, `saved_report`; `SalesMonitor.vue` |
| 3 | Workforce Intelligence | M–L | Phase 0 | Revenue axis ≠ 0; UI unlocks backend | `api/workforce.py`; `employee_period_rollup`; `WorkforceIntelligence.vue`; `WorkforceTV.vue` |
| 4 | Live Monitor | M | Phases 1–3 | One push-first wall, live sales, gold-at-risk | `api/command_center.py`; `Operations Alert`; `CommandCenter.vue` (rebuild) |
| 5 | Polish & Scale | L | Phases 1–4 | Feature-parity superset; multi-store scale | AIMS, scheduling, Insights Workbooks, `live_event_log` partitioning |

---

## 4. Quick-Win / Fast-Value Sprint (P0, days not weeks)

The concrete first batch. No design debates — these are pure wiring + contract fixes with outsized visible impact. Ship in **one sprint** before any module build.

| # | Quick win | Effort | Evidence | Visible result |
|---|---|---|---|---|
| Q1 | **Wire SCB `on_submit` + `on_cancel`** in `hooks.py` (after `commission.calculate_commissions`); `on_cancel` sets SCB `docstatus=2` | S | F1 | Profit dashboards stop returning empty |
| Q2 | **Wire `log_sale_event` → `on_submit`, `log_sale_cancel_event` → `on_cancel`** in `hooks.py` | S | F2 | Workforce revenue axis stops being 0 |
| Q3 | **Schedule `generate_pricing_recommendations`** (`7 2 * * *`) | S | F1 adjacent | Pricing recs actually generate |
| Q4 | **Backfill** `bench zevar-backfill-scb` + `backfill-performance-logs` (idempotent) | S | F1, F2 | History populated; underpaid associates reconciled |
| Q5 | **Fix the 4 broken contracts**: `create_recommendation` (404), case-insensitive `review_recommendation`, rewrite `get_margin_heatmap` to pivoted shape, map `confidence_level`→numeric | S | F1 | Profit UI cells render, approve/reject works |
| Q6 | **Resurrect dead realtime**: migrate `publish_repair_event` → `bus.publish`; add `run_anomaly_push` (`*/2`) + `run_health_heartbeat` (`*/5`) schedulers; delete `publish_anomaly_alert`/`publish_employee_event` | S | F4 | Anomalies push without a screen open |
| Q7 | **Add live sales to the command center**: hero KPIs + ticker delegate to `sales_monitor.get_summary`/`get_hourly`; never skip quiet stores | S | F4 (repair-only today) | The #1 owner metric appears live |
| Q8 | **Compute zero-cost KPIs** UPT, run-rate, projected-day-close from existing `Sales Invoice Item.qty` + invoice totals | S | F8 adjacent | KPIs the data already supported, now surfaced |
| Q9 | **Adopt ECharts + extract `utils/format.js`**: install `echarts`/`vue-echarts`; replace 17 `fmt()` copies | S | F7 | One chart lib, one formatter |
| Q10 | **Collapse 4 live screens → one Command Center route**: delete `ReportsHub.vue:211,215,245` `window.location.href` → `router.push`; register `/reports/dashboards/command-center` | S | F5, F6 | Switching dashboards stops tearing down the SPA |

**Sprint exit.** A stakeholder posts a sale at the POS and sees it on a non-empty Command Center wall within seconds; the Profit module shows a non-zero margin; a salesperson's scoreboard shows non-zero revenue — all on day 5, before any module "build" begins.

---

## 5. Milestones & Demoable Checkpoints

| Gate | What a stakeholder sees |
|---|---|
| **M0 — Platform spine live** | One margin number everywhere; backfill reconciles history; a socket push reaches the client < 3s; switching dashboards preserves SPA state. |
| **M1 — Profit trust demo** | Non-zero Margin Waterfall + PVM bridge; What-If slider matches posted SCB margin to the cent. |
| **M2 — Sales daily-use demo** | Store manager lives in Sales Monitor all day; EOD, wall, and `get_summary` agree; UPT/run-rate/projected-close visible; 7d range works. |
| **M3 — Workforce unlock demo** | Associate self-view shows non-zero revenue + on-pace payout; manager scoreboard updates live; commission traces to invoice+line+rule. |
| **M4 — Command Center capstone demo** | Owner wall on a TV: live sales, repairs, alerts, gold-at-risk, associates, conversion, health — one screen, push-first. The "gold spikes 3%" moment. |
| **M5 — Scale & superset demo** | 5-store × 3-year data holds < 100ms; full feature-coverage checklist vs spec passes; Insights Workbooks for deep BI. |

---

## 6. Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R1 | **Payroll-affecting bugs (F2/F3)** — wrong/zero commission basis goes into Salary Slips | Critical (legal/compensation) | High pre-fix | Q1–Q4 land first; integration test asserts commission ≡ `profit_math.gross_profit × rate`; freeze comp runs until Phase 3 P0 ships; backfill reconciles historical underpayment explicitly. |
| R2 | **7-way margin refactor touches `commission.py` payouts** | High (money correctness) | Med | Refactor behind the `profit_math` contract first; keep `valuation_rate` path as a flagged fallback for one release; unit-test every payout before/after. |
| R3 | **Backfill / data migration** (SCB, Performance Log) on large history | Med (runtime, partial fills) | Med | Idempotent on natural keys (`(employee,event_date,reference_document)`, `sales_invoice`); bench command re-runnable; dry-run + diff report; phase by date range. |
| R4 | **Conversion-data dependency** (`store_traffic_log`) — conversion KPI structurally impossible until traffic captured | Med (headline KPI gap) | High | Ship manual POS-staff entry in Sales P1 as the pragmatic fallback (unblocks conversion immediately); people-counter device in Phase 5. Never block other KPIs on it. |
| R5 | **Frappe-desk vs SPA coexistence** — desk page role gate (`admin_monitor.json`) and SPA `permissions.js` diverge | Med (Sales Manager redirected after load) | Med | Reconcile both to the same `only_for` list (§5.4); add Sales Manager everywhere; automated role-matrix test. |
| R6 | **Multi-store scale** (rollup reads, realtime fan-out) at 5+ stores × years | Med (latency) | Med | Sub-100ms guarantee comes from rollup tables + indexes `(store,date)`, `(salesperson,date)`; nightly safety rebuild; partition/prune `live_event_log`. |
| R7 | **Realtime reliability / API latency** — socket.io reconnect, stale data | Med (trust) | Med | `useRealtime` paused-when-hidden + backfill on resume; visible stale-clock warning (>60s/>180s); exponential-backoff poll fallback via `usePolling`. |
| R8 | **Privacy leak via global broadcast** (F4) — employee/customer events to all clients | High (compliance) | High pre-fix | Iron rule enforced in `bus.publish`: employee-attributed events `user=`-scoped or manager-only `room=`; socket-capture test asserts no global employee event. |
| R9 | **Generated TS drift** (`events_schema.py` vs `realtime-events.ts`) | Low (subtle UI bugs) | Med | CI gate `gen_realtime_types.py --check` fails the PR if they diverge. |
| R10 | **Stale planning artifacts mislead implementers** (`module_audit_raw.json` claims hook is wired) | Med (wrong work) | High | Annotate artifacts as unreliable in Phase 0; the §0 grounding table above is authoritative. |
| R11 | **Scope creep on Workforce** (scheduling, clienteling, microlearning are large) | Med (timeline) | Med | MVP per module (§8) gates P2 items behind P0/P1; the 13 existing endpoints + B2 fix are the MVP. |

---

## 7. Portfolio Success Metrics (proof Zevar became the leader)

| Metric | Target | How measured |
|---|---|---|
| **One true margin** | `gross_margin_pct` identical on commission payout, `top_profitability_by_product`, analytics hero, SCB, and the what-if simulator — 5 surfaces, 0 drift | Integration test gates the build |
| **SCB coverage** | 100% of submitted invoices; 0 orphan SCB rows after cancel | coverage query post-backfill |
| **Workforce revenue axis** | every associate with a submitted POS invoice has a non-zero `Sale Completed` Performance Log | count parity vs `tabSales Invoice` |
| **Commission correctness** | a "By Profit Margin" payout ≡ `rate × profit_math.gross_profit` within $0.01 | unit test |
| **Sub-100ms monitor queries** | every `sales_monitor.*` / `command_center.get_wall_state` < 100ms p95 at 5 stores × 3 years | benchmark vs rollup |
| **Realtime freshness** | sale posts to wall < 3s p95 (vs 30s poll today); wall hydrates from backfill < 1.5s | client telemetry |
| **Conversion rate live** | non-null whenever `store_traffic_log` has data for the period | conversion KPI |
| **Payroll-grade commissions** | any commission dollar traces to invoice + line + rule + rule-version; flows to HRMS Salary Slip | drill-down test |
| **Contribution margin** | `net_contribution_margin_pct` (revenue − 6 buckets − payment − overhead) computed per SCB | schema + KPI |
| **Coaching KPI parity+** | The Edge salesperson-performance set present (ARS, GP$/GP%, UPT, conversion, attach, discount ratio, capture, revenue-per-hour) | feature checklist |
| **SPA integrity** | 0 `window.location.href` in `ReportsHub`; 0 `function fmt(` in `pages/dashboards/` | grep gates |
| **Privacy** | 0 globally-broadcast employee events; associate never sees peer rows/amounts | socket-capture + API tests |

---

## 8. MVP Definition per Module (best-in-class minimum vs later gap-closers)

### Phase 1 — Profit Intelligence MVP (already best-in-class)
- Wired SCB hook + `profit_math` (one margin, everywhere)
- Margin Waterfall + PVM bridge + What-If (reconciled to posted SCB)
- The 4 broken contracts fixed; generator scheduled
- **Gap-closers (later):** Margin Floor at POS, AIMS, ABC overhead, MTM, interchange tiers, continuous-monitor recommendations

### Phase 2 — Sales Monitor MVP
- `sales_monitor.*` spine (kills 5-way drift); 8-KPI strip incl. UPT/run-rate/projected-close
- 24h zero-bucketed hourly; multi-granularity trend with prior/YoY overlay
- Associate leaderboard (Rev/UPT/Conv/Attach/Margin/Capture); SPA shell, no reload
- `custom_sales_channel`; manual `store_traffic_log` entry; conversion funnel
- **Gap-closers:** ReportBuilder grammar engine, velocity Grid matrix, tri-mode valuation, people-counter device, saved/scheduled Slack-WhatsApp push, TV mode

### Phase 3 — Workforce Intelligence MVP
- `log_sale_event` wired + backfill + hardcoded-zero fields populated + B3-fixed commission
- `employee_period_rollup`; Team Console + Associate self-view (UI unlocking the 13 endpoints)
- Commission Estimator; idempotent comp runs; role-gated review acknowledge
- **Gap-closers:** TV mode + gamification + coaching cadence + scheduling/clock-in + clienteling + payroll push + ASC 606 + microlearning

### Phase 4 — Live Monitor MVP
- One route, role-aware wall (owner/manager/associate); live SALES via `sales_monitor`
- `bus.publish` pipeline; `Operations Alert` ack/snooze/resolve; "last updated" stale warning
- Never omit quiet stores; visible live sales + repairs + alerts + gold + health
- **Gap-closers:** TV slide rotation/sticky-pin, system-health tile depth, incident correlation, conversion funnel, layout editor, resilience cache, predictive baselines

---

## 9. Sprint-by-Sprint Suggested Timeline (relative sprints; small team)

Assume a small team (2–3 engineers), ~2-week sprints. S = same sprint.

| Sprint | Focus | Output |
|---|---|---|
| **S1** | **Quick-Win Sprint (§4)** — Q1–Q10 | SCB/`log_sale_event` wired; backfill; 4 contracts fixed; realtime resurrected; live sales on wall; UPT/run-rate; ECharts + `utils/format.js`; SPA shell fix. *Demoable: non-empty Profit + Command Center.* |
| **S2–S3** | **Phase 0 finish** — `profit_math` full impl; 7-way margin refactor; rollup tables + triggers; `bus.py` + event schema + TS gen (CI gate); composables; `timeStore`; single permission model | *M0 — Platform spine live.* |
| **S4–S5** | **Phase 1 — Profit Intelligence** — SCB schema extend; waterfall; PVM; what-if; heatmap rewrite; multi-store overhead; pricing recs; `WaterfallChart.vue` | *M1 — Profit trust demo.* |
| **S6–S7** | **Phase 2 — Sales Monitor** — `sales_monitor.py`; delegate refactor; KPI strip; trend/hourly; leaderboard; channel field; traffic log; SPA shell | *M2 — Sales daily-use demo.* |
| **S8–S9** | **Phase 3 — Workforce Intelligence** — `workforce.py`; rollup repoint; zero-field population; idempotent comp; Team Console + self-view; Commission Estimator | *M3 — Workforce unlock demo.* |
| **S10–S11** | **Phase 4 — Live Monitor** — `command_center.py`; `Operations Alert`; Command Center rebuild; role variants; TV mode; never-skip-quiet-stores | *M4 — Command Center capstone demo.* |
| **S12+** | **Phase 5 — Polish & Scale** (parallelizable across engineers): AIMS, scheduling/clock-in, clienteling, payroll push, people-counter, Insights Workbooks, `live_event_log` partitioning, predictive baselines | *M5 — Scale & superset demo.* |

> **Critical path:** S1 (Quick Wins) → S2–S3 (Phase 0) → S4–S5 (Phase 1). Everything else can flex around team capacity once the spine + trust layer are solid. The single non-negotiable sequencing rule: **never run a compensation calculation against production payouts until Phase 0 (B2 + B3 fixes) and Phase 3 P0 have shipped.**

---

*All file paths above are absolute under `/workspace/development/frappe-bench/apps/zevar_core/`. The §0 grounding table is the authoritative baseline; `module_audit_raw.json` and similar prior artifacts are explicitly unreliable and should be annotated as such in Phase 0.*
