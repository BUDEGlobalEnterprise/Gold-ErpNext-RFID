> **Module:** Live Monitor (the "Command Center")
> **Role in the suite:** The realtime nervous system of Zevar — the single role-aware wall an owner, manager, or associate opens first. It is the *only* module that is **push-first and screen-shared** (TV/kiosk). The other three modules (Sales Monitor, Profit Intelligence, Workforce Intelligence) are its drill-down depth. Live Monitor owns the *pulse*; they own the *post-mortem*.
> **Builds on:** the Shared Platform (`bus.py`, `events_schema.py`, `live_event_log` backfill, `sales_monitor.*`, `profit_math`, `useRealtime`/`useDashboardData`/`useBackfill`, `timeStore`, ECharts primitives, single permission model). This design does **not** re-spec the platform; it consumes it.
> **Baseline reality (verified):** `publish_anomaly_alert` and `publish_employee_event` have **zero callers** (grep-confirmed above). `get_command_center_data` is **repair-only**. `CommandCenter.vue` is an **orphan** (no router entry). `LiveMonitor.vue` is a **stub**. `AdminMonitor.vue` **polls 30s, subscribes to nothing**. `_get_store_metrics` **skips zero-repair stores**. All three `publish_realtime` calls **broadcast globally**. The "Live Monitor" is currently 4 prototypes, not a product.

---

## (A) Module Vision & Role in the Suite

**Vision statement.** One screen that an owner mounts on a TV in the back office, a manager keeps open on a tablet on the floor, and an associate glances at on the POS between customers — each seeing exactly what their role permits, each updated by the same socket push, each able to drill from a live tile straight into Sales/Profit/Workforce depth. It is the *only* place in Zevar where "right now, across every store, is anything going wrong or going great" has a single answer.

**Design principles (opinionated):**

1. **Push-first, never poll-primary.** Every tile subscribes via `useRealtime`; polling (`usePolling`, exponential backoff, paused-when-hidden) is a *reconcile fallback*, never the source of truth. (Beats today's 30s-poll AdminMonitor and the dead-code anomaly publisher.)
2. **Never omit a quiet store.** The wall always shows every store the viewer is entitled to, with an explicit `idle/healthy` state — green emptiness, not absence. (Fixes `_get_store_metrics` skipping zero-repair stores.)
3. **One event schema, generated Python→TS.** No `new_status` vs `status` drift. The contract is `events_schema.py` + generated `realtime-events.ts`; CI fails the PR if they diverge.
4. **Scope on every event.** `room="admin_wall"` (owner+managers), `room="store_<wh>"`, or `user=<employee>`. Employee-attributed events are **never** broadcast globally. (Fixes the broadcast at `live_monitor.py:30,39,55` that undermines `employee_live_monitor.py`'s privacy scoping.)
5. **Role-aware, route-unified.** One route (`/reports/dashboards/command-center`), one `<router-view>`, three render variants (owner wall / manager wall / associate personal). Deletes the 4 fragmented screens.
6. **Jewelry signals first-class.** Live gold spot + sparkline, margin-at-risk stress widget, memo/consignment exposure, gold-purchase/scrap as a parallel buy-side feed — things no generic POS shows.
7. **TV/kiosk is a first-class mode, not an afterthought.** Auto-cycling slides, sticky-pin during incidents, visible "last updated" + stale-data warning.

**How it beats each competitor:**

| Competitor | Their Live story | Zevar's edge |
|---|---|---|
| **The Edge** | Configurable tile dashboards (Numeric/Gauge/Chart/List), per-associate or store-wide — but **static desktop reports, not streaming** | Same tile taxonomy (we adopt it) **plus** socket push, TV mode, multi-store live wall, jewelry COGS-at-risk. The Edge's "real-time" is inventory sync, not a management wall. |
| **Lightspeed** | Pulse / Insights Live — **gated to Custom/Insights tiers**, ~2–3h sync lag historically on retail line | Sub-minute push **by default** (not paywalled), true in-store + multi-store, gold-exposure widgets Lightspeed cannot model (its COGS is one weighted-average number). |
| **Shopify POS** | Live View is **online-store-centric** (globe + visitor dots); physical POS real-time walls are weaker, served by 3rd parties | Purpose-built for the **physical** jewelry floor: registers, repairs, memos out, gold spot, associate grid — Shopify Live View does none of this. |
| **RICS / Valigara / Jewel360** | Batch/scheduled reports; Jewelsteps has a manufacturing status-lane | We adopt Jewelsteps' status-lane for repairs **plus** a full ops/sales/health wall, push-first, with persistent `Operations Alert` workflow RICS entirely lacks. |
| **Datadog / Geckoboard / INOC (non-POS)** | Best-in-class TV walls + AIOps incident correlation | We port their TV rotation + incident-clustering pattern **into** jewelry ops — a category no jewelry POS has. |

---

## (B) Target Feature Set (grouped; each mapped to the gap/competitor it beats)

### B1. The Single Pane of Glass (SPOG) multi-store wall
- **All-stores strip** — one row per entitled store: live revenue, txn count, AOV, UPT, health dot, pace-to-target micro-gauge. *Beats* The Edge/Geckoboard TV mode; *fixes* `_get_store_metrics` skipping quiet stores.
- **System-wide hero KPIs** — revenue today, txn count, AOV, UPT, items, refund count/value, run-rate, projected-day-close, each with ▲/▼ vs prior period + YoY. *Beats* Lightspeed S-Series "delta arrow on every tile."
- **Pace-to-target gauge** per store (reads `Sales Target` via `sales_monitor.get_pace`). *Beats* Shopify/Lightspeed (no store-level target natively).
- **Quiet-store health** — explicit `idle/healthy` status; never omit. *Fixes* the current silent omission.

### B2. Live SALES in the command center (the #1 owner metric, today absent)
- Per-store live revenue / txn / AOV / UPT / items via `sales_monitor.get_summary` (reads `daily_store_sales_rollup`, sub-100ms). *Fixes* `get_command_center_data` being repair-only.
- Hourly trend (full 24h, zero-bucketed) via `sales_monitor.get_hourly` + `HourlyBarChart`. *Fixes* the hardcoded 9–21 window.
- Live recent-sales ticker (last-N invoices) driven by `sales_tick` events, not polling. *Replaces* `AdminMonitor.vue`'s 30s poll of `pos_session.get_live_sales_feed`.

### B3. Realtime event pipeline (replaces 3 broken publishers)
- Single `bus.publish()` entry point; `publish_anomaly_alert` / `publish_employee_event` **deleted**; `publish_repair_event` migrated to `bus.publish("repair_live", ...)`. *Fixes* B4.
- Anomalies move from poll-on-demand to **push-on-trigger**: `run_anomaly_push` scheduler (`*/2 * * * *`) + rule hooks fire `bus.publish("anomaly_alert", ...)`. *Fixes* the dead `publish_anomaly_alert`.
- 24h rolling `live_event_log` backfill; `useBackfill` hydrates a freshly-opened wall instantly. *Fixes* "empty feed until next poll."
- `useRealtime`: paused-when-hidden (resumes + backfills on visibilitychange), single-subscription-per-channel dedupe, exponential-backoff poll fallback. *Fixes* B7 (3 inconsistent HTTP clients / 4 fragmented subscriptions).

### B4. TV / Kiosk display mode
- Full-screen, large-font, high-contrast, auto-refresh; visible "last updated `HH:MM:SS`" + **stale-data warning** (>60s without an event turns the clock amber, >180s red). *Beats* Datadog/PowerMetrics/Geckoboard.
- Auto-cycling slides (Sales → Alerts → Repairs → Scoreboard → Health), ~20s each, with **sticky-pin override** during a critical incident. *Beats* Geckoboard.
- Read-only by default; a PIN unlocks interactive mode. *Beats* naive kiosk that lets customers poke around.

### B5. Operations Alert engine (persisted anomaly workflow)
- **`Operations Alert` doctype**: severity / type / status (`new`/`ack`/`snoozed`/`resolved`) / `assigned_to` / created / resolved / timeline (JSON). *Fixes* "alerts vanish when the page closes."
- **Rules** (static + rolling-baseline/z-score, not just thresholds):
  - Repair: severe overdue (>7d), stuck (>5d no change), unassigned (>24h), high-value-no-deposit (≥$500) — *kept from current engine*.
  - **Sales (new)**: zero-sale-hour during open session, volume drop >z=2 vs rolling 14-day same-hour baseline, AOV spike/drop, refund cluster (≥3 refunds/15min), discount-rate spike, register cash discrepancy > tolerance.
  - **Jewelry (new)**: gold price-shock (|Δ1h| > threshold, from `price_shock` channel), memo exposure breach (units/value over cap), margin-at-risk (gold value × +2%/+5% stress exceeds threshold).
  - **System (new)**: register offline >N min, POS Sync Log backlog >N, payment-gateway ping fail, hardware-bridge/printer down, offline-queue depth >N, API latency >p95.
- **Ack / snooze / resolve UI** + routing via `NotificationCenter` to in-app toast + email + push + Slack/WhatsApp. *Beats* INOC AIOps / Pricefx Agents pattern in a jewelry context.
- **Incident correlation** — cluster related signals into one incident card ("register offline + refund spike + negative margin") with MTTA/MTTR tracking. *Beats* every jewelry competitor (none have AIOps-style correlation).

### B6. Jewelry-specific live signals (no generic POS has these)
- **Live gold spot + sparkline** (from `metal_rate_history`), per purity, with Δ1h/Δ24h. *Beats* The Edge Spot Metal (which is at-POS prompt, not a live wall widget).
- **Margin-at-risk stress widget** — gold value of current inventory × −2%/−5%/+2%/+5% scenarios → $ at risk; flags if a price-shock just moved it. *Beats* every competitor (margin is descriptive everywhere else; we make it live-risk).
- **Memo/consignment exposure** — units + value out on loan, by customer/store, with overdue-call highlighting. *Beats* Valigara/Gem Logic (they model memo as a location, not a live exposure tile).
- **Gold-purchase/scrap feed** — parallel buy-side stream (grams in, $ paid, scrap margin) as a `sales_tick`-equivalent `gold_purchase` event. *Beats* The Edge trade-in module (report, not live).

### B7. System-health / device wall
- Register online/offline + last-seen, POS Sync Log backlog, payment-gateway ping, hardware-bridge/printer status, offline-queue depth, API latency p95, terminal battery (if reported). Fed by `system_health` channel + `hardware_bridge.py`. *Fixes* "no system-health monitoring" gap.

### B8. Live employee-activity grid (contact-center agent-wall pattern)
- Per-associate row: name, status badge (`with-customer`/`repairing`/`idle`/`break`/`offline`), time-in-state, current task, today's revenue/txn (manager+ only). Drives both the owner wall and demand-based scheduling. *Beats* Jewelsteps Salesperson Dashboard (static) with live state.

### B9. Live conversion funnel (rolling 10-min window)
- Footfall → greeted → engaged/try-on → purchased, sourced from `Store Traffic Log` (people-counter adapter or manual POS entry). *Adapts* Shopify Live View's online funnel to the physical store — impossible in any current jewelry POS without a traffic source.

### B10. Offline / resilience mode
- Cache last-known-good tile state; mark stale tiles; queue missed events for backfill on reconnect; the 24h `live_event_log` is the source of truth on resume. *Fixes* "no resilience."

### B11. Associate personal live view (role variant)
- `EmployeeLiveMonitor` content (today/yesterday revenue, items, active session, anonymized store hourly activity, personal task queue) rendered inside the same route for the associate tier — fed by `associate_personal` channel (user-scoped, never global). *Fixes* the broadcast that undermined its privacy scoping.

---

## (C) Information Architecture — Screens, Layout, Widgets, Role Variants

### C1. One route, three role variants

**Route:** `/reports/dashboards/command-center` → `pages/dashboards/CommandCenter.vue` (rebuilt). `meta: { requiresAuth: true, permission: 'monitor.view' }`. The 4 old screens are deleted/merged:

| Old screen | Disposition |
|---|---|
| `pages/LiveMonitor.vue` (stub) | **Delete**; redirect `/live-monitor` → command-center |
| `pages/dashboards/CommandCenter.vue` (orphan, repair-only) | **Rebuild in place** as the unified wall |
| `pages/dashboards/AdminMonitor.vue` (polls, no realtime) | **Merge** content (sales/registers/audit) into the wall widgets; delete file |
| `pages/dashboards/EmployeeLiveMonitor.vue` | **Keep as associate variant** rendered inside the same route |

Role variant is selected by `permissions.js` (`canAccessMonitor()` tier): owner = full multi-store wall; manager = their stores; associate = personal view (`EmployeeLiveMonitor` content). One `<router-view>`, one `useRealtime` subscription set.

### C2. Owner/Manager wall layout (12-column grid, responsive; TV mode = same grid, larger fonts, no chrome)

```
┌───────────────────────────────────────────────────────────────────────┐
│ TOP BAR: live clock | "Last updated HH:MM:SS" (amber>60s/red>180s) |  │
│          ⚡LIVE | timeStore quick-preset | store multi-select | TV mode │
├─────────────────────── HERO KPI ROW (6 KPICards) ──────────────────────┤
│ Revenue ▲12% | Txns ▲8% | AOV ▲3% | UPT ▼1% | Items ▲6% | Refunds ▼20% │
│   (each: KpiSparkline, vs prior + YoY, click→Sales Monitor drill)      │
├─────────── ALL-STORES STRIP ────────────┬──── GOLD / MARGIN RAIL ─────┤
│ Store A  $4.2k ▲  18 txn  ●healthy  82% │ Spot Au 24K  $2,340 ▲0.8%   │
│ Store B  $1.1k ▼   4 txn  ●idle         │ Margin-at-risk  −5%→ −$18k ⚠│
│ Store C  $0       0 txn  ●offline 🔴    │ Memo out  42u / $96k        │
│   (pace gauge per store; click→store)   │ Scrap today  12g / $640     │
├──────────── SALES TICKER ───────────────┴──── REPAIR STATUS LANE ─────┤
│ 14:32  Inv #2041  $890  Ring 18K   S.B┐  In-Work 6 │ Ready 3 │ Overdue│
│ 14:31  Inv #2040  $1.2k Watch        │  2 │ Received 4 │ Pickup 1    │
│ 14:30  Refund #1129 -$210 (alert⚠)   │  (Jewelsteps status-lane pattern)│
├──────── ASSOCIATE ACTIVITY GRID ───────┴──── OPERATIONS ALERTS ────────┤
│ Sam B.  🟢with-cust  6m  3/$2.1k       │ 🔴 Register C offline 4m  [ack]│
│ Mia T.  🟡idle       9m  1/$0.4k       │ 🟡 Refund cluster 14:25   [snooze]│
│ Dev R.  🔵repairing  22m 0/$0          │ 🟢 Gold +0.8% — cleared    │
├──────── CONVERSION FUNNEL (10-min) ─────┴──── SYSTEM HEALTH ───────────┤
│ 42 in → 28 greeted → 14 try-on → 6 buy │ Registers 3/4 up │ Sync 12 lag│
│  (ConversionFunnel.vue)                │ Gateway ● │ Printer B ● │ API p95 180ms│
└─────────────────────────────────────────────────────────────────────────┘
                         ALERT TICKER (marquee) — scrolling, no tile cost
```

### C3. TV / Kiosk mode
- Triggered by `?tv=1` or a toggle in the top bar. Hides interactive chrome (filters, ack buttons), enlarges fonts 1.6×, enables **slide rotation** (Sales → Alerts → Repairs → Scoreboard → Health, ~20s each). **Sticky-pin**: a critical alert pins the Alerts slide until resolved. Top-bar clock always visible; stale-warning governs trust. *Patterns:* Datadog TV, Geckoboard, PowerMetrics.

### C4. Manager variant
- Same grid, but `store multi-select` is locked to the manager's stores (enforced server-side via `only_for` reconciliation + the `store_<wh>` room subscription). Associate-activity grid shows only their team. No cross-store financial rollup they're not entitled to.

### C5. Associate variant (`EmployeeLiveMonitor` content)
- Personal KPI heroes (today vs yesterday revenue, items, active session), anonymized store hourly activity (amounts stripped — preserve the honest privacy scoping at `employee_live_monitor.py:96-172`), personal task queue (assigned repairs, layaway follow-ups, todos). Fed by `associate_personal` channel (user-scoped). No peer amounts, no wall, no TV mode.

---

## (D) Data Model — New/Changed Doctypes + Materialized Tables + Reuse

### D1. New doctype: `Operations Alert` (under `…/doctype/operations_alert/`)
| Field | Type | Notes |
|---|---|---|
| `alert_id` | Data (autoname `OA-YYMMDD-#####`) | PK |
| `severity` | Select (`critical`/`warning`/`info`) | |
| `type` | Select (repair_overdue / sales_volume_drop / refund_cluster / discount_spike / cash_discrepancy / gold_shock / memo_breach / margin_at_risk / register_offline / sync_lag / gateway_down / printer_down / queue_depth / api_latency) | |
| `title` / `description` | Data / Small Text | human-readable |
| `store` | Link→Warehouse | scope |
| `status` | Select (`new`/`ack`/`snoozed`/`resolved`) | default `new` |
| `assigned_to` | Link→User | routing |
| `correlation_id` | Data | groups related signals into one incident |
| `rule_fired` | Data | rule name + version (audit) |
| `evidence` | JSON | the metric snapshot that triggered |
| `timeline` | JSON | `[{ts, user, action, note}]` ack/snooze/resolve |
| `created_at` / `acked_at` / `resolved_at` | DateTime | MTTA/MTTR |
| `snooze_until` | DateTime | |

### D2. New doctype: `Live Monitor Layout` (per-user TV/wall config; The Edge "named dashboard" pattern)
| Field | Type | Notes |
|---|---|---|
| `user` | Link→User | PK part |
| `name` | Data | e.g. "Back-office TV", "Manager tablet" |
| `is_default` / `is_tv` | Check | |
| `slides` | JSON | ordered slide list for TV rotation |
| `pinned_alert_severities` | JSON | which severities pin |
| `store_filter` | JSON | scoped stores |

### D3. New materialized tables (owned by the Shared Platform; Live Monitor reads)
- `live_event_log` — 24h rolling backfill (PK `id` uuid, `ts`, `channel`, `event_type`, `store`, `actor_user`, `payload` JSON, `schema_version`). Live Monitor's `useBackfill` reads the tail.
- `daily_store_sales_rollup` — Live Monitor hero KPIs + store strip read this (sub-100ms).
- `metal_rate_history` — gold spot sparkline + margin-at-risk + price-shock detection.
- `employee_period_rollup` — associate-activity grid reads today's row per associate.

### D4. New doctypes Live Monitor **consumes** (owned by other modules/platform)
- `Store Traffic Log` (platform §7) → conversion funnel.
- `Sales Target` (platform §8) → pace gauge.
- `Sales Invoice.custom_sales_channel` (platform §8) → channel split on the ticker/hero.

### D5. EXISTING doctypes to reuse (do NOT rebuild)
- **`Repair Order`** — repair status-lane + repair live feed (status, promised_date, assigned_to, deposit_amount, estimated_cost, warehouse, modified).
- **`POS Closing Entry` / `POS Opening Entry`** — register open/close, floats, expected/counted cash → register health + cash-discrepancy anomaly.
- **`POS Profile`** — register identity.
- **`Sales Invoice` / `Sales Invoice Item` / `Sales Invoice Payment`** — sales ticker, hero KPIs (via rollup, never direct N+1).
- **`Sales Commission Split`** — associate attribution for the activity grid (via `employee_period_rollup`, not raw).
- **`Performance Log`** — associate status/time-in-state feed (after platform wires `log_sale_event`).
- **`Memo Contract` / `Layaway Contract` / `Gold Purchase`** — memo exposure, layaway follow-ups, scrap feed.
- **`Gold Rate Log`** — (alongside `metal_rate_history`) fallback spot source.
- **`POS Sync Log`** (ERPNext) — sync-lag health.
- **`Notification Log` / `Notification`** (Frappe) — alert routing via NotificationCenter (email/push/Slack/WhatsApp).

---

## (E) API Surface — Endpoints, Purpose, Method

All under `zevar_core.api.command_center.*` (new module; the old `live_monitor.py` is reduced to a thin compat shim or deleted). All role-gated via `only_for` reconciled with `permissions.js` (platform §5.4: System Manager, Administrator, Store Manager, **Accounts Manager**, **Sales Manager** — adding Sales Manager fixes the `live_monitor.py:78` omission).

| Endpoint | Method | Purpose |
|---|---|---|
| `command_center.get_wall_state` | GET (whitelisted) | Initial wall payload: hero KPIs, store strip, repair lane, associate grid, funnel, health, open alerts. One round-trip hydration. |
| `command_center.get_backfill` | GET (whitelisted) | `?hours=24&channels=...` tail of `live_event_log` for `useBackfill`. Streams dedup-ready envelopes. |
| `command_center.get_sales_ticker` | GET | Last-N invoices (replaces `pos_session.get_live_sales_feed` polling). |
| `command_center.get_repair_lane` | GET | Repair status-lane counts + recent status changes (reuses `get_repair_live_feed` logic). |
| `command_center.get_associate_grid` | GET | Per-associate status/time-in-state/today's KPIs (manager+ only; reads `employee_period_rollup`). |
| `command_center.get_health` | GET | Register/sync/gateway/printer/queue/API-latency snapshot. |
| `command_center.get_margin_risk` | GET | Gold exposure × scenarios; memo exposure; scrap feed. |
| `command_center.get_pace` | GET | Per-store pace-to-target (delegates `sales_monitor.get_pace`). |
| `command_center.ack_alert` | POST | Set status `ack`, `assigned_to`, append timeline. |
| `command_center.snooze_alert` | POST | Set `snooze_until`. |
| `command_center.resolve_alert` | POST | Set status `resolved`, `resolved_at`. |
| `command_center.save_layout` / `get_layout` | POST / GET | TV/wall layout persistence (`Live Monitor Layout`). |
| `command_center.enter_tv` / `exit_tv` | POST | Server-side TV session register (drives slide-state + pinned-alert eval). |

> The realtime path uses **no HTTP for live updates** — it is `bus.publish` → socket.io → `useRealtime`. HTTP above is hydration + mutations only.

---

## (F) Realtime & KPI Wiring (per Shared Platform)

### F1. Channels consumed by the Command Center

| Channel | Room/Scope | What the wall does with it |
|---|---|---|
| `command_center` | `room="admin_wall"` | universal fan-out; owner/manager wall hydration |
| `store_ops` | `room="store_<wh>"` | per-store widget updates for manager variant |
| `associate_personal` | `user=<employee>` | associate variant personal KPIs (NEVER global) |
| `repair_live` | `admin_wall` + `store_<wh>` | repair status-lane tile |
| `sales_tick` | `admin_wall` + `store_<wh>` | sales ticker + hero KPI increment + store strip |
| `anomaly_alert` | `admin_wall` | alert ticker + Operations Alert card |
| `price_shock` | `admin_wall` | gold sparkline + margin-at-risk recompute |
| `system_health` | `admin_wall` | health tile (register offline, sync lag, etc.) |

### F2. Event types (subset of `events_schema.py` the wall consumes)
`sale.completed`, `refund.processed`, `void.processed`, `repair.status_changed`, `session.opened`/`session.closed`, `anomaly.fired`/`anomaly.acked`/`anomaly.resolved`, `price.metal_shock`, `health.heartbeat`/`health.offline`, `associate.state_changed`, `gold.purchase_submitted`, `memo.out`/`memo.returned`.

### F3. Rollup tables read
- Hero KPIs & store strip → `daily_store_sales_rollup` (today's row, sub-100ms).
- Associate grid → `employee_period_rollup` (today, daily).
- Gold widgets → `metal_rate_history` (last 24h sparkline + Δ windows).
- Backfill → `live_event_log`.

### F4. Frontend wiring
- `useRealtime({ command_center, sales_tick, anomaly_alert, repair_live, price_shock, system_health, store_ops })` — single subscription set, deduped, paused-when-hidden.
- `useDashboardData('command_center.get_wall_state', { auto: true })` — initial hydration respecting `timeStore`.
- `useBackfill` — on mount + on tab-visible, merge `live_event_log` tail, dedupe on `envelope.id`, apply in `ts` order.
- `usePolling` — backoff (base 10s, cap 60s) reconcile fallback; resets on a successful realtime event.
- All charts via ECharts primitives (`KpiSparkline`, `HourlyBarChart`, `ConversionFunnel`); all formats via `utils/format.js`; all colors via `utils/status-colors.js`.

---

## (G) KPIs with Precise Formulas

| KPI | Formula | Source |
|---|---|---|
| **Revenue (today)** | `SUM(grand_total) WHERE is_pos=1 AND docstatus=1 AND posting_date=CURDATE() AND store IN scope` | `daily_store_sales_rollup.gross_revenue` |
| **Net revenue** | `SUM(net_total)` same scope | `daily_store_sales_rollup.net_revenue` |
| **Transaction count** | `COUNT(DISTINCT invoice)` same scope | `invoice_count` |
| **AOV (avg sale value)** | `net_revenue / txn_count` (NULL→0) | derived |
| **UPT (units per transaction)** | `SUM(qty) / COUNT(DISTINCT invoice)` | `unit_count / invoice_count` |
| **Attach rate** | `COUNT(invoices WITH qty≥2) / COUNT(invoices)` | derived |
| **Refund count / value** | `COUNT(is_return=1)` / `SUM(grand_total WHERE is_return=1)` | `refund_count` / `refund_value` |
| **Refund rate** | `refund_count / (invoice_count + refund_count)` | derived |
| **Run-rate (hourly)** | `revenue_so_far / hours_open` (hours_open from earliest session open to now) | derived |
| **Projected-day-close** | `run_rate × total_open_hours` (or `revenue_so_far + run_rate × hours_remaining`) | derived |
| **Pace-to-target %** | `revenue_today / target_revenue × 100` (`Sales Target`) | `sales_monitor.get_pace` |
| **Conversion rate (10-min)** | `purchases / visitors_in` (last 10 min) | `Store Traffic Log` + invoices |
| **Gold Δ1h / Δ24h** | `(rate_now − rate_1h_ago)/rate_1h_ago × 100` | `metal_rate_history.delta_pct_1h` |
| **Margin-at-risk ($)** | `SUM(net_weight × gold_rate × qty) × |scenario_pct|` (per scenario) | Items + `metal_rate_history` |
| **Memo exposure** | `SUM(value_out_on_loan)` + `COUNT(units_out)` | `Memo Contract` |
| **Cash discrepancy** | `ABS(counted_cash − expected_cash)` | `POS Closing Entry` |
| **MTTA (alert)** | `AVG(acked_at − created_at)` over resolved window | `Operations Alert` |
| **MTTR (alert)** | `AVG(resolved_at − created_at)` | `Operations Alert` |
| **Sync lag** | `NOW() − MAX(POS Sync Log.modified)` | `POS Sync Log` |
| **API latency p95** | p95 of wall-hydration round-trips | client telemetry |
| **Profit per store-hour** | `gross_profit (SCB) / operating_hours` (platform HotStats-analogue; reads SCB via `profit_math`) | `sale_cost_breakdown` |
| **Profit per associate-hour** | `associate gross_profit / hours_worked` | SCB + `employee_period_rollup.hours_worked` |

---

## (H) UX Patterns Worth Copying (cited)

- **The Edge tile taxonomy** (Numeric/Gauge/Chart/List, scoped per-associate or store-wide, named multi-dashboards) → `Live Monitor Layout` configurable tiles. *(research: The Edge Dashboards)*
- **Lightspeed S-Series** "period-over-period ▲/▼ delta on EVERY tile" → every hero KPI + store strip cell. *(research: Lightspeed Live Monitoring)*
- **Lightspeed** "same-type=OR, different-type=AND" filter rule, surfaced in UI → store/channel filter bar. *(research: Lightspeed)*
- **Lightspeed** "View report" drill-down that inherits dashboard filters → every tile drills into Sales/Profit/Workforce with filters pre-applied (no re-filter). *(research: Lightspeed)*
- **Shopify Live View** rolling 10-min funnel (active carts → checkout → purchased) → physical-store funnel (footfall → greeted → try-on → purchase). *(research: Shopify Live Monitoring)*
- **Jewelsteps Manufacturing Dashboard** status-lane cards (in-progress/delayed/on-hold + per-workstation + overdue highlight) → repair status-lane tile. *(research: Valigara cluster)*
- **RICS** ubiquitous multi-store control (Separate/Combine/Compare/Store Summary) → store-strip + store multi-select. *(research: RICS)*
- **INOC AIOps / Pricefx Agents** incident correlation + ack/snooze/resolve routing → `Operations Alert` incident cards. *(research + wf1)*
- **Datadog / Geckoboard / PowerMetrics** TV mode: auto-rotation, sticky-pin during incidents, visible "last updated" + stale warning → TV/kiosk mode. *(wf1 Best-in-Class)*
- **Nextiva/Geomant** scrolling alert ticker/marquee for anomalies without consuming tile space → alert ticker bar. *(wf1)*
- **HotStats/STR/Duetto** GOPPAR analogue → profit-per-store-hour live metric (jewelry-specific COGS via `profit_math`). *(wf1)*

---

## (I) Permissions & Privacy (esp. associate-data isolation)

**Single source of truth:** `utils/permissions.js` (`canAccessMonitor()`, `canAccessSalesPerformance()`, `isOwnSalesOnly()`). Router meta uses permission keys, not role lists. Client-side `beforeEach` guard renders `<NoAccess />` instead of flashing chrome then 403-ing. *(Fixes B5, B6.)*

**Backend `only_for` reconciliation** (platform §5.4): Command Center = System Manager, Administrator, Store Manager, **Accounts Manager**, **Sales Manager**. This **adds Sales Manager**, fixing the `live_monitor.py:78` omission that today blocks a Sales Manager who passes `canAccessMonitor()`. The `admin_monitor.json` desk-page role gate is aligned to the same list (fixes the desk/SPA mismatch where Sales Manager loads the iframe then is redirected).

**Privacy — the iron rule:** any event referencing a named employee, customer, or commission MUST publish with `user=` (personal) or to a manager-only `room=`. The current `publish_employee_event` global broadcast **violates** this and is deleted. The associate variant receives only `associate_personal` events scoped `user=<self>`. The manager/owner wall's associate-activity grid shows peer rows **only** to manager+ roles (server-enforced via `get_associate_grid` `only_for`); associates never see peer amounts. `get_store_activity` is fixed to scope to the employee's store (today it aggregates ALL stores company-wide — a cross-store volume leak). The honest anonymization in `employee_live_monitor.py:96-172` (amounts stripped from store hourly counts) is preserved.

---

## (J) Integration with the Other 3 Modules + Native Frappe Stack

**Sales Monitor:** hero KPIs, store strip, pace gauge, ticker all delegate to `sales_monitor.*` + `daily_store_sales_rollup`. Every tile's "View report" drill navigates (SPA, no reload) into Sales Monitor with `timeStore` + filters inherited.

**Profit Intelligence:** margin-at-risk + profit-per-store-hour widgets read SCB via `profit_math.compute_invoice_margin` (the sole margin definition, post-platform §2.2). A margin-at-risk alert drills into the Profit Margin Waterfall. `price_shock` events originate from the metal-rate fetch the Profit module owns.

**Workforce Intelligence:** associate-activity grid + scoreboard slide read `employee_period_rollup` (which, post-platform §2.4, is canonical — no more Performance-Log-vs-Commission-Split divergence). Associate status/time-in-state comes from Performance Log events the platform wires. The scoreboard slide is the TV-mode rendering of the Workforce leaderboard.

**Native Frappe stack (extend, don't rebuild):**
- `frappe.publish_realtime` (socket.io) — the transport under `bus.publish`.
- **Frappe Insights Alert** — for scheduled email/Telegram alert delivery; `Operations Alert` routing extends this to push/Slack/WhatsApp via NotificationCenter. Deep no-code owner BI stays in Insights Workbooks; Live Monitor owns realtime only (platform §9.1 rule — no duplication).
- **Workspace / Number Card / Dashboard Chart** — owner landing glance tiles; Live Monitor is the deep realtime surface they link into.
- **`Notification Log` / `Notification`** — alert routing substrate.
- **HRMS Employee Checkin/Shift** — drives associate status/time-in-state once wired.
- **ERPNext `POS Sync Log`, `POS Closing Entry`, `POS Opening Entry`** — register health + cash discrepancy, unchanged.

---

## (K) Phased Build WITHIN This Module (P0 must / P1 should / P2 nice)

> Each task is concrete and assignable. Platform-core tasks (B1–B7: `bus.py`, `events_schema.py`, rollups, `profit_math`, SCB hook, `log_sale_event`, `useRealtime`, `utils/format.js`, `timeStore`, SPA router-view fix, single permission model) are **prerequisites owned by the platform track** — listed here only where the module contributes a delta.

### P0 — Must (the module is unusable without these)

1. **Collapse to one route.** Delete `pages/LiveMonitor.vue` (redirect to command-center); rebuild `pages/dashboards/CommandCenter.vue` as the role-aware wall; fold `AdminMonitor.vue` sales/registers/audit into wall widgets and delete the file; register the route in `router.js` with `meta.permission: 'monitor.view'`; fix the `Dashboards.vue` card with no `route:`. *(Fixes orphan route + dead stub + 4 fragmented screens.)*
2. **Wire the realtime pipeline.** Migrate `publish_repair_event` → `bus.publish("repair_live", ...)`; **delete** `publish_anomaly_alert` + `publish_employee_event` (dead code); add `run_anomaly_push` scheduler `*/2 * * * *` + rule hooks so anomalies push on cadence with no screen open; add `system_health` heartbeat scheduler `*/5 * * * *`. *(Fixes B4.)*
3. **Stop broadcasting.** Every live event goes through `bus.publish` with `room=`/`user=` scoping; employee events user-scoped only. *(Fixes the privacy-undermining broadcast.)*
4. **Add live SALES to the wall.** `command_center.get_wall_state` hero KPIs + store strip + ticker delegate to `sales_monitor.get_summary`/`get_hourly`/`get_pace` reading `daily_store_sales_rollup`. Repair-only `get_command_center_data` is replaced. *(Fixes the #1 owner metric being absent.)*
5. **Stop hiding quiet stores.** Wall returns ALL entitled stores with explicit `idle/healthy/offline` status. *(Fixes `_get_store_metrics` skip.)*
6. **Adopt `useRealtime` + `useBackfill` + `useDashboardData`** in the wall; delete raw `fetch()`+CSRF / `call` / `createResource` triad from the 4 old screens. *(Fixes B7 inconsistent HTTP clients.)*
7. **Adopt ECharts primitives + `utils/format.js` + `utils/status-colors.js`**; delete the duplicated `statusBarColor`/`healthDot` maps and bespoke SVG bars. *(Fixes 17 fmt() copies + magic status maps.)*
8. **Operations Alert doctype + ack/snooze/resolve UI** for the existing 4 repair rules (persisted, routed via NotificationCenter). Anomalies stop vanishing on page close.
9. **Visible "last updated" + stale-data warning** in the top bar (amber >60s, red >180s).

### P1 — Should (makes it best-in-class)

10. **TV / Kiosk mode** — full-screen, slide rotation (Sales→Alerts→Repairs→Scoreboard→Health), sticky-pin on critical, `?tv=1` + `Live Monitor Layout` persistence.
11. **Sales + jewelry anomaly rules** — volume-drop (z-score vs 14-day same-hour baseline), zero-sale-hour-during-open-session, AOV spike/drop, refund cluster, discount spike, cash discrepancy, gold price-shock (consume `price_shock`), memo exposure breach, margin-at-risk.
12. **System-health tile** — register online/offline + last-seen, POS Sync Log backlog, payment-gateway ping, hardware-bridge/printer status, offline-queue depth, API latency p95.
13. **Jewelry live rail** — gold spot sparkline + Δ1h/Δ24h (`metal_rate_history`), margin-at-risk stress widget, memo/consignment exposure, gold-purchase/scrap feed.
14. **Live associate-activity grid** (manager+ only) — status badge, time-in-state, current task, today's KPIs from `employee_period_rollup`.
15. **Incident correlation** — cluster related alerts into one incident card (`correlation_id`) with MTTA/MTTR.
16. **Conversion funnel** (10-min rolling) — once `Store Traffic Log` exists (platform §7), wire `ConversionFunnel.vue`.
17. **Alert ticker marquee** + routing to email/push/Slack/WhatsApp via NotificationCenter.
18. **All tiles' "View report" drill-down** into Sales/Profit/Workforce inheriting `timeStore` + filters (SPA `router.push`, no reload).

### P2 — Nice (differentiators/polish)

19. **Live Monitor Layout editor** — drag-and-drop tile config (The Edge named-dashboard pattern), per-user + per-device (TV vs tablet).
20. **Offline/resilience cache** — last-known-good tile state + queued-event backfill on reconnect.
21. **Predictive anomaly baselines** — seasonality-aware (day-of-week × hour-of-day) z-score beyond static thresholds; gold-rate elasticity on volume.
22. **Margin-at-risk drill** → Profit Margin Waterfall with the scenario pre-loaded.
23. **Profit-per-store-hour / profit-per-associate-hour** live tiles (HotStats GOPPAR analogue).
24. **EOD "overnight" digest** — scheduled email/push recap for owners not watching the wall (Lightspeed Sales Summary email pattern).

---

## (L) Success Metrics / Acceptance Criteria (proving best-in-class)

**Freshness / realtime integrity**
- A sale posted at the POS appears on an open owner wall in **< 3s** p95 (socket push), vs the current 30s poll. Measured by client telemetry (`event.ts` → render).
- A freshly-opened wall hydrates from `useBackfill` in **< 1.5s** with no empty-feed gap (vs today's "blank until next poll").
- `document.hidden` pauses subscriptions; on visibility resume, backfill merges with **zero duplicate renders** (dedupe on `envelope.id`).
- Zero events broadcast globally — grep for `publish_realtime(` without `room=`/`user=` in `live_monitor`/`command_center` returns **nothing**.

**Correctness / data integrity**
- Hero KPIs on the wall reconcile to the EOD Z-report and to `sales_monitor.get_summary` to the penny (single rollup source — no more 5-way divergence).
- Every entitled store appears in the strip; a store with zero sales shows `●idle`, never omitted.
- `gross_margin_pct` shown anywhere on the wall equals `profit_math.compute_invoice_margin` output (single margin definition).
- The TS event types in `realtime-events.ts` match `events_schema.py` — CI gate `gen_realtime_types.py --check` passes (kills `new_status` vs `status` drift).

**Operational**
- Anomaly **MTTA < 5 min** for critical alerts (ack workflow exists; today alerts vanish).
- A register going offline surfaces a `system_health` alert in **< 2 min** (vs today: not detected at all).
- TV mode runs 24h unattended with no stale-data confusion (clock-stale warning fires reliably > 60s/180s).

**Adoption / parity**
- All 4 old screens deleted/merged; one route, one `<router-view>`, one subscription set. `git grep "function fmt("` in `pages/dashboards/` returns **0** (all use `utils/format.js`).
- Sales Manager role can open the wall (today blocked by `live_monitor.py:78`) — verified by an automated role-matrix test.
- The wall shows live sales, repairs, alerts, health, associates, gold, memo exposure, conversion — a feature checklist no single competitor matches (The Edge = static tiles; Lightspeed = paywalled + laggy; Shopify = online-only; Jewelsteps = manufacturing-only).

**The "best-in-class" proof:** an owner mounts the wall on a TV, walks away, and the first time gold spikes 3% they learn it from Zevar's margin-at-risk alert — not from the evening news, and not from a 30-minute-stale poll. That moment is the product.

---

### Key file-path index (all absolute)

**Backend (new):**
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/command_center.py` (new — replaces `live_monitor.py` as the wall service)
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/unified_retail_management_system/doctype/operations_alert/` (new)
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/unified_retail_management_system/doctype/live_monitor_layout/` (new)

**Backend (platform-owned, consumed):**
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/realtime/{bus.py,events_schema.py,hooks.py}`
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/sales_monitor.py`
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/services/profit_math.py`
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/hooks.py` (add schedulers + doc_events; delete dead publishers' callers)

**Backend (delete/clean):**
- `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/live_monitor.py:37-60` (delete `publish_anomaly_alert`, `publish_employee_event`)

**Frontend (rebuild/merge):**
- `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/pages/dashboards/CommandCenter.vue` (rebuild)
- `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/pages/LiveMonitor.vue` (delete + redirect)
- `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/pages/dashboards/AdminMonitor.vue` (merge → delete)
- `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/pages/dashboards/EmployeeLiveMonitor.vue` (associate variant)
- `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/router.js` (register command-center route, `meta.permission`)
- `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/components/reports/Dashboards.vue` (fix the route-less "Command Center" card)

**Frontend (platform-owned, consumed):**
- `…/src/composables/{useRealtime.js,useDashboardData.js,usePolling.js,useBackfill.js}`
- `…/src/utils/{format.js,status-colors.js}`, `…/src/stores/time.js`, `…/src/types/realtime-events.ts`
- `…/src/components/charts/{KpiSparkline.vue,HourlyBarChart.vue,ConversionFunnel.vue}`
