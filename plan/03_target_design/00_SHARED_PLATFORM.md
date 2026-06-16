# Zevar — Shared Cross-Cutting Platform Spec

> **Role:** Chief Platform Architect. This is the foundation all 4 monitoring modules (Live Monitor, Sales Monitor, Profit Intelligence, Workforce Intelligence) build on. Every file path, doctype name, column, and endpoint below is concrete and engineering-ready.
>
> **Grounding note (verified by direct code read, not the stale baseline):** Several prior planning artifacts (e.g. `plan/02_current_state_audit/module_audit_raw.json`) wrongly claim the `calculate_sale_cost_breakdown` hook is wired and that margin math is centralized. Both are **false**. `zevar_core/hooks.py` (read in full) confirms Sales Invoice `on_submit` registers only `commission.calculate_commissions`, `stock_reduction.detect_stock_reduction`, `reservation_manager.release_reservation_for_invoice` — NO profit hook, NO `log_sale_event`. `publish_anomaly_alert` and `publish_employee_event` have **zero callers** (grep-confirmed). This spec is written against the corrected baseline.

---

## 0. The 7 P0 bugs this platform must eliminate (evidence-backed)

| # | Bug | Evidence | Platform fix |
|---|-----|----------|--------------|
| B1 | `calculate_sale_cost_breakdown` hook unwired → no Sale Cost Breakdown rows ever created → all profit endpoints return empty | `hooks.py:65-69` (on_submit list has no profit hook) | §2 — wire via doc_events + on_cancel + backfill |
| B2 | `log_sale_event`/`log_sale_cancel_event` unwired → Workforce revenue axis always 0 (payroll-affecting) | `hooks.py:65-73` | §2 — wire to on_submit/on_cancel + backfill |
| B3 | Margin defined 7 different ways; `commission.py` pays out on a 1-bucket margin | `commission.py:109` (valuation_rate only); 6 other sites | §2 — single `compute_invoice_margin()` in `profit_math` |
| B4 | `publish_anomaly_alert` + `publish_employee_event` are dead code; docstrings lie about room scoping | `live_monitor.py:37-60`, `publish_repair_event` docstring says "broadcast to 'repair_monitor' room" but the call has no `room=` | §1 — event bus + room/user scoping + scheduler |
| B5 | `ReportsHub.vue:245` full-page reload on every dashboard switch | `ReportsHub.vue` (3 `window.location.href`) | §4 — SPA router-view shell |
| B6 | Role logic triplicated; `canAccessMonitor()` allows Sales Manager but `live_monitor.py:78` excludes them | `permissions.js`, `router.js:4-29 ROLE_TIERS`, `Dashboards.vue` inline `accessTier` | §5 — single permission helper |
| B7 | 17 duplicated `fmt()` definitions; 4 fragmented live screens; no chart library; no shared time context | `grep -c "function fmt("` = 17; `router.js` live routes | §3, §4, §7 |

---

## 1. REALTIME / EVENT-BUS ENGINE

### 1.1 Goals
Push-first (socket.io via `frappe.realtime`), polling as exponential-backoff fallback only. Role/room/user scoping on **every** event — never broadcast employee-attributed events globally. A 24h rolling backfill log so a freshly-opened wall hydrates instantly. One versioned event schema, generated Python→TS to kill field drift (e.g. `new_status` vs `status`).

### 1.2 Channel taxonomy (the only allowed event names)

| Channel (event name) | Scope rule | Producers | Consumers |
|---|---|---|---|
| `command_center` | `room="admin_wall"` (owner + managers only) | every business event fan-out | Command Center owner wall |
| `store_ops` | `room="store_<warehouse>"` | repair, session, stock, override | store manager widgets |
| `associate_personal` | `user=<employee_user_id>` (NEVER global) | sale/repair/attendance attributed to an employee | EmployeeLiveMonitor, associate detail |
| `repair_live` | `room="admin_wall"` + `room="store_<wh>"` (publish twice, scoped) | `repair_order.py` status hooks | repair feed tile |
| `sales_tick` | `room="admin_wall"` + `room="store_<wh>"` | invoice on_submit/on_cancel, gold_purchase submit | live sales tiles, scoreboard |
| `anomaly_alert` | `room="admin_wall"` | anomaly scheduler + rule hooks | alert ticker, Operations Alert |
| `price_shock` | `room="admin_wall"` | metal_rate fetch when Δ > threshold | margin-at-risk widget |
| `system_health` | `room="admin_wall"` | health heartbeat scheduler + hardware_bridge | device/system-health wall |

> **Iron rule:** any event whose payload references a named employee, customer, or commission amount MUST be published with `user=` (personal) or to a manager-only `room=`. The current `publish_employee_event` broadcast violates this and is fixed below.

### 1.3 Versioned event schema (single source of truth → TS generated)

**File:** `zevar_core/api/realtime/events_schema.py` — Python `TypedDict` definitions, the canonical contract.

```python
# zevar_core/api/realtime/events_schema.py
from typing import TypedDict, Literal, Optional
import time

SCHEMA_VERSION = "1.0.0"

# ---- Common envelope (every event is wrapped in this) ----
class EventEnvelope(TypedDict):
    v: str                 # SCHEMA_VERSION
    id: str                # uuid4 — dedupe key for backfill merge
    channel: str           # one of the channel names above
    event_type: str        # sale.completed, refund.processed, repair.status_changed, ...
    ts: str                # ISO-8601 UTC
    store: Optional[str]   # warehouse id, "" if system-wide
    actor_user: str        # frappe.session.user of the producer
    actor_name: str
    data: dict             # event-type-specific payload (typed below)

# ---- Typed payloads (examples; full set in the file) ----
class SaleCompletedData(TypedDict):
    invoice: str
    customer: str
    net_total: float
    grand_total: float
    qty: int
    employees: list[str]            # salesperson employee ids (for personal fan-out)
    channel: str                    # in_store | online | phone | b2b | memo  (see §8)
    gross_margin_pct: Optional[float]   # from SCB if available, else null

class RepairStatusData(TypedDict):
    repair: str
    name: str
    customer: str
    status: str                     # canonical status string
    promised_date: Optional[str]
    assigned_to: Optional[str]

class AnomalyData(TypedDict):
    alert_id: str                   # Operations Alert name
    severity: Literal["critical","warning","info"]
    type: str
    title: str
    store: Optional[str]
```

**TS mirror (generated, never hand-edited):** `frontend/zevar_ui/src/types/realtime-events.ts` — generated by `scripts/gen_realtime_types.py` (a `mypy`/stub-style extractor reading the TypedDicts, or a single `EVENT_TYPES` registry dataclass that is the single source both Python and TS read). Run in CI; PR fails if `realtime-events.ts` differs from generated output. This eliminates the `new_status` vs `status` drift that today breaks `CommandCenter.vue:327`.

### 1.4 Backend publisher (replaces the 3 broken publishers)

**File:** `zevar_core/api/realtime/bus.py`

```python
# zevar_core/api/realtime/bus.py
import frappe, uuid, json
from datetime import timedelta
from zevar_core.api.realtime.events_schema import SCHEMA_VERSION, EventEnvelope

# 24h rolling backfill log (MariaDB table; Redis optional accelerator)
BACKFILL_TTL_HOURS = 24

def publish(channel: str, event_type: str, data: dict, *,
            store: str | None = None, employees: list[str] | None = None,
            broadcast_admin: bool = True, broadcast_store: bool = True):
    """Single entry point. Computes scope, persists to live_event_log, fan-outs."""
    env: EventEnvelope = {
        "v": SCHEMA_VERSION,
        "id": str(uuid.uuid4()),
        "channel": channel,
        "event_type": event_type,
        "ts": frappe.utils.now_datetime().isoformat(),
        "store": store or "",
        "actor_user": frappe.session.user,
        "actor_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
        "data": data,
    }
    _persist_backfill(env)                      # 24h rolling log (see §1.5)
    _fan_out(env, employees, broadcast_admin, broadcast_store)

def _fan_out(env, employees, broadcast_admin, broadcast_store):
    msg = frappe.as_json(env)
    if broadcast_admin:
        frappe.publish_realtime(env["channel"], msg, room="admin_wall", after_commit=True)
    if broadcast_store and env["store"]:
        frappe.publish_realtime(env["channel"], msg, room=f"store_{env['store']}", after_commit=True)
    if employees:                               # personal channel — NEVER global
        for emp in employees:
            user = frappe.db.get_value("Employee", emp, "user_id")
            if user:
                frappe.publish_realtime("associate_personal", msg, user=user, after_commit=True)
```

**Wiring (hooks.py deltas):**

```python
doc_events["Sales Invoice"]["on_submit"].append("zevar_core.api.realtime.hooks.on_invoice_submit")
doc_events["Sales Invoice"]["on_cancel"].append("zevar_core.api.realtime.hooks.on_invoice_cancel")
doc_events["Repair Order"]["on_update"].append("zevar_core.api.realtime.hooks.on_repair_update")
doc_events["Gold Purchase"]["on_submit"].append("zevar_core.api.realtime.hooks.on_gold_purchase_submit")

scheduler_events["cron"]["*/2 * * * *"] = ["zevar_core.api.realtime.hooks.run_anomaly_push"]      # push anomalies on a cadence, no screen open
scheduler_events["cron"]["*/5 * * * *"] = ["zevar_core.api.realtime.hooks.run_health_heartbeat"]  # system_health
```

The dead `publish_anomaly_alert`/`publish_employee_event` are deleted; `publish_repair_event` is migrated to `bus.publish("repair_live", "repair.status_changed", RepairStatusData(...))`. This fixes B4.

### 1.5 24h rolling backfill log (table `live_event_log`)

See full schema in **§2.6** (it is also the audit/event-stream fact table). On wall open, the client calls `zevar_core.api.realtime.get_backfill?hours=24&channels=...` which streams the tail; `useRealtime` merges deduping on `envelope.id`. Retention enforced nightly by `zevar_core.tasks.purge_live_event_log` (cron `0 3 * * *`, delete `ts < NOW() - INTERVAL 24 HOUR`).

### 1.6 Vue composables (exact responsibilities)

All in `frontend/zevar_ui/src/composables/`.

**`useRealtime.js`** — the single realtime abstraction. Wraps `frappe.realtime.on/off`.
- Responsibilities: subscribe to one or more channels with a typed handler; auto-reconnect awareness (re-subscribe on `socket.io` reconnect event); **pause when `document.hidden`** (resumes on visibilitychange, triggers a backfill fetch on resume); single-subscription-per-channel **dedupe** (multiple components sharing a channel share one socket subscription via a module-level registry); exponential-backoff poll fallback wired through `usePolling`.
- API: `const { lastError, isLive } = useRealtime({ 'sales_tick': handler, 'anomaly_alert': handler2 })`.
- Migrates `CommandCenter.vue:366`, `EmployeeLiveMonitor.vue:352`, `session.js:66`, `AdminMonitor.vue` (currently subscribes to nothing), `NotificationCenter`.

**`useDashboardData.js`** — wraps `frappe-ui` `createResource` with shared `loading`/`error`/`refresh`, **auto-respects the global time store** (re-fetches when `timeStore.range` changes), and supports `poll: true` to attach a `usePolling` fallback. Standardizes the 3 inconsistent HTTP clients (B7): deletes raw `fetch()`+CSRF from `Revenue.vue`/`Customer.vue`/`Inventory.vue`/`EmployeeLiveMonitor.vue`.
- API: `const { data, loading, error, refresh } = useDashboardData('zevar_core.api.sales_monitor.get_summary', { auto: true, poll: 30000 })`.

**`usePolling.js`** — exponential-backoff interval (e.g. base 10s, capped 60s, reset to base on success), paused-when-hidden, `onInvisiblePause`/`onVisibleResume` hooks, returns `{ pause, resume, currentDelay }`. Imported by `useDashboardData` and `useRealtime` as the fallback path.

**`useBackfill.js`** — on mount and on tab-visible, calls `realtime.get_backfill` and merges events into the local store, deduping on `envelope.id`, applying them in `ts` order.

---

## 2. UNIFIED KPI & CALCULATION LAYER

This is the spine. It kills the 7-way margin bug (B3), the 5 duplicate today's-sales queries, and the two divergent workforce revenue paths.

### 2.1 `sales_monitor.py` — the sole sales-KPI aggregation service

**File:** `zevar_core/api/sales_monitor.py` (new). Owns **all** sales KPIs. `revenue_dashboard.py`, the EOD revenue section (`reports.py:_eod_revenue`), `analytics_hub.py` sales hero, and `sales_history.py:get_sales_summary` are refactored to delegate here (the 5 duplicate today's-sales SQL implementations collapse to one).

Public whitelisted endpoints (all role-gated, all read the **rollup table** first):

| Endpoint | Returns |
|---|---|
| `sales_monitor.get_summary(from, to, store, granularity)` | revenue, txn_count, AOV, UPT, units, refund_count, refund_value, run_rate, projected_day_close, vs_prior_period, vs_yoy |
| `sales_monitor.get_hourly(from, to, store, bucket)` | hour-of-day (full 24h, zero-bucketed) |
| `sales_monitor.get_trend(metric, from, to, granularity, compare)` | multi-series with prior-period + YoY/WoW overlay |
| `sales_monitor.get_breakdown(dimension, from, to, store)` | by category/metal/purity/salesperson/channel/SKU/customer |
| `sales_monitor.get_leaderboard(from, to, store)` | per-associate revenue, UPT, conversion, attach, margin, customer-capture |
| `sales_monitor.get_pace(from, to, store)` | vs `Sales Target` (§8), projected-close, attainment % |
| `sales_monitor.run_query(report_spec)` | generic engine for the report-builder grammar (§6) |

**Zero-cost KPIs finally computed** (data already exists): UPT = `SUM(Sales Invoice Item.qty)/COUNT(invoices)`; attach rate; refund/void rate; run-rate; projected-day-close.

### 2.2 `profit_math` — the single shared margin module (fixes B3)

**File:** `zevar_core/services/profit_math.py` (new — `services/` already exists, confirmed). Exposes exactly **two** entry points the entire system must use:

```python
# zevar_core/services/profit_math.py
def get_item_cogs(item) -> dict:
    """Metal (net_weight x gold_rate_at_sale) + gemstone + making + alloy + commission-attrib
       + payment-attrib + overhead-attrib. One definition. Returns dict of components."""

def compute_invoice_margin(invoice_name: str, *, include_overhead=True, include_payment=True) -> dict:
    """Returns: {revenue, metal_cogs, gemstone_cogs, making_charge, alloy_adjustment,
                 labor, commission, payment_cost, overhead, total_cost,
                 gross_profit, gross_margin_pct, net_contribution_margin_pct,
                 gold_rate_at_sale, gold_rate_source, gold_rate_timestamp,
                 calc_log: [...]}"""
```

**Refactor targets** (each currently has its own divergent margin — all repointed to `profit_math`):

| Site (current, broken) | Current math | Action |
|---|---|---|
| `commission.py:104-109` | `valuation_rate * qty` only → **pays commission on inflated margin** | call `compute_invoice_margin(...)`; commission on true margin (highest $-impact fix) |
| `top_profitability_by_product.py:70-71` | recomputes from `valuation_rate` despite joining SCB | read `scb.gross_profit` directly |
| `analytics_hub.py:1012 _margin_pct` | `custom_cost_price` basis | call `profit_math` |
| `rag/tools/pricing_tools.simulate_price_change:210` | gold+gem only | call `compute_invoice_margin` so simulator matches posted SCB (trust fix) |
| `repair_accounting.py:704` | material-only (labor excluded) | call `profit_math` with `include_labor=False` documented |
| `gemstone_value_service.py:125` | markup-on-cost (inverted denominator) | rename to `markup_on_cost_pct`; do not reuse `margin_pct` key |
| `finance.py:351` | GL-based net profit | keep, but label `accounting_net_profit`, never `gross_profit` |

After this, the word `gross_margin_pct` means exactly one thing everywhere. The what-if simulator, commission payouts, reports, and analytics all reconcile.

### 2.3 Sale Cost Breakdown = the sole COGS/margin spine

Keep the existing doctype (`sale_cost_breakdown`, schema read and confirmed: 6-bucket COGS, `gold_rate_at_sale`/`source`/`timestamp`, `gross_profit`, `gross_margin_pct`, `calculation_log`). The `calculate_sale_cost_breakdown` function is refactored to call `profit_math.compute_invoice_margin` and persist the result.

**Schema additions** (new fields on SCB):
- `making_charge` (Currency) — per §Profit gap, currently missing
- `alloy_wastage_amount` (Currency)
- `store` (Link → Warehouse) — enables multi-store profit (Cost Center Allocation is a singleton today, blocking this)
- `item_group` (Link → Item Group) — category dimension beyond `jewelry_type`
- `net_contribution_margin_pct` (Percent) — revenue − all 6 buckets − payment − overhead

### 2.4 Performance Log = canonical workforce revenue source

The two divergent revenue paths are reconciled: **Performance Log** is canonical; `employee_live_monitor.py` is refactored to read from it (today it reads `Sales Commission Split` directly → diverges). `log_sale_event` is wired to Sales Invoice `on_submit` (B2) and `log_sale_cancel_event` to `on_cancel`, plus a one-time `backfill_performance_logs_from_history` bench command.

### 2.5 Materialized rollup tables — exact schemas

All four are new MariaDB tables (custom doctypes or bare `tab*` tables managed via Frappe migrations). Refreshed by **triggers on invoice submit/cancel** (`zevar_core.api.realtime.hooks` calls `sales_monitor.rebuild_rollup(invoice)`), plus a nightly `*/30 0 * * *` safety full-rebuild.

#### `daily_store_sales_rollup` (collapse the EOD's 15+ queries to sub-100ms)

| Column | Type | Notes |
|---|---|---|
| `date` | Date | PK part |
| `store` | varchar(20) | PK part (warehouse code) |
| `salesperson` | varchar(140) | PK part (employee id; `__none__` if unattributed) |
| `channel` | varchar(20) | PK part — `in_store/online/phone/b2b/memo` (§8) |
| `category` | varchar(140) | PK part — `custom_jewelry_type` |
| `metal` | varchar(20) | PK part |
| `invoice_count` | int | |
| `unit_count` | int | `SUM(qty)` |
| `gross_revenue` | decimal(18,4) | `SUM(grand_total)` |
| `net_revenue` | decimal(18,4) | `SUM(net_total)` |
| `refund_count` | int | |
| `refund_value` | decimal(18,4) | |
| `discount_value` | decimal(18,4) | |
| `cogs_total` | decimal(18,4) | from SCB |
| `gross_profit` | decimal(18,4) | from SCB |
| `gold_rate_avg` | decimal(12,2) | avg of SCB.gold_rate_at_sale |
| `updated_at` | datetime | |

PK: `(date, store, salesperson, channel, category, metal)`. Indexes: `(store,date)`, `(date)`, `(salesperson,date)`.

#### `employee_period_rollup` (workforce; replaces `get_team_performance` N+1)

| Column | Type | Notes |
|---|---|---|
| `employee` | varchar(140) | PK part |
| `period_type` | varchar(20) | PK — `daily/weekly/monthly/quarterly` |
| `period_start` | date | PK part |
| `period_end` | date | |
| `store` | varchar(20) | |
| `revenue_amount` | decimal(18,4) | from Performance Log |
| `item_count` | int | |
| `customer_count` | int | |
| `txn_count` | int | |
| `upt` | decimal(8,3) | units/txn |
| `high_ticket_count` | int | |
| `upsell_count` | int | |
| `return_count` / `return_value` | int / decimal | |
| `commission_earned` | decimal(18,4) | |
| `hours_worked` | decimal(8,2) | from clock-in logs (§Workforce) |
| `attendance_pct` | decimal(5,2) | |
| `points_earned` | int | gamification ledger |
| `updated_at` | datetime | |

PK: `(employee, period_type, period_start)`. Fixes the `get_team_performance` O(employees×logs) Python loop.

#### `metal_rate_history` (gold pass-through analytics + what-if backtesting)

| Column | Type |
|---|---|
| `timestamp` | datetime (PK) |
| `metal` | varchar(10) (PK) |
| `purity` | varchar(10) (PK) |
| `rate_per_gram` | decimal(12,2) |
| `source` | varchar(40) |
| `delta_pct_1h` | decimal(6,2) |
| `delta_pct_24h` | decimal(6,2) |

Fed by `fetch_live_metal_rates` (already scheduled `*/60`). Enables gold pass-through %, unrealized gain/loss, price-shock alerts, and what-if backtesting.

#### `live_event_log` (24h rolling backfill — see §1.5)

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(36) (PK) | envelope.id (uuid) |
| `ts` | datetime | indexed; partition/daily prune |
| `channel` | varchar(40) | |
| `event_type` | varchar(60) | |
| `store` | varchar(20) | |
| `actor_user` | varchar(140) | |
| `payload` | JSON / LongText | full envelope JSON |
| `schema_version` | varchar(10) | |

### 2.6 Refresh triggers

- **Invoice submit/cancel** → `sales_monitor.rebuild_rollup(invoice)` (upsert affected `(date,store,...)` rows) → publish `sales_tick` via `bus.publish`. Deletes/voids the SCB row on cancel (B1 on_cancel).
- **Performance Log insert** → `rebuild_employee_rollup(employee, period)` upsert.
- **Metal rate fetch** → append `metal_rate_history`; if `|delta_pct_1h| > threshold`, `bus.publish("price_shock", ...)`.
- Nightly safety: `*/30 0 * * *` full rebuild of all rollups (idempotent).

---

## 3. DESIGN SYSTEM & CHART PRIMITIVES

### 3.1 Charting library: **ECharts**

Rationale (vs ApexCharts): (1) **Heatmap + funnel** are first-class in ECharts (both required by the suite: margin heatmap, conversion funnel) — ApexCharts heatmap is weaker; (2) better perf for the live multi-store wall (canvas renderer, large dataset mode); (3) tree-shakeable; (4) richer waterfall/bridge support needed for the Margin Waterfall and PVM bridge (Profit module). ApexCharts wins on aesthetics but loses on heatmap/funnel/waterfall, which are load-bearing here. Install `echarts` + `vue-echarts` in `frontend/zevar_ui`.

### 3.2 Six reusable chart components

All in `frontend/zevar_ui/src/components/charts/`, all consume `timeStore` and `utils/format.js`:

| Component | Props | Used by |
|---|---|---|
| `KpiSparkline.vue` | `series, comparisonSeries?` | KPI cards, Command Center tiles |
| `HourlyBarChart.vue` | `data (full 24h, zero-bucketed), compare?` | Sales hourly, traffic overlay |
| `CategoryDonut.vue` | `slices, metric` | category/metal/channel/tender breakdown |
| `TrendLineChart.vue` | `metric, granularity, current, prior, yoy` | the multi-series trend with comparison overlay |
| `MarginHeatmap.vue` | `rows, cols, cellValue, metric` | margin heatmap (replaces broken pivot-mismatch version) |
| `ConversionFunnel.vue` | `stages[]` | footfall → greeted → try-on → purchase |

Also a `WaterfallChart.vue` (built on ECharts waterfall) for the Profit Margin Waterfall (counts as a 7th specialized component but the 6 above are the shared primitives).

### 3.3 Shared formatters — `utils/format.js`

**File:** `frontend/zevar_ui/src/utils/format.js` (new). Exports `fmtCurrency`, `fmtPercent`, `fmtCompact`, `fmtRelativeTime`, `fmtNumber`, `fmtDate`. Replaces the **17 duplicated `fmt()` copies** (grep-confirmed). Each dashboard's local `fmt` is deleted and imports `utils/format.js`.

### 3.4 Shared status-color constants

**File:** `frontend/zevar_ui/src/utils/status-colors.js` (new). Exports `STATUS_COLORS`, `SEVERITY_COLORS`, `HEALTH_COLORS`. Replaces the per-dashboard `statusBarColor`/`healthDot`/`alert` maps duplicated in `CommandCenter.vue:423-448`, `AdminMonitor.vue`, `EmployeeLiveMonitor.vue`.

### 3.5 Design tokens (reuse, don't rewrite)

Reuse existing `frontend/zevar_ui/src/styles/tokens.css`, `.premium-card`, `.premium-title` (defined in `index.css`, used in 5+ files). `KPICard.vue` (already reused in 9 files) becomes the mandatory KPI tile primitive. No new token system.

---

## 4. UNIFIED DASHBOARD SHELL + GLOBAL TIME CONTEXT

### 4.1 One hub: expand `ReportsHub`

`ReportsHub.vue` becomes the suite shell. The catastrophic full-page reload at `ReportsHub.vue:245` (and the other 2 `window.location.href`) is **deleted** (B5) and replaced with `router.push()`:

```js
// BEFORE (ReportsHub.vue:244-246) — tears down the entire SPA
function openDashboard(name) { window.location.href = `/pos/reports/dashboards/${name}` }

// AFTER
function openDashboard(name) { router.push({ name: `dashboard-${name}` }) }
```

The dashboards tab mounts a `<router-view>` so switching dashboards preserves Pinia state, the global time store, live subscriptions, and the SPA boot.

### 4.2 Collapse the 4 live screens into one role-aware Command Center

| Old screen (delete/merge) | Status | Destination |
|---|---|---|
| `LiveMonitor.vue` (stub) | **delete** | redirect `/live-monitor` → Command Center |
| `CommandCenter.vue` (orphan, repair-only) | **merge** | becomes the repair/ops widgets inside Command Center; route registered in `router.js` |
| `AdminMonitor.vue` (sales, polls 30s, no realtime) | **merge** | becomes the sales/registers/audit widgets inside Command Center |
| `EmployeeLiveMonitor.vue` (associate self) | **keep** as the associate role view of the same route |

**New route:** `/reports/dashboards/command-center` → `CommandCenter.vue` (rebuilt). Role-aware rendering: owner = full multi-store wall; manager = their stores; associate = personal live view (renders `EmployeeLiveMonitor` content). One route, one `<router-view>`, one realtime subscription set.

### 4.3 Global time-range Pinia store

**File:** `frontend/zevar_ui/src/stores/time.js` (new). State: `{ from, to, granularity, compareMode }`. Actions: `setRange`, `setGranularity`, `setCompare`, `quickPreset('today'|'7d'|'30d'|'90d'|'ytd'|'qtd')`. Every widget (`useDashboardData`) watches `timeStore.$state` and re-fetches. Fixes the current chaos: Profit has from/to, RepairAnalytics has 7/30/90, Revenue/Customer/Inventory hardcoded 'today', AdminMonitor uses 4/8/24/72h windows. One source of truth.

---

## 5. SINGLE ROLE / PERMISSION MODEL

### 5.1 `utils/permissions.js` is the **sole** helper

Keep `utils/permissions.js` (already 7.6KB, ~15 helpers). **Delete** the two competing copies (B6):
- `router.js:4-29` — `ROLE_TIERS`, `getAccessTier`, `TIER_LEVELS`, `canAccess` → removed
- `components/reports/Dashboards.vue:111-119` — inline `accessTier`/`minTier` → removed

### 5.2 Router meta references **permission keys**, not role lists

```js
// router.js — meta uses permission keys (single source: permissions.js)
{ path: '/reports/dashboards/command-center',
  meta: { requiresAuth: true, permission: 'monitor.view' } }
{ path: '/reports/dashboards/profit',
  meta: { requiresAuth: true, permission: 'profit.view' } }
```

### 5.3 Client-side route guards with graceful no-access states

A global `beforeEach` guard calls the `permissions.js` helper for `meta.permission`; on denial it renders a `<NoAccess />` state instead of flashing full UI then 403-ing (today every dashboard flashes its chrome before the API throws — confirmed: grep finds zero `canAccess` checks inside `pages/dashboards/*`).

### 5.4 Reconcile frontend ↔ backend `only_for()` lists

| Surface | Frontend helper | Backend `only_for` (reconciled) |
|---|---|---|
| Command Center (owner wall) | `canAccessMonitor()` | System Manager, Administrator, Store Manager, **Accounts Manager**, **Sales Manager** (add Sales Manager — today `live_monitor.py:78` omits it while `canAccessMonitor` allows it) |
| Sales monitor | `canAccessSalesPerformance()` | System Manager, Store Manager, Sales Manager, Sales User (own-store), Accounts Manager |
| Profit Intelligence | `canAccessProfit()` (new) | System Manager, Administrator, Accounts Manager, Store Manager (read) |
| Workforce (manager) | `canAccessWorkforce()` (new) | System Manager, HR Manager, Store Manager |
| Associate self | `isOwnSalesOnly()` | Employee, Employee Self Service, Sales User |

The `admin_monitor.json` desk-page role gate is aligned to the same list (fixes the desk/SPA role mismatch where `Sales Manager` loads the iframe then gets redirected).

---

## 6. COMPOSABLE REPORT-BUILDER GRAMMAR

### 6.1 Metrics × Dimensions × Filters

**File:** `frontend/zevar_ui/src/components/reports/ReportBuilder.vue` (new) + backend engine `sales_monitor.run_query(report_spec)`.

```ts
interface ReportSpec {
  metrics:   Metric[];      // revenue, txn_count, aov, upt, units, gross_profit, margin_pct, conversion, sell_thru, roi, turns
  dimensions: Dimension[];  // store, salesperson, category, metal, purity, gem, channel, sku, customer, hour, dow, day, week, month
  filters:   FilterGroup;   // shared grammar below
  period:    PeriodSpec;    // from timeStore
  order_by:  { metric, dir };
  compare:   'none' | 'prior_period' | 'yoy' | 'wow';
}
```

### 6.2 Shared filter grammar (one `criteria` object across all 4 modules)

```
By: Store | Salesperson | Category | Metal | Gem | Channel | SKU | Customer | Period
```

- Each field has an **Exclude** toggle.
- Multi-select within a field = comma list.
- **same-type = OR, different-type = AND** rule (e.g. Metal IN (Gold, Silver) AND Category = Ring AND Channel = in_store).
- Surfaced in the UI as a single composable filter bar reused by Sales Monitor, Profit, Workforce, and Live (RICS + Shopify synthesis).

This single object is the cross-module filter contract — what a user filters in Sales Monitor carries into the Profit drill-down.

---

## 7. FOOTFALL / CONVERSION DATA LAYER

### 7.1 `Store Traffic Log` doctype (new)

| Field | Type | Notes |
|---|---|---|
| `date` | Date | PK part |
| `store` | Link→Warehouse | PK part |
| `hour` | Int (0-23) | PK part |
| `visitors_in` | Int | people-counter or manual |
| `visitors_out` | Int | optional |
| `source` | Select (`people_counter`, `manual_pos`, `door_sensor`) | |
| `device_id` | Data | hardware_bridge device ref |
| `entered_by` | Link→User | manual entry attribution |
| `notes` | Small Text | |

### 7.2 People-counter adapter

**File:** `zevar_core/integrations/hardware/people_counter.py` (new), invoked via the existing `scripts/hardware_bridge.py`. Adapter interface: `fetch_traffic(device_id, since) -> list[{ts, in, out}]`. v1 supports (a) a supported counter device and (b) **manual POS staff entry** on session open/close as the pragmatic fallback (the audit notes "no traffic data anywhere" — this is the #1 sales-monitor KPI blocker).

With traffic captured, conversion = `txn_count / visitors_in`, attach rate, traffic-vs-sales correlation, and demand-based scheduling all become possible. Surfaced as the `ConversionFunnel` chart and the salesperson leaderboard's conversion column.

---

## 8. CHANNEL + STORE-TARGET DIMENSIONS

### 8.1 Sales Channel on Sales Invoice (new custom field)

`Sales Invoice.custom_sales_channel` — Select: `In-Store POS`, `Online`, `Phone`, `B2B`, `Memo/Consignment`. Set on the POS path (`pos.py`) and exposed as a first-class report dimension (currently unmodeled — confirmed). Flows into `daily_store_sales_rollup.channel`.

### 8.2 `Sales Target` doctype (store-level, distinct from employee Performance Target)

| Field | Type | Notes |
|---|---|---|
| `store` | Link→Warehouse | PK part |
| `period_type` | Select (`Daily/Weekly/Monthly`) | PK part |
| `period_start` | Date | PK part |
| `period_end` | Date | |
| `target_revenue` | Currency | |
| `target_units` | Int | |
| `target_upt` | Decimal | |
| `target_conversion` | Decimal | |
| `channel_targets` | Table (child) | per-channel revenue target |

Drives the live pacing-to-target gauge and projected-day-close run-rate in `sales_monitor.get_pace`. Distinct from the existing `performance_target` (which is employee × compensation).

---

## 9. FRAPPE-STACK LEVERAGE MAP (use, don't rewrite)

### 9.1 Frappe core

| Native doctype | Use for | Not for |
|---|---|---|
| **Number Card** | glance KPI tiles on Workspaces | — |
| **Dashboard Chart** | embedded mini-charts on Workspaces | the SPA suite (use ECharts) |
| **Workspace** | owner landing/quick-glance tiles | deep analytics (use SPA) |
| **Frappe Insights Query v3 / Dashboard v3 / Alert** | zero-code owner BI, deep ad-hoc analysis, scheduled email/Telegram alerts | realtime (use custom event bus) |

> **Rule:** Insights Workbooks own deep no-code owner BI; the custom SPA owns realtime + the role-aware Command Center. No duplication.

### 9.2 HRMS (payroll-grade workforce — the native commission-to-salary moat)

| HRMS doctype | Use for | Zevar mapping |
|---|---|---|
| **Appraisal Cycle / Appraisal Template** | quarterly review cadence | `Quarterly Performance Review` ↔ Appraisal |
| **Goal** (goal tree) | target cascade store→team→associate | `Performance Target` ↔ Goal |
| **Employee Performance Feedback** | 1:1/coaching feedback records | Coaching Session (new) feeds this |
| **Employee Checkin / Shift** | clock-in (geo-fenced/kiosk) | produces `Clock In/Out` Performance Logs + worked hours (fixes hardcoded `scheduled_hours=0`) |
| **Salary Structure / Salary Slip** | payroll disbursement | `Commission Rule` + `Sales Commission Split` → **Salary Component** → Salary Slip (native, audit-grade) |
| **Employee Incentive / Additional Salary** | one-off SPIFF/bonus payout | gamification SPIFFs → Additional Salary |
| **Attendance** | attendance %, punctuality | populates `attendance_pct` (today hardcoded 0) |

### 9.3 ERPNext reports (reuse, don't rebuild)

- `sales_analytics`, `sales_invoice_trends`, `gross_profit` — reference/aggregation
- **`sales_person_target_variance_based_on_item_group`** — variance engine; mirror its logic in `sales_monitor.get_pace` for store-level
- `customer_acquisition_and_loyalty` — customer-capture-rate KPI (Lightspeed's jewelry-critical CRM KPI)

### 9.4 Other native (confirmed installed in this bench)

- `insights` (Frappe Insights app) — for owner BI Workbooks
- `crm`, `helpdesk`, `gameplan` — clienteling/follow-ups available without integration

---

## 10. How each module plugs in (the unblock map)

| Module | Consumes from this platform |
|---|---|
| **Live Monitor** (Command Center) | `bus.publish` channels + `live_event_log` backfill + `useRealtime` + `useDashboardData` + `CommandCenter.vue` shell + role-aware route + `sales_monitor.get_summary` for live sales (today absent) + `Operations Alert` doctype (severity/type/status ack-snooze-resolve/assigned/routing via NotificationCenter) |
| **Sales Monitor** | `sales_monitor.*` endpoints + `daily_store_sales_rollup` + `Sales Target` + `Store Traffic Log` + `custom_sales_channel` + report-builder grammar + `timeStore` + ECharts primitives |
| **Profit Intelligence** | `profit_math.compute_invoice_margin` (sole margin def) + SCB wired via `on_submit`/`on_cancel` + `metal_rate_history` + scheduled `generate_pricing_recommendations` + Margin Waterfall/PVM/what-if on `compute_invoice_margin` |
| **Workforce Intelligence** | Performance Log wired (`log_sale_event`) + `employee_period_rollup` + HRMS Appraisal/Goal/Checkin/Shift/Salary-Component + real scoreboard via `associate_personal` channel + UI against the 13 existing endpoints |

---

## 11. Sequencing (critical path; every module unblocked in order)

1. **Platform core (unblocks all):** profit_math + wire SCB hook + wire `log_sale_event` + backfill + rollup tables + `bus.py` + event schema + delete dead publishers + `useRealtime`/`useDashboardData`/`usePolling` + `utils/format.js` + `timeStore` + SPA router-view fix + single permission model.
2. **Then parallel:** Sales Monitor (on `sales_monitor`), Workforce UI (on existing endpoints), Profit exec views (on `profit_math`), Command Center (on `bus`).

The platform is intentionally sequenced first because the 7 P0 bugs (B1–B7) live *in* the shared layer, not in any single module.

---

### Key file-path index (all absolute)

- Backend realtime: `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/realtime/{bus.py,events_schema.py,hooks.py}` (new)
- Sales/KPI service: `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/sales_monitor.py` (new)
- Profit math: `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/services/profit_math.py` (new; `services/` confirmed exists)
- Hooks (must edit): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/hooks.py` (add SCB + log_sale_event + anomaly/health schedulers)
- Dead-code publishers (must delete): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/live_monitor.py:37-60`
- 7-way margin sites (must refactor): `commission.py:109`, `analytics_hub.py:1012`, `rag/tools/pricing_tools.py:210`, `repair_accounting.py:704`, `gemstone_value_service.py:125`, `finance.py:351`
- Frontend composables: `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/composables/{useRealtime.js,useDashboardData.js,usePolling.js,useBackfill.js}` (new)
- Frontend shared: `…/src/utils/format.js`, `…/src/utils/status-colors.js`, `…/src/stores/time.js`, `…/src/types/realtime-events.ts` (new)
- Shell fix: `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/pages/ReportsHub.vue:245` (delete `window.location.href`)
- Permission de-dup: `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/router.js:4-29`, `…/src/components/reports/Dashboards.vue:111-119`
- New doctypes: `operations_alert`, `store_traffic_log`, `sales_target`, `daily_store_sales_rollup`, `employee_period_rollup`, `metal_rate_history`, `live_event_log` under `…/zevar_core/unified_retail_management_system/doctype/`
