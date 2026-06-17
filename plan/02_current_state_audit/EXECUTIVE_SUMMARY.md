# Current-State Audit — Executive Summary

> The "so what" of the deep code audit. Full per-module detail with file:line references: `CURRENT_STATE_AUDIT.md`.

## Module maturity (where each module really stands today)

| Module | Backend | Frontend | vs best-in-class | #1 blocker |
|---|---|---|---|---|
| **Profit Intelligence** | Strong *design*, ~50% | ~20% (only module with a Pinia store) | **~50%** | `calculate_sale_cost_breakdown` hook is **NOT wired** → zero output. Margin defined **7 inconsistent ways**. |
| **Workforce Intelligence** | Rich (~1054 lines, tiered comp engine) — **but data-starved: event stream unwired** | **~0%** (two "coming soon" stubs) | ~40% backend / 0% UI | **Entire `Performance Log` event stream unwired** → table empty → every scoreboard/comp/review runs on zero events. |
| **Live Monitor** | Partial (repair-only realtime) | Fragmented (4 overlapping screens) | **~25%** | No live **sales** in the command center; `publish_anomaly_alert` is **dead code**; events broadcast globally. |
| **Sales Monitor** | Shallow (today-only; 5 duplicate SQL impls) | Thin (no date picker, no trend) | **~15% — weakest** | **No traffic/conversion data source** (conversion rate structurally impossible); no UPT; no channel dimension. |
| **Cross-cutting** | Realtime plumbing exists; profit math centralized *on paper* | No chart lib; triplicated role logic; full-page-reload nav | — | No shared KPI/calc layer; no design system; two competing dashboard hubs. |

## Critical P0 bugs (fix first — these make current numbers wrong/zero)

> ⚠️ These supersede an earlier rate-limited audit pass that falsely claimed the Profit hook was wired and margin was centralized. **Both are false.**

1. **Profit — `calculate_sale_cost_breakdown` is NOT registered in `hooks.py`** (`doc_events['Sales Invoice']['on_submit']`). Sale Cost Breakdown records are never auto-created, so `get_profit_summary` / `get_margin_analysis` / `get_margin_heatmap` / `get_cost_component_trends` all return **zero** in a live system. No `on_cancel` cleanup either (orphan rows on cancel/amend).
2. **Profit — `generate_pricing_recommendations` is NOT scheduled** (`scheduler_events` only lists `fetch_live_metal_rates`). Pricing Recommendation records never auto-generate → Pricing tab permanently empty.
3. **Profit — 4 broken frontend↔backend contracts:** `create_recommendation` endpoint doesn't exist (UI calls it → 404); `review_recommendation` expects lowercase `approve`/`reject` but UI sends `Approved`/`Rejected` (buttons always throw "Invalid action"); `get_margin_heatmap` returns a flat array but `MarginHeatmap.vue` expects a pivoted shape (every cell renders `--`); `confidence_level` is a `High|Medium|Low` string but the UI treats it as a numeric % (bar always 0%).
4. **Workforce — the ENTIRE Performance Log event stream is dead.** Verified by direct code trace: `_create_performance_log` (performance.py:75) is called **only** by `log_sale_event` / `log_sale_cancel_event` / `log_layaway_event` / `log_repair_event` / `log_attendance_event` (performance.py:127/163/197/228/269) — and **none of those functions are registered in `hooks.py` nor called anywhere** (grep across the package returns zero references). The active `hooks.py` `doc_events` covers only `Item` and `Sales Invoice` (no `Layaway Contract`, `Repair Order`, or `Attendance` key); the second `unified_retail_management_system/hooks.py` has its `doc_events` commented out. **Result: the `Performance Log` table is empty in production** → every scoreboard, compensation calculation, and quarterly review is computed from zero events. (An earlier audit pass claimed layaway/repair/attendance hooks *were* wired at `hooks.py:77/80/83` — those lines are actually `scheduler_events`; that claim was incorrect.) Additionally `generate_quarterly_reviews` and `generate_pricing_recommendations` are **not** in the active `scheduler_events`. The fix is: wire **all** `log_*_event` hooks + `calculate_sale_cost_breakdown`, schedule both generators, and **backfill** Sale Cost Breakdown + Performance Logs from historical Sales Invoices / Commission Splits.
5. **Live — `publish_anomaly_alert` is dead code** (defined `live_monitor.py:37`, never called); anomaly detection has **no scheduler**; `publish_employee_event` is never invoked from the `pos.py` sale path; `AdminMonitor` polls 30s instead of subscribing to `pos_sale_event` (which *is* published); all `live_monitor.py` `publish_realtime` calls (lines 30/39/55) omit `user=`/`room=` → **employee-attributed events broadcast to every socket**, undermining the privacy `employee_live_monitor.py` claims.

## Top structural issues (block a unified world-class suite)

- **Fragmentation of "Live Monitor"** into 4 overlapping screens: `LiveMonitor.vue` (dead stub), `CommandCenter.vue` (the only realtime-capable screen — **orphaned, not in `router.js`, card has no `route:`**), `AdminMonitor.vue` (the real sales/registers monitor — poll-only), `EmployeeLiveMonitor.vue` (associate self-view).
- **Sales performance computed 5+ different ways** (`revenue_dashboard.py`, `analytics_hub.py`, `reports.py` EOD/brief, `sales_history.py`) with subtly divergent SQL — numbers drift between surfaces. No shared sales-aggregation service.
- **Margin defined 7 ways** across the repo (`profit_intelligence.py` canonical 6-bucket vs `commission.py` 1-bucket `valuation_rate` vs `pricing_tools.simulate_price_change` 2-bucket vs `analytics_hub._margin_pct` vs `top_profitability_by_product.py` vs `repair_accounting.py` vs `gemstone_value_service.py`). `commission.py` pays real commissions on an **inflated margin**. The what-if simulator's projected margin won't match the posted margin → trust killer.
- **No charting library** — every dashboard hand-rolls CSS/SVG bars. Blocks trend lines, tooltips, drill-down.
- **`17` duplicated `fmt()` definitions**; triplicated role logic (`utils/permissions.js`, `router.js ROLE_TIERS`, `Dashboards.vue` inline); **`window.location.href` full-page reload** on every dashboard switch (`ReportsHub.vue:245`) tears down the SPA — fatal for a command-center UX.
- **REPORT_CATALOG advertises reports that don't exist** (`Store Scorecard`, `Sales by Metal` are catalog-only stubs); iframe-embedded Frappe reports have no cross-filter/drill-through.
- **`Cost Center Allocation` is a singleton** → cannot represent per-store overhead/payment rates → blocks multi-store profit intelligence.
- **COGS model gaps** (jewelry accuracy): no **making charge**, no **alloy/wastage**, gemstone at **cost-not-replacement**, labor is a **guessed constant** (`default_minutes_per_sale`), `labor_burden_percent` field exists but is **never applied**.
- **Two divergent workforce revenue paths**: `Performance Log` (manager engine) vs direct `Sales Commission Split` SQL (`employee_live_monitor.py`) — manager view and associate view will disagree.
- **6 of 12 Performance Log event types are never produced** (Clock In/Out, Overtime, Upsell Recorded, Layaway Completed, Sale Completed[unwired], Return Processed[unwired]); many scorecard fields hardcoded 0 (`high_ticket_sales`, `upsells`, `scheduled_hours`, `attendance_%`, CSAT=100, `layaway_default_rate`).

## The honest verdict

The backends are **far ahead of the frontends**, and the **integration layer is the dominant flaw** — well-designed islands (Sale Cost Breakdown, Performance Log, repair realtime) with **no bridges to the invoice lifecycle or to each other**. Three of the four flagship modules currently produce **partially-zero or stub data** in a live system. The work is: **wire the hooks, unify the KPI/calc layer, adopt a design system, and build the missing UIs** — *not* rebuild the backends. That framing drives the design and roadmap in `03_target_design/` and `04_roadmap/`.
