# Zevar — Sales Monitor: Target Design

> **Lead Designer deliverable.** A complete, engineering-ready target design for the Sales Monitor module, built on the Zevar Frappe/ERPNext stack and the **Shared Cross-Cutting Platform**. Every file path, doctype, column, endpoint, and KPI formula is concrete and assignable.
>
> **Grounding:** This is the *weakest* of the four modules today — there is **no dedicated Sales Monitor**. Sales-performance visibility is fragmented across 6 surfaces that do not agree (`Revenue.vue`, `AdminMonitor.vue` "Live Monitor", the `analytics_hub.py` sales hero, the `reports.py` REPORT_CATALOG, iframe-embedded native Script Reports, and the EOD closeout). The single most important sales-monitor KPI — **conversion rate** — is *structurally impossible* because there is zero foot-traffic data anywhere. This design closes that gap and supersedes every fragment.

---

## (A) Module Vision & Role in the Suite

**One-liner:** Sales Monitor is the *analytical* lens on what sold, to whom, through which associate/channel, at what velocity, against which target — the historical and comparative counterpart to Live Monitor's *moment-by-moment* pulse and Profit Intelligence's *margin* lens.

**Position in the 4-module suite:**

| Module | Time lens | Question it answers | Sales Monitor feeds / feeds-from |
|---|---|---|---|
| **Live Monitor (Command Center)** | Now (sub-second) | "What is happening right now?" | Consumes `sales_tick` events Sales Monitor's hooks emit; shares `daily_store_sales_rollup` for the live sales tile |
| **Sales Monitor** | Period (hour→year) | "What sold, why, vs whom, vs target?" | **Owns** all sales KPIs; the single sales-aggregation spine the other modules delegate to |
| **Profit Intelligence** | Margin lens | "How much did we actually make on that?" | Reads SCB rows Sales Monitor's `on_submit` hook persists; drill-through from a leaderboard row lands on Profit's invoice margin view |
| **Workforce Intelligence** | People lens | "Who is performing and how do we pay them?" | Reads `employee_period_rollup`, which Sales Monitor rebuilds; leaderboard conversion/UPT columns are Workforce inputs |

**Why it becomes best-in-class:** It is the only one of the four that can combine (1) real foot-traffic → conversion (the universal jewelry-POS gap), (2) a unified sales-KPI spine that kills the 5-way "today's sales" drift, (3) RICS-style parametric report-building with a shared filter grammar, and (4) jewelry-native dimensions (metal/purity/gem/jewelry-type) that no generic retail POS models — all inside one role-aware SPA shell on the shared platform.

**The one architectural decision that defines this module:** `zevar_core/api/sales_monitor.py` becomes the **sole** sales-aggregation service. `revenue_dashboard.py`, the EOD revenue section (`reports.py:_eod_revenue`), `analytics_hub.py`'s sales hero, and `sales_history.py:get_sales_summary` stop computing their own totals and **delegate**. The 5 duplicate "today's sales" SQL implementations collapse to one, and all reads go through the `daily_store_sales_rollup` table for sub-100ms response.

---

## (B) Target Feature Set (grouped; each item mapped to the gap/competitor it beats)

### B1. The unified sales-KPI spine — *beats Zevar's own 5-way drift*
- **Single source of truth:** all sales KPIs computed in `sales_monitor.py` reading the rollup table. `revenue_dashboard.py`, EOD revenue, analytics hero, `sales_history` delegate here. *(Gap: "duplicate today's-sales SQL across 5 modules.")*
- **Sub-100ms rollup reads:** `daily_store_sales_rollup` (date × store × salesperson × channel × category × metal) refreshed on invoice submit/cancel + nightly safety rebuild. *(Gap: "no caching layer; EOD fires 15+ raw queries.")*

### B2. The conversion-rate breakthrough — *beats The Edge + TraxSales, Lightspeed, RetailPro*
- **`Store Traffic Log` doctype + people-counter adapter** via the existing `scripts/hardware_bridge.py`. v1 ships **manual POS-staff traffic entry on session open/close** as the pragmatic fallback; v2 integrates a supported people-counter device. *(Gap: "zero foot-traffic capture anywhere — conversion impossible.")*
- **Conversion Rate as a headline KPI**, sliced by hour-of-day and day-of-week heatmap. *(Best-in-Class target: "Conversion rate as headline KPI… TraxSales/Hoxton/Dor-style.")*
- **ConversionFunnel:** footfall → greeted → try-on → purchase, with per-stage drop-off %. *(The Edge TraxSales "manage your unsold customers.")*

### B3. The KPIs that were free but never computed — *beats Zevar today*
- **UPT, IPT, attach rate, basket depth, refund/void rate, run-rate, projected-day-close** — all derivable from existing `tabSales Invoice Item.qty` + invoice totals. *(Gap: "NO UPT/IPT anywhere; qty available but unused.")*
- **20/80 attribution:** auto-detect the ~20% of customers driving 80% of revenue and the handful of vendors/SKUs driving most sales. *(The Edge pattern.)*

### B4. The trend depth that was missing — *beats Shopify + Lightspeed*
- **Multi-granularity trend:** hour / hour-of-day / day / day-of-week / week / month / year with selectable **prior-period + YoY/WoW overlay** on the same `TrendLineChart`. *(Gap: "every SPA dashboard single-day-only; no date picker.")*
- **Global time-range store** drives every widget; switching range re-fetches the whole module. *(Platform §4.3.)*

### B5. Multi-store & channel as first-class — *beats RICS, Shopify*
- **One-tap store control** (Separate / Combine / Compare / Store Summary) on every report. *(RICS proves this is table-stakes for multi-store.)*
- **Channel comparison:** In-Store / Online / Phone / B2B / Memo via `Sales Invoice.custom_sales_channel`. *(Gap: "channel not modeled anywhere.")*

### B6. Sales targets & live pacing — *beats Toast + Lightspeed*
- **`Sales Target` doctype** (store × period × revenue/units/UPT/conversion), distinct from employee `Performance Target`. *(Gap: "targets exist only in workforce-comp, no store sales pacing.")*
- **Pacing-to-target gauge + projected-day-close run-rate.** *(Toast/Lightspeed pattern.)*

### B7. The report-builder grammar — *beats RICS + Shopify + Lightspeed*
- **Metrics × Dimensions × Filters × Period** with a **shared filter grammar** (`By Store / Salesperson / Category / Metal / Gem / Channel / SKU / Customer`), same-type=OR / different-type=AND, per-field Exclude toggle. One composable criteria object shared across all 4 modules. *(RICS synthesis.)*
- **In-place "Measure" swap, period-over-period delta arrows (▲/▼), inline pivot ("Format results").** *(Shopify/Lightspeed ergonomics.)*

### B8. Salesperson leaderboard, finally complete — *beats Lightspeed*
- Ranked on **revenue + UPT + conversion + attach rate + margin + customer-capture-rate** — not revenue/txn only. *(Lightspeed's Customer Capture Rate is jewelry-critical.)*
- **"Multiple Sales Exclude"** class-exclusion control so UPT/multi-sale isn't inflated by cheap add-ons (polishing cloth). *(RICS metric-purity feature.)*

### B9. Velocity & inventory-velocity analytics in-SPA — *beats RICS*
- **Slow-mover vs fast-mover panel:** days-since-last-sale, sell-through %, days-of-inventory-remaining — surfaced in-SPA, not iframe-embedded. *(Gap: "fast/slow reports exist but orphaned.")*
- **Price-Point Summary** (sales distribution by price band), **Grid (Col×Row) matrix** (karat × style, gem-type × setting) with per-cell sell-through & % of total. *(RICS grid pattern.)*
- **Tri-mode valuation toggle** (Active Selling Price / Avg weighted Cost / Current Cost) and **ROI/Turns/Sell-Thru %** as sort keys. *(RICS.)*

### B10. Insight-to-action loop — *beats Lightspeed PO-from-report*
- From a slow-mover / stockout / margin insight, **one-click action** without leaving the screen: create PO, adjust price, transfer stock between stores, flag for AIMS markdown. *(Lightspeed pattern.)*

### B11. Saved + scheduled reports & push — *beats RICS + Lightspeed*
- Save report specs; schedule daily/weekly/monthly email to stakeholders; **extend to Slack/WhatsApp push for owners**. *(RICS "Automated Reports, Delivered Your Way.")*

### B12. Sales anomaly detection — *closes Zevar gap*
- Unusual volume drops, zero-sale hours during open sessions, AOV spikes/drops, refund clusters, discount-rate spikes — mirroring the repair anomaly engine that already exists but is repair-only. *(Gap: "live_monitor.py anomaly is repair-only.")*

---

## (C) Information Architecture — Screens, Layout, Role Variants

### C1. One module, one route, three role-aware shells

**Route:** `/reports/dashboards/sales-monitor` → `SalesMonitor.vue` (new), registered in `router.js` with `meta: { requiresAuth: true, permission: 'sales.view' }`. Mounted inside the `ReportsHub` SPA shell (no full-page reload — platform §4.1 fix). The 4 fragmented live screens (`Revenue.vue`, `RevenueTab.vue`, `AdminMonitor.vue` sales tab, iframe `ReportViewer.vue` for the Sales group) are **merged into role-scoped views of this one module**.

### C2. Role-aware rendering

| Role | Default view | Sees |
|---|---|---|
| **Owner / System Manager / Accounts Manager** | **Multi-store Owner Wall** | All stores, store-vs-store, channel mix, full leaderboard, 20/80, targets wall, scheduled-report admin |
| **Store Manager / Sales Manager** | **Single-store Manager View** | Their store(s) only; pacing gauge, leaderboard, conversion funnel, anomaly ticker, hourly heatmap |
| **Sales User / Associate (self)** | **Associate Personal View** | Own rows only — personal KPIs vs own target, own UPT/conversion, own recent sales; **never** sees peer rows, store totals, or other associates' conversion (privacy §I). Rendered by `EmployeeLiveMonitor` content scoped to `user=`. |

> **TV/Kiosk mode:** Owner/Manager wall has a `?tv=1` query flag that hides nav, chrome, and hover controls, auto-cycles KPI tiles every 12s, and reads `sales_tick` for live update — mounts on a wall display behind the counter. Associate self-view never enters TV mode.

### C3. Screen layout (Owner Wall)

```
┌───────────────────────────────────────────────────────────────────┐
│ Sales Monitor          [TimeStore: today|7d|30d|90d|ytd|qtd][⚙cmp] │  ← global time + compare
│ [Store: All▾][Channel: All▾][Filter: ▾][Save][Schedule][Export]    │  ← shared filter bar
├───────────────────────────────────────────────────────────────────┤
│ ┌KPI┐ ┌KPI┐ ┌KPI┐ ┌KPI┐ ┌KPI┐ ┌KPI┐ ┌KPI┐ ┌KPI┐                     │  ← 8 KpiCards w/ ▲▼ + sparkline
│ │Rev│ │Txn│ │AOV│ │UPT│ │Unit│ │Conv│ │Refnd│ │Margin│             │
│ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └────┘                    │
├───────────────────────────────────────┬────────────────────────────┤
│  TrendLineChart (metric▾, day/week/mo)│  Pacing-to-Target Gauge     │
│  prior-period + YoY/WoW overlay       │  projected-day-close ▶      │
├───────────────────────────────────────┼────────────────────────────┤
│  Hourly Bar (full 24h, zero-bucketed) │  Conversion Funnel          │
│  + traffic overlay line               │  footfall→greeted→try-on→buy │
├───────────────────────────────────────┴────────────────────────────┤
│  Conversion Heatmap (DOW × hour)        │  Channel Mix Donut         │
├────────────────────────────────────────┴────────────────────────────┤
│  Salesperson Leaderboard (Rev|UPT|Conv|Attach|Margin|Capture, sort) │  ← multi-column, drill-through
├─────────────────────────────────────────────────────────────────────┤
│  Velocity Panel: Fast vs Slow movers (sell-thru, days-since, DII)   │
│  + 20/80 customer & vendor concentration                            │
├─────────────────────────────────────────────────────────────────────┤
│  Report Builder (collapsed): Metric × Dimension × Filter ▶ Run       │  ← RICS grammar
└─────────────────────────────────────────────────────────────────────┘
```

### C4. Drill-through contract (the unifying UX rule)
Every visualization is clickable → **transaction-level detail** in a side drawer, filtered to the same criteria + the clicked cell. Click an hour bar → that hour's invoices. Click a leaderboard row → that associate's sales (manager/owner only) or Profit Intelligence invoice-margin view. This kills the iframe disconnection the audit flagged.

### C5. Components (all in `frontend/zevar_ui/src/components/`, consume shared primitives)

| Component | Reuses platform primitive |
|---|---|
| `SalesMonitor.vue` | shell, `timeStore`, `useDashboardData`, `useRealtime(sales_tick)` |
| `KpiCard` strip | existing `KPICard.vue` + `KpiSparkline.vue` |
| Trend panel | `TrendLineChart.vue` |
| Hourly | `HourlyBarChart.vue` (traffic overlay) |
| Funnel | `ConversionFunnel.vue` |
| Heatmap | `MarginHeatmap.vue` (repurposed DOW×hour) |
| Channel/category/metal | `CategoryDonut.vue` |
| Leaderboard | new `AssociateLeaderboard.vue` |
| Velocity | new `VelocityPanel.vue` |
| Report builder | new `components/reports/ReportBuilder.vue` |

---

## (D) Data Model — New / Changed / Reused

### D1. NEW doctypes / tables (all under `…/unified_retail_management_system/doctype/`)

#### `daily_store_sales_rollup` (materialized — the performance spine)
| Column | Type | Notes |
|---|---|---|
| `date` | Date | PK part |
| `store` | varchar(20) | PK part (warehouse) |
| `salesperson` | varchar(140) | PK part (employee id; `__none__` if unattributed) |
| `channel` | varchar(20) | PK part — `in_store/online/phone/b2b/memo` |
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

PK `(date, store, salesperson, channel, category, metal)`. Indexes `(store,date)`, `(date)`, `(salesperson,date)`. Refreshed by `sales_monitor.rebuild_rollup(invoice)` on submit/cancel + nightly `*/30 0 * * *`.

#### `store_traffic_log` (foot-traffic fact — unblocks conversion)
| Field | Type | Notes |
|---|---|---|
| `date` | Date | PK part |
| `store` | Link→Warehouse | PK part |
| `hour` | Int (0-23) | PK part |
| `visitors_in` | Int | people-counter or manual |
| `visitors_out` | Int | optional |
| `source` | Select (`people_counter`/`manual_pos`/`door_sensor`) | |
| `device_id` | Data | hardware_bridge ref |
| `entered_by` | Link→User | manual attribution |
| `notes` | Small Text | |

#### `sales_target` (store-level, distinct from employee Performance Target)
| Field | Type | Notes |
|---|---|---|
| `store` | Link→Warehouse | PK part |
| `period_type` | Select (Daily/Weekly/Monthly) | PK part |
| `period_start` | Date | PK part |
| `period_end` | Date | |
| `target_revenue` | Currency | |
| `target_units` | Int | |
| `target_upt` | Decimal | |
| `target_conversion` | Decimal | |
| `channel_targets` | Table (child) | per-channel revenue target |

#### `saved_report` (report-builder presets + schedule)
| Field | Type | Notes |
|---|---|---|
| `name` | Data | user-given |
| `owner` | Link→User | |
| `module` | Select (Sales/Profit/Workforce/Live) | |
| `report_spec` | JSON | the ReportSpec (§F) |
| `schedule_cron` | Data | optional |
| `deliver_to` | Table (child) | User + channel (email/slack/whatsapp) |
| `last_run` | datetime | |

### D2. CHANGED — custom field added to `Sales Invoice`
- **`Sales Invoice.custom_sales_channel`** — Select: `In-Store POS / Online / Phone / B2B / Memo-Consignment`. Set on the POS path (`api/pos.py`) and exposed as a first-class report dimension. Flows into `daily_store_sales_rollup.channel`. *(Confirmed absent today.)*

### D3. REUSED — do not rebuild (Frappe/ERPNext native)
| Doctype | Use for |
|---|---|
| **Sales Invoice** (+ Item, Payment) | primary sales fact |
| **Sales Commission Split** | the *only* reliable salesperson attribution (owner is unreliable) |
| **POS Opening/Closing Entry** | session windows, float, cash reconciliation |
| **Performance Log / Performance Target** | workforce canonical revenue source (platform §2.4) — `sales_monitor.get_leaderboard` reads Performance Log for revenue/employee |
| **sale_cost_breakdown** | cogs/gross_profit source for the leaderboard margin column (after platform wires the `on_submit` hook, B1) |
| **Employee / User** | associate identity + role scoping |
| **Warehouse** | store dimension |
| **Item** (+ `custom_jewelry_type`, `custom_metal`, `custom_purity`) | category/metal dimensions |
| **Customer** | 20/80 attribution + customer-capture-rate |

### D4. People-counter adapter (new file)
`zevar_core/integrations/hardware/people_counter.py` — invoked via existing `scripts/hardware_bridge.py`. Interface: `fetch_traffic(device_id, since) -> list[{ts, in, out}]`. v1: supported counter device + **manual POS staff entry on session open/close** (the pragmatic fallback the audit calls the #1 blocker).

---

## (E) API Surface (all whitelisted, role-gated, read rollup first)

All under `zevar_core/api/sales_monitor.py` (new — the sole sales-aggregation service).

| Endpoint | Method | Purpose | Reads |
|---|---|---|---|
| `sales_monitor.get_summary` | GET | revenue, txn_count, AOV, UPT, units, refund_count, refund_value, run_rate, projected_day_close, vs_prior, vs_yoy | `daily_store_sales_rollup` |
| `sales_monitor.get_hourly` | GET | hour-of-day (full 24h, **zero-bucketed**) + traffic overlay | rollup + `store_traffic_log` |
| `sales_monitor.get_trend` | GET | multi-series (current/prior/YoY/WoW) for a metric × granularity | rollup |
| `sales_monitor.get_breakdown` | GET | by category/metal/purity/salesperson/channel/SKU/customer | rollup |
| `sales_monitor.get_leaderboard` | GET | per-associate revenue, UPT, conversion, attach, margin, capture | rollup + Performance Log + SCB |
| `sales_monitor.get_pace` | GET | vs `Sales Target`, projected-close, attainment % | rollup + `sales_target` |
| `sales_monitor.get_conversion` | GET | funnel stages + DOW×hour conversion heatmap | `store_traffic_log` + rollup |
| `sales_monitor.get_velocity` | GET | fast/slow movers, sell-thru, days-since-last-sale, DII | rollup + `tabBin`/Item |
| `sales_monitor.get_concentration` | GET | 20/80 customer + vendor concentration | rollup + Customer |
| `sales_monitor.run_query` | POST | generic report-builder engine | rollup (grammar §F) |
| `sales_monitor.rebuild_rollup` | (internal) | upsert affected rows on invoice submit/cancel | invoice |
| `sales_monitor.save_report` / `list_reports` / `run_saved_report` | POST/GET | saved-report CRUD | `saved_report` |
| `sales_monitor.schedule_report` | POST | attach cron + delivery channel | `saved_report` |

**Refactor targets (delegate to `sales_monitor` — kill the drift):**
`revenue_dashboard.get_dashboard_data`, `revenue_dashboard.get_today_summary/get_hourly_distribution/get_category_breakdown/get_top_salespersons`, `reports._eod_revenue` + `_brief_sales`, `analytics_hub.get_hub_data` sales hero + `get_daily_revenue_breakdown`, `sales_history.get_sales_summary`. These become thin callers or are deleted.

**Deleted/replaced:** the iframe-embedded native reports (`hourly_sales`, `sales_by_salesperson`, `top_selling_jewelry`) for the Sales group are replaced by in-SPA components; the catalog stubs (`Store Scorecard`, `High Value Sales`) that have no backing report definition are implemented here or removed.

---

## (F) Realtime & KPI Wiring (per shared platform)

### F1. Channels consumed/produced

| Channel | Direction | Use |
|---|---|---|
| `sales_tick` | **produced** (via platform `bus.publish` in `realtime.hooks.on_invoice_submit/on_cancel` and `on_gold_purchase_submit`) → drives Live Monitor's live tile | after `rebuild_rollup` |
| `sales_tick` | **consumed** by `useRealtime` in `SalesMonitor.vue` → live-refresh the KPI strip + pacing gauge without re-fetch | rooms `admin_wall` + `store_<wh>` |
| `anomaly_alert` | **consumed** → anomaly ticker (volume drop, zero-sale hour, AOV spike, refund cluster, discount spike) | room `admin_wall` |
| `price_shock` | **consumed** → margin-at-risk badge on the KPI strip when metal-rate Δ exceeds threshold | room `admin_wall` |
| `associate_personal` | **consumed (associate view only)** → personal KPI live-refresh; scoped to `user=<employee_user_id>` — never global | user-scoped |

### F2. Rollup tables this module reads
`daily_store_sales_rollup` (primary), `employee_period_rollup` (leaderboard revenue/upt via Workforce canonical path), `store_traffic_log` (conversion), `metal_rate_history` (margin-at-risk + gold pass-through), `sales_target` (pacing).

### F3. Refresh trigger flow
`Sales Invoice on_submit` → `realtime.hooks.on_invoice_submit` → (1) `sales_monitor.rebuild_rollup(invoice)` upsert, (2) platform `profit_math.compute_invoice_margin` persists SCB (B1), (3) `bus.publish("sales_tick", "sale.completed", SaleCompletedData(...))` with `employees=[...]` for personal fan-out. `on_cancel` reverses the upsert + deletes SCB row + publishes `sale.cancelled`.

### F4. Report-builder grammar (single cross-module contract)
```ts
interface ReportSpec {
  metrics: Metric[];      // revenue, txn_count, aov, upt, units, gross_profit, margin_pct, conversion, sell_thru, roi, turns
  dimensions: Dimension[];// store, salesperson, category, metal, purity, gem, channel, sku, customer, hour, dow, day, week, month
  filters: FilterGroup;   // By Store|Salesperson|Category|Metal|Gem|Channel|SKU|Customer|Period; per-field Exclude; multi-select = comma; same-type=OR, diff-type=AND
  period: PeriodSpec;     // from timeStore
  order_by: { metric, dir };
  compare: 'none'|'prior_period'|'yoy'|'wow';
}
```
Same `ReportSpec` + `FilterGroup` object is shared with Profit, Workforce, Live (a filter set in Sales Monitor carries into a Profit drill-down).

---

## (G) KPI Table — Precise Formulas

| KPI | Formula | Source |
|---|---|---|
| **Gross Revenue** | `SUM(Sales Invoice.grand_total) WHERE docstatus=1` (excl. returns) | rollup |
| **Net Revenue** | `SUM(net_total)` | rollup |
| **Transaction Count (Txn)** | `COUNT(DISTINCT Sales Invoice.name) WHERE is_return=0` | rollup.invoice_count |
| **AOV / Avg Ticket** | `Gross Revenue / Txn Count` | derived |
| **Units Sold** | `SUM(Sales Invoice Item.qty)` | rollup.unit_count |
| **UPT (Units per Transaction)** | `SUM(qty) / COUNT(DISTINCT invoice)` (with Multiple-Sales-Exclude class filter available) | rollup |
| **IPT (Items per Transaction)** | `COUNT(DISTINCT line items) / COUNT(DISTINCT invoice)` | rollup |
| **Attach Rate** | `Txn with ≥2 line items / Total Txn` | rollup |
| **Basket Depth** | `SUM(qty) / Txn` (= UPT; distinct when line-items vs units differ) | rollup |
| **Refund/Void Rate** | `refund_count / (invoice_count + refund_count)` | rollup |
| **Refund Value** | `SUM(grand_total) WHERE is_return=1` | rollup |
| **Discount Value / Rate** | `SUM(discount_amount)` ; `discount_value / gross_revenue` | rollup |
| **Conversion Rate** | `Txn Count / SUM(store_traffic_log.visitors_in)` (same store+hour+day) | traffic + rollup |
| **Customer Capture Rate** | `COUNT(DISTINCT new customers in period) / Total visitors_in` (Lightspeed jewelry-critical CRM KPI) | traffic + Customer |
| **Run Rate (per-hour)** | `Net Revenue so far today / hours_elapsed_since_store_open` | rollup |
| **Projected Day-Close** | `Run Rate × total_open_hours` (or weighted by hourly distribution) | rollup |
| **Pacing / Attainment %** | `Actual-to-date / (target_revenue × elapsed_fraction_of_period)` | rollup + `sales_target` |
| **Sell-Through %** | `Units Sold / (Units Sold + On-hand inventory)` | rollup + `tabBin` |
| **Days-of-Inventory-Remaining (DII)** | `On-hand units / (Units Sold / days_in_period) × days_in_period` | rollup + Bin |
| **Days-Since-Last-Sale** | `TODAY - MAX(posting_date) per SKU` | rollup |
| **ROI (Gross Profit $ per $ invested)** | `gross_profit / avg_inventory_at_cost` | SCB + Bin |
| **Turns** | `COGS / avg_inventory_at_cost` | SCB + Bin |
| **Gross Margin %** | `gross_profit / net_revenue` (single definition via `profit_math` / SCB) | SCB |
| **Gold Pass-Through %** | `metal_cogs / net_revenue` | SCB |
| **20/80 Customer Concentration** | Pareto: rank customers by revenue, find % accounting for 80% | rollup |
| **Channel Mix %** | `channel_revenue / total_revenue` | rollup |

---

## (H) UX Patterns Worth Copying (cited)

| Pattern | Source | How used |
|---|---|---|
| Parametric report model: Metrics × Dimensions × Filters × Period, shared filter grammar, per-field Exclude, same-type=OR/diff-type=AND | **RICS** (RICS>Retail Report Creator) | ReportBuilder.vue — one grammar across all 4 modules |
| One-tap multi-store control (Separate/Combine/Compare/Store Summary) on every report | **RICS** | store control chip on every panel |
| Conversion as headline KPI, traffic-vs-sales by time-of-day × day-of-week heatmap | **The Edge + TraxSales** | ConversionFunnel + DOW×hour heatmap |
| "Manage your unsold customers" — traffic that didn't convert | **TraxSales** | Funnel drop-off stage + conversion tile |
| 20/80 customer & vendor concentration auto-surfaced | **The Edge** | Concentration panel |
| Per-employee Customer Capture Rate as a leaderboard column | **Lightspeed** | AssociateLeaderboard |
| PO-from-report one-click insight-to-action | **Lightspeed** | VelocityPanel action buttons |
| In-place "Measure" swap + period-over-period ▲/▼ + inline pivot | **Shopify / Lightspeed** | KPI cards + TrendLineChart |
| Tri-mode valuation (Active Selling Price / Avg Cost / Current Cost), ROI/Turns/Sell-Thru sort keys | **RICS** | VelocityPanel + ReportBuilder metrics |
| Grid (Col×Row) attribute matrix with per-cell sell-through | **RICS** | karat×style, gem×setting matrix |
| Saved + scheduled reports delivered "your way" (email + push) | **RICS + Lightspeed** | saved_report + Slack/WhatsApp for owners |
| Multiple Sales Exclude (class exclusion to keep UPT pure) | **RICS** | ReportBuilder metric-purity filter |

---

## (I) Permissions & Privacy (esp. associate-data isolation)

**Single permission helper:** `utils/permissions.js` is the sole source (platform §5). Router meta uses **permission keys**, not role lists.

| Surface | Helper | Backend `only_for` (reconciled) |
|---|---|---|
| Sales Monitor (owner wall) | `canAccessSalesPerformance()` | System Manager, Administrator, Store Manager, Sales Manager, Accounts Manager |
| Sales Monitor (manager view) | `canAccessSalesPerformance()` | Store Manager, Sales Manager (own store scoping via `_owner_clause`) |
| Associate self view | `isOwnSalesOnly()` | Employee, Employee Self Service, Sales User |

**Iron privacy rules (enforced in `sales_monitor.py` `only_for`):**
1. **Associate self-view NEVER sees peer rows.** Leaderboard/breakdown endpoints return only `WHERE salesperson = current_employee` when role is associate. Backend-enforced — frontend hiding alone is insufficient.
2. **Personal-channel events use `user=`, never global.** `sales_tick` fan-out to associates goes through `associate_personal` with `user=<employee_user_id>` (platform §1.2 iron rule).
3. **Margin/financial sections** (gross_profit, margin %, ROI) masked to `ACCOUNTING_ROLES / ADMIN_ROLES` only — reuse the existing `_eod_owner_clause` + accounting-role masking pattern from `reports.py`.
4. **Customer names in 20/80 / transaction drill-through** masked for associate role (customer privacy).
5. **Store scoping:** non-managers see only their store via `cost_center`/Warehouse filter; manager sees assigned stores only.

---

## (J) Integration with the Other 3 Modules + Native Stack

**With Live Monitor (Command Center):**
- Produces `sales_tick` events Live Monitor consumes for the live sales tile.
- Shares `daily_store_sales_rollup` so Live's `get_summary` is instant.
- Sales anomaly rules feed `anomaly_alert` → Live's ticker.

**With Profit Intelligence:**
- Leaderboard margin column reads SCB rows (Sales Monitor's `on_submit` hook persists them via `profit_math`).
- Drill-through from a leaderboard row → Profit Intelligence invoice-margin view (same ReportSpec filters carry over).
- Shares `metal_rate_history` for margin-at-risk (`price_shock`) badge.

**With Workforce Intelligence:**
- Leaderboard reads `employee_period_rollup` (Workforce canonical revenue path) so sales-revenue and workforce-revenue never diverge.
- UPT/conversion/attach columns are Workforce scorecard inputs.
- Shares the `salesperson` dimension + Performance Log attribution.

**With native Frappe stack (leverage, don't rebuild):**
- **Frappe Insights Query v3 / Dashboard v3 / Alert** — zero-code owner BI for ad-hoc deep analysis and scheduled email/Telegram alerts. Sales Monitor SPA owns realtime + role-aware wall; Insights owns deep no-code BI. No duplication.
- **ERPNext `sales_person_target_variance_based_on_item_group`** — mirror its variance engine in `sales_monitor.get_pace` for store-level.
- **ERPNext `customer_acquisition_and_loyalty`** — source for Customer Capture Rate.
- **Number Card / Dashboard Chart / Workspace** — glance tiles on the owner landing Workspace; deep analytics live in the SPA.
- **Native Frappe reports** (`sales_analytics`, `sales_invoice_trends`, `gross_profit`) — reference/aggregation only; not the primary surface.

---

## (K) Phased Build (within this module)

> **Dependency:** Phase P0 of the **Shared Platform** (§11.1: `profit_math`, wire SCB hook + `log_sale_event`, rollup tables, `bus.py`, event schema, `useRealtime`/`useDashboardData`/`usePolling`, `utils/format.js`, `timeStore`, SPA router-view fix, single permission model) **must land first**. The tasks below assume that spine exists.

### P0 — Must (the module becomes real and beats today's fragmentation)

| # | Task | Owner | Deliverable |
|---|---|---|---|
| P0.1 | Create `zevar_core/api/sales_monitor.py` with `get_summary`, `get_hourly` (24h zero-bucketed), `get_breakdown`, `get_leaderboard`, `get_pace`, `rebuild_rollup` | Backend | sole sales-KPI service |
| P0.2 | Create `daily_store_sales_rollup` table + `rebuild_rollup(invoice)` upsert on submit/cancel + nightly `*/30 0 * * *` safety rebuild | Backend | sub-100ms reads |
| P0.3 | Refactor `revenue_dashboard.py`, `reports._eod_revenue`, `analytics_hub` sales hero, `sales_history.get_sales_summary` to **delegate** to `sales_monitor`; delete duplicate SQL | Backend | kills 5-way drift |
| P0.4 | Add `Sales Invoice.custom_sales_channel`; set on POS path; flow into rollup.channel | Backend | channel dimension |
| P0.5 | Create `SalesMonitor.vue` shell + route `/reports/dashboards/sales-monitor` (`meta.permission='sales.view'`); merge `Revenue.vue` + AdminMonitor sales tab; mount in ReportsHub SPA (delete `window.location.href`) | Frontend | one module, no reload |
| P0.6 | KPI strip: 8 `KPICard`s (Rev, Txn, AOV, **UPT**, Units, Refund, Margin, Run-rate/Projected-close) with ▲▼ + sparkline; all consume `timeStore` + `useDashboardData` | Frontend | first time UPT/run-rate exist |
| P0.7 | `TrendLineChart` panel with day/week/month granularity + prior-period/YoY/WoW overlay; global time-range store wired | Frontend | first real multi-day trend |
| P0.8 | Hourly bar (full 24h, zero-bucketed) replacing the hardcoded 9am-8pm window | Frontend | fixes lossy window |
| P0.9 | `useRealtime('sales_tick')` live-refresh of KPI strip + pacing gauge; backfill on tab-visible | Frontend | realtime sales |
| P0.10 | Role-aware rendering (owner wall / manager / associate self) with backend `only_for` enforcing associate isolation | Full-stack | privacy correct |

### P1 — Should (the differentiators that beat single competitors)

| # | Task | Deliverable |
|---|---|---|
| P1.1 | `store_traffic_log` doctype + manual POS-staff entry on session open/close + `people_counter.py` adapter interface | conversion unblocked |
| P1.2 | `get_conversion` + `ConversionFunnel.vue` (footfall→greeted→try-on→buy) + DOW×hour conversion heatmap | headline conversion KPI |
| P1.3 | `sales_target` doctype + `get_pace` pacing-to-target gauge + projected-day-close | Toast/Lightspeed pacing |
| P1.4 | `AssociateLeaderboard.vue` with Rev+UPT+Conv+Attach+Margin+Capture columns; drill-through drawer; Multiple-Sales-Exclude | complete leaderboard |
| P1.5 | Multi-store one-tap control (Separate/Combine/Compare/Summary) on every panel | RICS table-stakes |
| P1.6 | Channel-mix donut + channel comparison panel | first-class channel |
| P1.7 | `ReportBuilder.vue` + `sales_monitor.run_query` with shared filter grammar; in-place Measure swap + ▲▼ + inline pivot | RICS grammar |
| P1.8 | `get_concentration` + 20/80 customer & vendor panel; Price-Point Summary (sales by price band) | The Edge insights |
| P1.9 | `saved_report` CRUD + email schedule | RICS "delivered your way" |
| P1.10 | Sales anomaly rules (volume drop, zero-sale open hour, AOV spike, refund cluster, discount spike) → `anomaly_alert` | closes repair-only gap |

### P2 — Nice (polish that makes it the leading product)

| # | Task | Deliverable |
|---|---|---|
| P2.1 | `VelocityPanel.vue` (fast/slow movers, sell-thru, DII, days-since) + Grid Col×Row matrix (karat×style, gem×setting) | RICS velocity + grid |
| P2.2 | Tri-mode valuation toggle + ROI/Turns/Sell-Thru sort keys | RICS valuation |
| P2.3 | Insight-to-action buttons (create PO, adjust price, transfer stock, AIMS markdown) from velocity/stockout insights | Lightspeed loop |
| P2.4 | People-counter device integration (replace manual entry) | TraxSales-grade |
| P2.5 | Slack/WhatsApp push for owners on saved-report schedule | RICS extended |
| P2.6 | TV/Kiosk mode (`?tv=1`) for the owner/manager wall | wall display |
| P2.7 | Basket affinity analysis (items sold together) | basket depth+ |

---

## (L) Success Metrics / Acceptance Criteria (proving best-in-class)

**Performance**
- Every `sales_monitor.*` endpoint returns **< 100ms p95** at 5 stores × 3 years of data (rollup reads only).
- EOD closeout query count drops from **15+ raw queries to ≤ 3** (rollup-backed).
- KPI strip live-updates on `sales_tick` **< 1s** after invoice submit (no full re-fetch).

**Correctness (the drift bug is dead)**
- **Single-definition guarantee:** `grep` for sales-total computation outside `sales_monitor.py` + SCB returns **0** business-logic hits (only delegation calls). Revenue.vue, EOD revenue, analytics hero, sales_history all show the **same** today's-total for a given store/period.
- `gross_margin_pct` means exactly one thing (via `profit_math` / SCB) across leaderboard, trend, and Profit drill-through.

**Capability coverage (vs Best-in-Class target list)**
- Conversion Rate exists and is non-null whenever `store_traffic_log` has data for the period.
- UPT, attach rate, run-rate, projected-day-close computed and displayed (data already existed — now surfaced).
- Multi-granularity trend (hour→year) with prior-period + YoY/WoW overlay selectable.
- Channel comparison operational end-to-end (POS sets channel → rollup → donut + comparison).
- Store-vs-store control available on every panel.
- ReportBuilder produces a valid result for every Metric × Dimension × Filter combination in the grammar.
- Salesperson leaderboard shows all 6 ranking columns (Rev/UPT/Conv/Attach/Margin/Capture).

**Privacy (non-negotiable)**
- Automated test: an associate-role API call to `get_leaderboard` / `get_breakdown` returns **only their own rows**; peer revenue/margin never appears.
- Personal-channel events carry `user=` scope; no employee-attributed event is broadcast globally (verified by event-bus unit test).

**UX**
- Switching from Sales Monitor to any other dashboard (and back) **does not full-page reload** (`window.location.href` count in ReportsHub = 0).
- Every visualization drill-throughs to a transaction drawer filtered to the clicked cell (no iframe disconnect).
- Period-over-period ▲▼ arrows render on every KPI tile; in-place Measure swap works without re-run.

**Integration**
- Workforce Intelligence `get_team_performance` revenue figure **equals** Sales Monitor leaderboard revenue for the same employee/period (both read `employee_period_rollup`).
- Live Monitor's live sales tile **equals** Sales Monitor `get_summary(today)` at the same instant.

---

### Key file-path index (all absolute)

- **New backend service:** `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/sales_monitor.py`
- **People-counter adapter:** `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/integrations/hardware/people_counter.py`
- **New doctypes:** `daily_store_sales_rollup`, `store_traffic_log`, `sales_target`, `saved_report` under `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/unified_retail_management_system/doctype/`
- **Custom field:** `Sales Invoice.custom_sales_channel` (via Fixtures/custom field JSON)
- **Refactor (delegate to sales_monitor):** `…/api/revenue_dashboard.py`, `…/api/reports.py` (`_eod_revenue`, `_brief_sales`), `…/api/analytics_hub.py` (sales hero, `get_daily_revenue_breakdown`), `…/api/sales_history.py` (`get_sales_summary`)
- **New frontend:** `frontend/zevar_ui/src/pages/dashboards/SalesMonitor.vue`, `…/src/components/AssociateLeaderboard.vue`, `…/src/components/VelocityPanel.vue`, `…/src/components/reports/ReportBuilder.vue`
- **Shared (platform, consumed):** `…/src/composables/{useRealtime.js,useDashboardData.js}`, `…/src/stores/time.js`, `…/src/utils/format.js`, `…/src/utils/permissions.js`, `…/src/components/charts/*`
- **Route:** add `/reports/dashboards/sales-monitor` (`meta.permission='sales.view'`) in `frontend/zevar_ui/src/router.js`; delete the `Revenue.vue` / `AdminMonitor.vue` sales-tab routes and the iframe `ReportViewer.vue` Sales group.
