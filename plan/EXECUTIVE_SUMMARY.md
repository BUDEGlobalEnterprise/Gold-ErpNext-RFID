# Executive Summary — Zevar Monitor Suite

> Read this first. It is the whole plan in ~2 pages. Detail lives in the design and roadmap docs.

## The opportunity

The four flagship monitoring modules — **Live Monitor, Sales Monitor, Profit Intelligence, Workforce Intelligence** — have **rich backends but thin/fragmented frontends and, critically, a broken integration layer.** They do not yet form one coherent suite. This plan turns them into the refined superset of the best jewelry POS systems in the world: **deeper on jewelry economics than The Edge, more live than Lightspeed, more workforce-native than Shopify, and more profit-aware than any generic retail POS.**

### Combined vision
A single Frappe/ERPNext core where an owner opens **one live wall** and sees every store's sales, repairs, memos out on loan, gold-spot exposure, margin-at-risk, and associate scoreboard updating in real time; drills from any tile into a **margin waterfall** that decomposes every dollar of COGS into gold-at-sale, gemstone, labor, making charge, payment interchange, and overhead; **simulates** a gold-rate or discount change before applying it; and **pays associates** on gross-profit-margin-tiered commissions that flow straight into HRMS Salary Slips — all on one MariaDB data model with zero ETL, self-hosted or cloud.

### Why Zevar wins (three-layer moat)
1. **Jewelry economic depth** — gold-rate-at-sale locking, per-karat purity mapping, gemstone 4Cs, making/alloy/labor decomposition, payment-interchange-aware contribution margin, captured once per invoice and queried consistently everywhere.
2. **Native unification on the Frappe stack** — live wall (`publish_realtime`), BI (Frappe Insights, zero backend code), workforce (HRMS Appraisal/Goal/Salary Component), and the profit engine all read **one** MariaDB model. Competitors bolt these on as paid external layers.
3. **Real-time + relationship** — because Zevar owns the POS event stream, it pushes live scoreboards, in-the-moment coaching nudges, and gamification in real time; rivals relying on nightly CRM sync cannot.

---

## Where the four modules stand today (verified)

| Module | Backend | Frontend | vs best-in-class |
|---|---|---|---|
| **Profit Intelligence** | Strong *design* (~50%) | ~20% (only module with a Pinia store) | **~50%** |
| **Workforce Intelligence** | Richest (~1054 lines) but **data-starved** | **~0%** (two stubs) | ~40% backend / 0% UI |
| **Live Monitor** | Repair-only realtime | 4 fragmented screens | **~25%** |
| **Sales Monitor** | Shallow (today-only; 5 duplicate SQL) | Thin (no date picker) | **~15% — weakest** |

---

## 🔴 The critical P0 bugs (verified by direct code read of `hooks.py`)

These make current dashboards show **zero or wrong** data. They are the foundation of the entire plan.

1. **Profit — `calculate_sale_cost_breakdown` is NOT registered** in `Sales Invoice on_submit` → **Sale Cost Breakdown records are never created → every profit endpoint returns zero.** No `on_cancel` cleanup either. (`generate_pricing_recommendations` is also unscheduled; 4 UI↔API contracts are broken: `create_recommendation` 404, approve/reject casing, heatmap pivot shape, confidence string-vs-number.)
2. **Workforce — the ENTIRE Performance Log event stream is dead.** `_create_performance_log` is called only by the `log_*_event` functions, and **none of them are registered or called anywhere** → the **Performance Log table is empty in production** → every scoreboard, compensation calculation, and quarterly review runs on zero events. *(An earlier audit claimed layaway/repair/attendance hooks were wired — that was wrong; the active `hooks.py` `doc_events` covers only `Item` and `Sales Invoice`.)* `generate_quarterly_reviews` is also unscheduled.
3. **Live — `publish_anomaly_alert` is dead code** (zero callers) and anomaly detection has no scheduler; `publish_employee_event` is never invoked from the sale path; `AdminMonitor` polls 30s instead of subscribing to `pos_sale_event`; all realtime publishes omit `user=`/`room=` → **employee events broadcast to every socket** (privacy leak).
4. **Margin is defined 7 inconsistent ways** across the repo. `commission.py` pays real commissions on a 1-bucket `valuation_rate` margin → **associates are paid on an inflated margin.** The what-if simulator's projected margin won't match the posted margin.

---

## Recommended sequencing

**Shared Platform (Phase 0) → Profit (1) → Sales (2) → Workforce (3) → Live Monitor (4) → Polish & Scale (5).**

> *Why:* the platform kills all 7 P0 bugs and stands up the single margin definition + rollups + event bus. **Profit goes first** because every other module reads margin from Sale Cost Breakdown — landing it first means commission, sales, and workforce all build on one true number. **Workforce defers to Profit** because its commission engine pays on the wrong margin until `profit_math` exists. **Live Monitor is the capstone** — it consumes the event streams the other three produce, so it can't be credible until they exist.

> *Rejected:* Workforce-first ("just wire the rich backend") — would lock in *more* wrong commission payouts before the pay basis is fixed.

---

## The Quick-Win Sprint (S1 — days, not weeks)

Ship before any module "build" — pure wiring + contract fixes with outsized visible impact:

- **Q1** Wire `calculate_sale_cost_breakdown` (`on_submit`/`on_cancel`) → Profit stops returning empty
- **Q2** Wire `log_sale_event`/`log_sale_cancel_event` → Workforce revenue axis stops being 0
- **Q3** Schedule `generate_pricing_recommendations`
- **Q4** Backfill Sale Cost Breakdown + Performance Logs from history (idempotent; reconciles underpaid commissions)
- **Q5** Fix the 4 broken Profit UI↔API contracts
- **Q6** Resurrect dead realtime → `bus.publish` + anomaly/health schedulers; delete dead publishers
- **Q7** Add **live sales** to the command center (the #1 owner metric, absent today)
- **Q8** Compute zero-cost KPIs: **UPT, run-rate, projected-day-close** (data already exists)
- **Q9** Adopt **ECharts** + extract `utils/format.js` (kill 17 duplicate `fmt()`)
- **Q10** Collapse the 4 live screens → **one Command Center route**; kill the `window.location.href` full-page reloads

**Sprint exit (day ~5):** post a sale at the POS and see it on a non-empty Command Center wall within seconds; Profit shows a non-zero margin; a salesperson's scoreboard shows non-zero revenue.

---

## MVP per module (best-in-class minimum)

- **Profit:** wired SCB hook + `profit_math` (one margin everywhere) + Margin Waterfall + PVM bridge + What-If reconciled to posted SCB.
- **Sales:** `sales_monitor.*` spine (kills 5-way drift) + 8-KPI strip (incl. UPT/run-rate/projected-close) + multi-granularity trend + associate leaderboard + conversion funnel (manual traffic entry v1).
- **Workforce:** `log_sale_event` wired + backfill + populated scorecard fields + corrected commission + Team Console + associate self-view (unlocks the existing 13 endpoints).
- **Live Monitor:** one role-aware push-first wall with live sales + repairs + alerts + gold-at-risk + associates + health + ack/snooze/resolve.

---

## What proves we became the leader (portfolio success metrics)

- **One true margin** — `gross_margin_pct` identical on 5 surfaces (commission payout, top-profitability report, analytics hero, SCB, what-if simulator); 0 drift (integration-gated).
- **Sub-100ms** monitor queries at 5 stores × 3 years (via rollups).
- **Realtime freshness** — sale posts to wall < 3s p95 (vs 30s polling today).
- **Payroll-grade commissions** — any payout traces to invoice + line + rule + version, flows to HRMS Salary Slip.
- **Coaching KPI parity+** with The Edge (ARS, GP$/GP%, UPT, conversion, attach, discount ratio, capture rate, revenue-per-hour).
- **Privacy** — 0 globally-broadcast employee events; associates never see peer amounts.

---

## What to do Monday

1. Read [`04_roadmap/IMPLEMENTATION_ROADMAP.md`](./04_roadmap/IMPLEMENTATION_ROADMAP.md) §0 (grounding) and §4 (quick wins).
2. Open [`03_target_design/00_SHARED_PLATFORM.md`](./03_target_design/00_SHARED_PLATFORM.md) §0 (the 7 P0 bugs) and §2 (`profit_math`).
3. Start the **Quick-Win Sprint (Q1–Q10)**. ⚠️ **Non-negotiable rule: never run a compensation calculation against production payouts until the Phase 0 fixes (wired `log_sale_event` + unified `profit_math`) have shipped and backfill has reconciled history.**
