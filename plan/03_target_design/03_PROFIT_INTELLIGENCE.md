# Profit Intelligence — Best-in-Class Target Design

> **Lead Designer:** Profit Intelligence module. Grounded in direct code reads (SCB doctype schema, `hooks.py:65-79`, `profit_intelligence.py` function map, `commission.py:104-109`, `pricing_tools.py:210`, `analytics_hub.py:1012`, `finance.py:351`, `services/` dir confirmed present). The corrected audit (`CURRENT_STATE_AUDIT.md` § Profit Intelligence + Margin Math Integrity) is treated as authoritative; the stale `module_audit_raw.json` is explicitly ignored per the audit.

---

## (A) Module Vision & Role in the Suite

**One-line thesis:** Profit Intelligence is the module that makes Zevar the only jewelry POS where every "margin %" the owner, the CPA, the commission engine, and the AI-pricing agent see is **the same number**, decomposed all the way to net pocket margin, and where the owner can *simulate before acting*.

**Role in the suite of four:**
- **Live Monitor (Command Center)** pushes a live "margin-at-risk" tile and a `price_shock` alert to the wall when gold moves; Profit Intelligence is the *producer* of that signal.
- **Sales Monitor** owns volume/revenue/traffic KPIs; Profit Intelligence owns *what those sales earned*. They share the report-builder grammar, the `timeStore`, and the `daily_store_sales_rollup` — but Profit Intelligence is the only module that reads the 6-bucket SCB spine.
- **Workforce Intelligence** pays commissions; Profit Intelligence is the *sole source of the margin number commissions are computed on* (kills the B3 commission-on-inflated-margin bug). Compensation flows into Salary Slips only after `profit_math` runs.

**The moat (per `wf1_consolidated.md` differentiation thesis):** No competitor combines (1) gold-rate-at-sale locking + per-karat mapping + 4C gemstone cost, (2) making/alloy/labor/payment-interchange/overhead decomposition persisted per-invoice, and (3) PVM/margin-waterfall/what-if — because Lightspeed/Shopify/RICS model COGS as a single flat number, The Edge has the depth but only as static desktop reports, and Pricefx/Vendavo have the exec views but not jewelry COGS. Zevar fuses both on one MariaDB model with zero ETL.

**Design principle (load-bearing):** there is exactly **one** margin function — `zevar_core/services/profit_math.py::compute_invoice_margin()`. Everything in this module, and everything in the other three that touches margin, calls it or reads a SCB row it produced. The word `gross_margin_pct` means one thing, everywhere, forever.

---

## (B) Target Feature Set (grouped; each mapped to the gap/competitor it beats)

### B1. Trust Spine — single, wired, accurate margin (P0)
| Feature | Beats | Closes gap |
|---|---|---|
| Wire `calculate_sale_cost_breakdown` to `on_submit` + add `on_cancel` cleanup + backfill bench command | The Edge (hooks are correct there); Zevar itself (audit's #1 issue: SCB never created) | Audit B1 — entire dashboard blank today |
| `profit_math.compute_invoice_margin()` single source; refactor `commission.py:104`, `top_profitability_by_product.py:70`, `analytics_hub._margin_pct:1012`, `pricing_tools.simulate:210`, `repair_accounting.py:704`, `gemstone_value_service.py:125`, `finance.py:351` | No competitor has *one* reconcilable margin; Zevar's own 7-way divergence is worse than any competitor's single (wrong) one | Audit B3 — commission pays on inflated margin |
| Per-invoice `calc_log` JSON exposed in UI + exportable | Luxare/PIRO auditability | Already designed, just not surfaced |
| Margin data-quality guardrail: flag zero/missing-cost rows, negative-margin sales | Lightspeed Margin Alert | Audit gap: no DQ guardrail |

### B2. Jewelry-Accurate COGS model (P1)
| Feature | Beats | Closes gap |
|---|---|---|
| `making_charge` (per-gram + per-piece) added to SCB + Item | Valigara/Jewel360 (have it); Lightspeed/Shopify (don't) | Largest jewelry-accuracy hole (10-30% of price) |
| `alloy_wastage_amount` (% applied to metal_cogs) | The Edge | Pure-metal COGS assumption |
| Apply unused `labor_burden_percent` + honor `Labor Cost Pool.allocation_method` | — | Dead-config tech debt |
| Gemstone costing mode: `cost` vs `replacement` (melee-parcel lot, FX, cert premium) | Valigara | Audit gap: static Item-master cost |
| Interchange-tier payment cost (Visa/MC/Amex/corporate) | Rare even in dedicated jewelry systems | Audit gap: one flat 2.9% |

### B3. Exec Views — what separates "reports" from "Profit Intelligence" (P1)
| Feature | Beats | Closes gap |
|---|---|---|
| **Margin Waterfall** (Revenue → metal → gems → making → labor → commission → payment → overhead → NET pocket margin), green=add / red=leak | Pricefx / Vendavo | Audit gap: stacked-bar only, no bridge |
| **PVM / Margin Bridge** (period-over-period Δ decomposed into price/volume/mix/new-discontinued/cost effect) | Vendavo Margin Bridge Analyzer | "THE killer exec view; no jewelry POS has it" |
| **What-If / Market Simulation** with sliders (gold rate, making %, discount, overhead) + elasticity-adjusted volume + revenue impact + **confidence band** + **price-range sweep / margin curve**; persists `What-if Simulation Run` for replay | Pricefx Market Simulation | Audit gap: simulator thinner than SCB → trust killer; fixes by calling `compute_invoice_margin` |
| **Gold pass-through %** (margin Δ attributable to gold moves) | The Edge Spot Metal + Jewel360 | Audit gap |
| **Unrealized gain/loss on inventory** (MTM: historical vs replacement) | Expected in a "Profit Intelligence" suite | Audit gap (out of COGS scope, in suite scope) |
| **Net/Contribution margin per SKU** (revenue − COGS − payment − commission − allocated overhead) | "No competitor exposes it well — Zevar's moat" | New `net_contribution_margin_pct` on SCB |

### B4. Overhead & Multi-Store (P1)
| Feature | Beats | Closes gap |
|---|---|---|
| Convert `Cost Center Allocation` singleton → **per-store** (or child table); add `store` to SCB | Any multi-store owner | Singleton structurally blocks multi-store profit |
| **Activity-Based Costing (ABC)** driver-based overhead (per-invoice, revenue-proportional, per-sqft, per-associate-hour, per-repair-bench-hour) as a 3rd method | — | Only 2 methods today |
| Multi-store profit consolidation view + `group_by='store'` | — | Audit gap |

### B5. Prescriptive Pricing (P2)
| Feature | Beats | Closes gap |
|---|---|---|
| **Floor-price / lowest-acceptable-price** shown in inventory + at POS; block-with-override or warn-with-reason, capture override reason | The Edge floor-price + Luxare rule-based minimum margin | Turns module descriptive → prescriptive |
| **AIMS aged-inventory margin-recovery engine**: monthly batch → Old-vs-New preview → tiered spiffs (bonus commission) AND markdowns → auto-generate staff spiff posters + in-case clearance signage | The Edge AIMS (category-unique) | Audit gap: flat 15% markdown only |
| **Markdown/slow-mover optimization** (aging buckets × velocity × sell-through target → clearance price maximizing recovered margin) | Increff/RELEX/Yieldigo | Audit gap: `Clearance` enum has no velocity math |
| **AI margin recommendations** grounded in RAG over store's own history (confidence_level + reasoning + rag_sources), wired to live events, Pricefx-Agents-style continuous monitors + approve→auto-apply workflow | Pricing Recommendation already has the bones | Audit gaps: generator unscheduled, `create_recommendation` 404, approve/reject casing, confidence string-vs-number |

---

## (C) Information Architecture — Screens, Layout, Role-Aware Variants

Single route under the unified shell: `/reports/dashboards/profit` → `ProfitIntelligence.vue` (rebuilt). SPA-routed (no `window.location.href`), consumes `timeStore`, renders a `<router-view>` for sub-tabs. Permission key `profit.view` (new). ECharts primitives throughout; the module owns the specialized **`WaterfallChart.vue`** and reuses `MarginHeatmap.vue`, `TrendLineChart.vue`, `KpiSparkline.vue`, `CategoryDonut.vue`.

### C1. Shared shell (every tab)
- Global time-range bar (`timeStore` presets) + the **shared filter grammar** (`ReportBuilder.vue` filter bar: By Store / Salesperson / Category / Metal / Gem / Channel / SKU / Customer + Exclude toggles + same-type=OR/different-type=AND).
- KPI strip: Gross Profit $, Gross Margin %, Net Contribution Margin %, Gold Pass-Through %, Aged-Inventory at Risk $ — each with `KpiSparkline` prior-period overlay and ▲/▼ delta vs prior period and YoY.

### C2. Tabs & widgets
| Tab | Widgets (top→bottom) |
|---|---|
| **Overview** | KPI strip → Margin Waterfall (full company, current period) → Profit Trend (`TrendLineChart`, gross vs net margin, prior + YoY overlay) → Cost-Component `CategoryDonut` (absolute/% toggle) → Gold Pass-Through strip + `metal_rate_history` sparkline |
| **Margin Analysis** | Margin Heatmap (Category × Metal, cell = avg `gross_margin_pct`, click → invoice list) → dimension selector (store/salesperson/category/metal/purity/channel/SKU/customer) → per-dimension margin table sortable by margin $/margin %/revenue/ROI/turns → per-invoice drill-down (`get_cost_breakdown_detail` + full `calc_log`) |
| **PVM Bridge** | Period-A vs Period-B selector → Price/Volume/Mix/New-Disc/Cost waterfall (the 5-effect bridge) → contribution table (% of Δ explained by each effect) → "unexplained residual" honesty row |
| **What-If Simulator** | Item/store/category picker → sliders (gold rate ±, making %, discount %, overhead $) → live `compute_invoice_margin` recompute → projected margin %, revenue impact (elasticity-adjusted volume), **confidence band**, **margin-vs-price curve** → "Save Simulation Run" → "Create Recommendation" (wired to real endpoint) |
| **Pricing Actions** | `PricingRecommendationsPanel` (rebuilt): cards with type/current vs recommended/Δ margin/**confidence_level label + bar**/**RAG sources + similar_events_count rendered** → Approve/Reject (case-insensitive) → Approve→auto-apply writes `custom_msrp` + secondary-confirm audit row → AIMS spiff/markdown batch runner → slow-mover list (`get_slow_moving_inventory`) → pricing action feed (`get_pricing_action_items`) |
| **Inventory MTM** | Gold held in stock valued at historical cost vs `metal_rate_history` replacement → unrealized gain/loss by store/category; aged-inventory margin-recovery preview |

### C3. Role-aware variants
| Role | Sees |
|---|---|
| **Owner / System Manager / Accounts Manager** | All tabs, all stores, full waterfall/PVM/simulator, recommendation approve→apply, AIMS runner, MTM, per-associate margin heatmap |
| **Store Manager** | All tabs **scoped to their store**; can view recommendations but approve→apply requires Accounts/Owner secondary confirm (fixes audit's "price-change power with no secondary approval" note) |
| **Associate** | **Denied** `profit.view` (cost/margin are owner-financial data). Routed to the Workforce self-view where they see their *commission tier* and *attainment*, never absolute margin $ or COGS. Enforced server-side via `only_for()` (see §I). |

### C4. TV / Kiosk mode
A read-only `/reports/dashboards/profit?mode=tv` variant for the owner's office screen: large-font KPI strip, auto-cycling slides (Overview → Waterfall → PVM → Gold exposure) on a 60s rotation with visible "last updated" + stale-data warning, sticky-pin during incidents. No filter editing. Same `useRealtime`/`useDashboardData` plumbing; subscribes to `price_shock` + `sales_tick` so the gold-exposure tile and margin-at-risk update live. Profit-specific TV signals: live gold spot + sparkline, margin-at-risk stress widget (gold value × ±2%/±5%), unrealized gain/loss ticker.

---

## (D) Data Model

### D1. New / changed doctypes
**Sale Cost Breakdown** (existing — extend). *Confirmed current fields via doctype JSON read.* Add:
| New field | Type | Purpose |
|---|---|---|
| `making_charge` | Currency | Jewelry-accuracy (B2) |
| `alloy_wastage_amount` | Currency | Jewelry-accuracy (B2) |
| `store` | Link → Warehouse | Multi-store (unblocks `group_by='store'`) |
| `item_group` | Link → Item Group | Category dimension beyond `jewelry_type` |
| `net_contribution_margin_pct` | Percent | revenue − 6 buckets − payment − overhead |
| `gemstone_costing_mode` | Select (Cost/Replacement) | (B2) |
| `payment_cost_detail` | (exists, JSON) | extend with interchange-tier breakdown |

Autoname `SCB-YY-MM-#####`, unique on `sales_invoice`, **unique on `(sales_invoice, store)`** after multi-store. Cancel handling: `on_cancel` sets SCB `docstatus=2` (never hard-delete, preserve audit).

**Cost Center Allocation** — convert singleton → **per-store** (one doc per Warehouse, or a `Warehouse Overhead` child table on the Warehouse doctype). Fields gain a `store` (Warehouse) dimension; new `overhead_allocation_method` value **`Activity Based (ABC)`** + child table `Overhead Driver` (pool, driver_type, rate).

**Labor Cost Pool** — honor existing `allocation_method` (Per Hour/Per Sale/Per Repair/Salary Spread) in `profit_math`; apply `labor_burden_percent`.

**Pricing Recommendation** (existing — no schema change needed; fix the *wiring*): schedule `generate_pricing_recommendations`; add the missing `create_recommendation` whitelist; extend generator to write AIMS spiff + markdown rows and true velocity-based clearance pricing.

**NEW doctypes** (under `zevar_core/unified_retail_management_system/doctype/`):
| Doctype | Key fields | Purpose |
|---|---|---|
| `What-if Simulation Run` | `owner_user`, `scope_type` (item/category/store/all), `baseline_margin_pct`, `scenarios` (child: gold_rate, making_pct, discount_pct, overhead_$, elasticity, projected_margin, projected_revenue, confidence_low/high), `created_at`, `replay_token` | Replay/audit (Pricefx) |
| `Margin Floor Rule` | `store`, `category`, `metal`, `min_margin_pct`, `enforcement` (Block/Block-with-override/Warn), `override_reason_required` | Floor-price at POS (B5) |
| `Overhead Driver` (child) | `pool` (rent/utilities/.../marketing), `driver_type` (per_invoice/revenue_proportional/per_sqft/per_associate_hour/per_repair_bench_hour), `rate`, `driver_value` | ABC overhead (B4) |
| `Aged Inventory Recovery Run` | `run_date`, `store`, `aging_buckets` (JSON), `items_reviewed`, `markdowns_applied`, `spiffs_created`, `recovered_margin_projected`, `status` | AIMS engine (B5) |
| `Interchange Tier` | `card_brand`, `tier` (Regulated/Standard/Corporate), `rate_pct`, `flat`, `applies_to_channels` | Payment cost granularity (B2) |

### D2. Materialized tables (from shared platform §2.5)
| Table | Used by Profit for |
|---|---|
| `daily_store_sales_rollup` | sub-100ms margin-by-dimension reads (reads `cogs_total`, `gross_profit`, `gold_rate_avg` columns — these come *from SCB*) |
| `metal_rate_history` | gold pass-through %, what-if backtesting, MTM unrealized gain/loss, `price_shock` threshold detection |
| `live_event_log` | backfill of `price_shock` + `sales_tick` into TV mode |

Refresh: invoice submit/cancel → `sales_monitor.rebuild_rollup` (which reads SCB) → `bus.publish("sales_tick")`. Metal rate fetch → append `metal_rate_history` → if `|delta_pct_1h| > threshold` → `bus.publish("price_shock")`.

### D3. Reuse, don't rebuild (Frappe / ERPNext / HRMS)
- **Frappe Insights Workbook** — owner's deep no-code margin ad-hoc analysis against the SCB table; zero backend code. Reserve custom API for realtime + the exec views only.
- **ERPNext `gross_profit` report** — reference only (it uses `valuation_rate`; do NOT point margin UI at it; keep SCB authoritative).
- **ERPNext `sales_person_target_variance_based_on_item_group`** — mirror its variance-decomposition *pattern* for the store-level PVM (not the math basis).
- **HRMS Salary Component / Additional Salary** — receives the commission computed on the *true* `profit_math` margin (Workforce disbursement path; Profit only *produces the number*).
- **`services/` package** — confirmed present (`gemstone_value_service.py`, `metal_rate_service.py`, etc.); `profit_math.py` lands here cleanly.

---

## (E) API Surface

All `@frappe.whitelist()`, all role-gated via `only_for()` per §I. All read from SCB / rollup tables; none recompute margin ad hoc except `profit_math`.

| Endpoint | Method | Purpose |
|---|---|---|
| `profit_intelligence.get_profit_summary` | POST | KPI strip: gross profit $/%, net contribution %, vs prior, vs YoY (reads rollup first, SCB fallback) |
| `profit_intelligence.get_margin_waterfall` **(new)** | POST | Full waterfall: revenue → each cost bucket → net pocket margin, for a scope/period |
| `profit_intelligence.get_pvm_bridge` **(new)** | POST | Period-A vs Period-B → {price_effect, volume_effect, mix_effect, new_disc_effect, cost_effect, residual} |
| `profit_intelligence.get_margin_analysis` | POST | Group-by margin table; **extend `group_by` to add `store`, `category`(item_group), `channel`, `sku`, `customer`** |
| `profit_intelligence.get_margin_heatmap` | POST | **Rewrite output to pivoted `{category, margins:{metal:{margin_pct, gross_profit, revenue, count}}}`** (fixes the shape mismatch — audit gap) |
| `profit_intelligence.get_cost_component_trends` | POST | Weekly/monthly trend per bucket |
| `profit_intelligence.get_cost_breakdown_detail` | POST | Per-invoice drill-down incl. full `calc_log` |
| `profit_intelligence.get_profit_trends` | POST | **Expose `quarterly` mode** (exists, not surfaced) |
| `profit_intelligence.get_gold_pass_through` **(new)** | POST | Margin Δ attributable to gold moves (from `metal_rate_history`) |
| `profit_intelligence.get_unrealized_gain_loss` **(new)** | POST | MTM: stock gold at historical cost vs replacement |
| `profit_intelligence.simulate_whatif` **(new, replaces ad-hoc)** | POST | Calls `compute_invoice_margin`; returns margin curve + confidence band; persists `What-if Simulation Run` |
| `profit_intelligence.create_recommendation` **(new — fixes 404)** | POST | Creates Pricing Recommendation from a Simulation Run |
| `profit_intelligence.get_recommendations` | POST | List (now includes numeric `confidence` mapped from `confidence_level`) |
| `profit_intelligence.review_recommendation` | POST | **Case-insensitive `action`** (fixes casing bug) + secondary-confirm when `apply` for Store Manager |
| `profit_intelligence.run_aged_recovery` **(new)** | POST | Trigger AIMS batch → `Aged Inventory Recovery Run` |
| `profit_math.compute_invoice_margin` | (internal) | The single margin function — `include_overhead`, `include_payment`, `include_labor` toggles |
| `profit_math.get_item_cogs` | (internal) | Per-item COGS dict (metal+gem+making+alloy+labor+commission-attrib+payment-attrib+overhead-attrib) |
| `profit_intelligence.calculate_sale_cost_breakdown` | (hook fn) | Wired to `on_submit` (after `commission.calculate_commissions`) + `on_cancel` |
| `profit_intelligence.backfill_scb` (bench) | CLI | `bench --site x zevar-backfill-scb` — populate SCB for historical invoices |
| `tasks.generate_pricing_recommendations` | (scheduled) | Add to `scheduler_events` (daily `7 2 * * *`) |

---

## (F) Realtime & KPI Wiring (per shared platform)

| Channel | Room/User scope | When Profit fires it | Consumer |
|---|---|---|---|
| `price_shock` | `room="admin_wall"` | `metal_rate_history` append where `|delta_pct_1h| > threshold` (default 3% — matches existing `get_pricing_action_items` rule) | TV margin-at-risk tile, Command Center alert |
| `sales_tick` | `room="admin_wall"` + `room="store_<wh>"` | invoice submit/cancel → `rebuild_rollup` → publish (produced by shared hooks, Profit *reads* it to refresh live margin tiles) | Overview live KPIs |
| `anomaly_alert` | `room="admin_wall"` | negative-margin sale, zero-cost sale, margin-floor breach-with-override (DQ guardrail) | Operations Alert ticker |

**Rollup tables read:** `daily_store_sales_rollup` (margin-by-dimension; columns `cogs_total`, `gross_profit`, `gold_rate_avg` populated from SCB at rollup time), `metal_rate_history` (pass-through + MTM + shock). **24h backfill** via `live_event_log` hydrates TV mode on open.

**Hook deltas in `hooks.py`:**
```python
doc_events["Sales Invoice"]["on_submit"].append("zevar_core.api.profit_intelligence.calculate_sale_cost_breakdown")  # AFTER commission.calculate_commissions
doc_events["Sales Invoice"]["on_cancel"].append("zevar_core.api.profit_intelligence.handle_invoice_cancel")
scheduler_events["cron"]["7 2 * * *"] = ["zevar_core.tasks.generate_pricing_recommendations"]
scheduler_events["cron"]["0 3 * * 0"] = ["zevar_core.tasks.run_aged_recovery_batch"]
```

Dead `publish_anomaly_alert`/`publish_employee_event` are deleted from `live_monitor.py` (shared platform B4); Profit's anomaly producers migrate to `bus.publish`.

---

## (G) KPI Table (precise formulas)

All read SCB (or the rollup fed by SCB). `qty` from Sales Invoice Item, `visitors_in` from `Store Traffic Log`.

| KPI | Formula | Source |
|---|---|---|
| Gross Profit $ | `SUM(scb.gross_profit)` | SCB |
| Gross Margin % | `SUM(scb.gross_profit) / SUM(scb.total_revenue) * 100` | SCB |
| Net Contribution Margin % | `SUM((scb.total_revenue − scb.total_cost − scb.total_payment_cost − scb.overhead_per_invoice)) / SUM(scb.total_revenue) * 100` (net_contribution_margin_pct field) | SCB (new field) |
| Metal COGS % | `SUM(scb.total_metal_cogs) / SUM(scb.total_revenue) * 100` | SCB |
| Making Charge % | `SUM(scb.making_charge) / SUM(scb.total_revenue) * 100` | SCB (new field) |
| Gold Pass-Through % | `(margin_current − margin_at_baseline_gold) / (gold_rate_current − gold_rate_baseline) * 100` — share of margin Δ explained by gold | SCB + `metal_rate_history` |
| Unrealized Gain/Loss $ | `SUM(item.net_weight_g × (metal_rate_history.rate_now − item.valuation_gold_rate))` for on-hand stock | Item + `metal_rate_history` |
| PVM — Price Effect | `Σ(qty_curr × (price_curr − price_base))` held at base volume | SCB pairs |
| PVM — Volume Effect | `Σ((qty_curr − qty_base) × price_base × margin_pct_base)` | SCB pairs |
| PVM — Mix Effect | `Σ(qty_curr × price_base × (margin_curr − margin_base))` − price effect | SCB pairs |
| PVM — Cost Effect | `Σ(qty_curr × (cogs_base − cogs_curr))` | SCB pairs |
| PVM — Residual | `Δmargin − (price+volume+mix+new+cost)` — shown as honesty row | derived |
| AOV | `SUM(scb.total_revenue) / COUNT(DISTINCT scb.sales_invoice)` | SCB |
| UPT | `SUM(sii.qty) / COUNT(DISTINCT sii.parent)` | Sales Invoice Item |
| Refund $ GP Lost | `SUM(scb_cancelled.gross_profit)` over cancelled invoices in period | SCB (docstatus=2) |
| Discount Leakage $ | `SUM(discount_amount)` split line vs order | Sales Invoice |
| Margin-Floor Breach Rate | `COUNT(breach_overrides) / COUNT(invoices) * 100` | Margin Floor Rule + override log |
| Return Rate (qty) | `SUM(returned_qty) / SUM(sold_qty) * 100` | Sales Invoice |
| Margin Data-Quality Flags | `COUNT(items_sold WHERE cogs=0 OR cost IS NULL OR margin<0)` | SCB |
| Aged Inventory at Risk $ | `SUM(qty_on_hand × cost)` for items `days_since_last_sale > 90/180` | Item + SCB velocity |

---

## (H) UX Patterns Worth Copying (research-cited)

1. **Margin Waterfall with color-coded leaks** (Pricefx / Vendavo) — green adds, red leaks; hover shows % of revenue. The single most important "where does margin disappear" visualization. Use ECharts waterfall (`WaterfallChart.vue`).
2. **PVM Margin Bridge** (Vendavo Margin Bridge Analyzer) — period-over-period Δ decomposed; the "THE killer exec view" per `wf1_consolidated`. Include an explicit **residual/unexplained** row for honesty (builds trust).
3. **Interactive What-If with confidence band + margin curve** (Pricefx Market Simulation) — sliders, live recompute, sweep a price *range* not a point, elasticity-adjusted volume. **Critical: call the same `compute_invoice_margin` as posting time** so simulator ≡ posted margin (fixes the trust-killer audit gap).
4. **Floor-price negotiation guardrail at POS** (The Edge + Luxare) — lowest-acceptable price alongside margin; block-with-override capturing a reason; this is what turns the module prescriptive.
5. **AIMS aged-inventory spiff + markdown + signage automation** (The Edge AIMS) — category-unique; auto-generate both staff spiff posters and customer-facing clearance signage from one batch.
6. **RAG-grounded AI recommendations with visible sources** (Zevar's own Pricing Recommendation bones, Pricefx-Agents) — show `confidence_level` as a *label*, render `rag_sources` + `similar_events_count`. The audit shows the UI hides these today — surfacing them is the differentiator.
7. **Margin data-quality guardrail** (Lightspeed Margin Alert) — flag zero/missing/negative cost; very common jewelry data problem; surfaces as an `anomaly_alert`.
8. **TV/Kiosk cycling slides with sticky-pin** (Datadog/Geckoboard/PowerMetrics) — large-font, high-contrast, 60s auto-rotation, visible freshness, sticky during incidents.
9. **One composable filter bar carrying across modules** (RICS + Shopify synthesis) — what the user filters in Sales Monitor carries into the Profit drill-down (shared `criteria` object).
10. **Period-over-period ▲/▼ on every metric tile + "Measure" in-place dropdown** (Shopify/Lightspeed ergonomics).

---

## (I) Permissions & Privacy (especially associate-data isolation)

| Surface | Frontend helper | Backend `only_for()` |
|---|---|---|
| Profit Intelligence (all tabs) | `canAccessProfit()` **(new)** | System Manager, Administrator, Accounts Manager; **Store Manager (read-only, their store)** |
| Approve → Apply a recommendation | `canApplyPricing()` | System Manager, Accounts Manager only (Store Manager requires secondary confirm — fixes audit's no-secondary-approval price-power note) |
| AIMS / What-If Run | `canAccessProfit()` | System Manager, Accounts Manager |
| Associate | — | **Denied `profit.view`** |

**Privacy rules (iron):**
- Absolute margin $, COGS, payment cost, overhead, and per-associate margin heatmap are **owner-financial data**. Associates never see them, even their own sales' margin (they see their *commission tier* and *attainment* in the Workforce self-view, never the underlying COGS).
- Associate-attributed margin rows in `daily_store_sales_rollup` exist for ranking, but any realtime event referencing a named employee + a margin amount is published **only** to `room="admin_wall"` (manager-only) or `user=<employee>` — never global (shared platform §1.2 iron rule).
- The Margin Heatmap's `salesperson` dimension is gated: Store Manager sees only their store's associates; Owner sees all.
- Override reasons on margin-floor breaches are captured (who, when, reason) for audit — these reference a cashier, so the log is `Accounts Manager`-readable only.

**Frontend guard:** `router.js` meta `{ permission: 'profit.view' }`; global `beforeEach` renders `<NoAccess />` instead of flashing chrome before a 403 (shared platform B6).

---

## (J) Integration with the Other 3 Modules + Native Frappe Stack

| Integration | How |
|---|---|
| **Live Monitor (Command Center)** | Profit *produces* `price_shock` (gold moves) and the negative-margin/zero-cost `anomaly_alert`; the wall consumes them. TV margin-at-risk tile + gold-exposure strip are Profit widgets on the wall. |
| **Sales Monitor** | Shares `daily_store_sales_rollup`, `timeStore`, report-builder grammar, filter bar. Sales owns volume/revenue; Profit owns margin. `sales_monitor.get_breakdown(dimension)` reads the rollup; `get_profit_summary` reads the same rollup's `gross_profit`/`cogs_total` columns → **guaranteed reconciliation** between the two modules. |
| **Workforce Intelligence** | `commission.py` refactored to call `profit_math.compute_invoice_margin`; commission paid on the *true* margin (B3 fix — highest $-impact). Commission output → HRMS Salary Component → Salary Slip (payroll-grade, audit-grade). ASC 606/IFRS 15 recognition fields live on the Workforce `Compensation Calculation`. |
| **Frappe Insights** | Owner deep no-code margin analysis against SCB via Workbooks; custom API reserved for realtime + exec views only (no duplication — shared platform §9.1 rule). |
| **HRMS** | Appraisal Cycle / Goal / Salary Slip — receives commission numbers Profit produced. |
| **ERPNext reports** | `gross_profit` (reference only — it uses `valuation_rate`, never point UI at it); `sales_person_target_variance_based_on_item_group` (mirror its variance *pattern* for store PVM). |

---

## (K) Phased Build (P0 must / P1 should / P2 nice) — concrete, assignable tasks

### P0 — Trust Spine (must; nothing else matters until these land)
1. **Wire the SCB hook.** Add `zevar_core.api.profit_intelligence.calculate_sale_cost_breakdown` to `hooks.py` `doc_events["Sales Invoice"]["on_submit"]` *after* `commission.calculate_commissions` (so splits exist). Add `handle_invoice_cancel` on `on_cancel` (set SCB `docstatus=2`, never hard-delete). **Fixes audit B1 — the entire dashboard is blank without this.**
2. **Backfill bench command** `zevar-backfill-scb` — populate SCB for historical invoices (idempotent; re-key on amend).
3. **Build `zevar_core/services/profit_math.py`** with `get_item_cogs(item)` and `compute_invoice_margin(invoice, *, include_overhead=True, include_payment=True, include_labor=True)`. Refactor `calculate_sale_cost_breakdown` to call it.
4. **Repoint the 7 margin sites** (B3): `commission.py:104-109` (highest $-impact), `top_profitability_by_product.py:70-71` (read `scb.gross_profit` directly), `analytics_hub._margin_pct:1012`, `pricing_tools.simulate:210`, `repair_accounting.py:704` (`include_labor=False` documented), `gemstone_value_service.py:125` (rename to `markup_on_cost_pct`), `finance.py:351` (label `accounting_net_profit`).
5. **Fix the 4 broken frontend/backend contracts:** implement `create_recommendation` (or repoint `WhatIfSimulator.vue:217`); make `review_recommendation` accept case-insensitive action; **rewrite `get_margin_heatmap` to pivoted shape** matching `MarginHeatmap.vue`; map `confidence_level`→numeric for the bar.
6. **Schedule the generator:** add `tasks.generate_pricing_recommendations` to `scheduler_events`.
7. **Integration tests** asserting the simulator's `projected_margin_pct` ≡ SCB `gross_margin_pct` for the same item (the trust assertion).
8. **Correct the planning artifacts** (`module_audit_raw.json`) — annotate as unreliable.

### P1 — Exec Views + Jewelry-Accurate COGS (should; the "Intelligence")
9. **`MarginWaterfall` view + `WaterfallChart.vue`** (ECharts) — Revenue → metal → gems → making → labor → commission → payment → overhead → net pocket margin.
10. **PVM Bridge** — `get_pvm_bridge` endpoint + tab; price/volume/mix/new-disc/cost effects + residual honesty row.
11. **Authoritative What-If Simulator** — `simulate_whatif` calling `compute_invoice_margin`; sliders, margin curve (price range sweep), confidence band, elasticity-adjusted volume; persist `What-if Simulation Run`.
12. **Extend COGS model:** add `making_charge`, `alloy_wastage_amount` to SCB + Item; apply `labor_burden_percent`; honor `Labor Cost Pool.allocation_method`; gemstone `cost` vs `replacement` mode.
13. **Net contribution margin** — new `net_contribution_margin_pct` SCB field + KPI.
14. **Multi-store overhead** — convert `Cost Center Allocation` singleton → per-store; add `store`, `item_group` to SCB; add `group_by='store'|'category'`.
15. **ABC overhead** — 3rd allocation method + `Overhead Driver` child.
16. **Gold pass-through %** + **Unrealized gain/loss MTM** — `metal_rate_history`-backed endpoints + widgets.
17. **Surface hidden backend:** per-invoice drill-down, group-by selector, quarterly trend, `get_pricing_action_items` feed, `get_slow_moving_inventory`, RAG sources on recommendation cards.

### P2 — Prescriptive & Recovery (nice; the moat-wideners)
18. **Margin Floor enforcement at POS** — `Margin Floor Rule` doctype; block/warn/override-with-reason; computed from `profit_math`.
19. **AIMS aged-inventory engine** — `Aged Inventory Recovery Run`; tiered spiffs + markdowns; auto-generate staff posters + clearance signage.
20. **Markdown/slow-mover optimization** — aging × velocity × sell-through-target → recovery-maximizing clearance price.
21. **Interchange-tier payment cost** — `Interchange Tier` doctype; Visa/MC/Amex/corporate granularity.
22. **TV/Kiosk mode** — read-only cycling slides, sticky-pin, freshness warning.
23. **Pricing Recommendation as continuous monitors** (Pricefx-Agents pattern) — wired to live margin events, not just daily batch.

---

## (L) Success Metrics / Acceptance Criteria (proving best-in-class)

**Trust (the non-negotiable bar):**
1. For any sampled Sales Invoice, `compute_invoice_margin()` ≡ the SCB row's `gross_profit`/`gross_margin_pct` ≡ the simulator's `projected_margin_pct` for that item ≡ the commission basis used by `commission.py` ≡ the margin shown in `top_profitability_by_product`. **One number, five surfaces, zero drift.** (Integration test gates the build.)
2. **SCB coverage = 100%** of submitted invoices (hook wired + backfill complete); 0% orphan SCB rows after cancel.
3. All 4 previously-broken frontend/backend contracts pass (heatmap renders cells, confidence bar shows, approve/reject works, create-recommendation returns 200).

**Functional completeness:**
4. Margin Waterfall, PVM Bridge, What-If Simulator, Gold Pass-Through, MTM all render real (non-zero) data on a live store.
5. `daily_store_sales_rollup.gross_profit` reconciles to `SUM(SCB.gross_profit)` to the cent for any period/store slice (Profit ⟷ Sales Monitor reconciliation).
6. Margin analysis groupable by store, category, metal, purity, salesperson, channel, SKU, customer.

**Performance:**
7. Any Profit KPI tile < 100ms p95 (reads rollup); waterfall/PVM < 500ms p95 (SCB aggregation, indexed); What-If recompute < 200ms per slider move.

**Prescriptive value (P2):**
8. AIMS run recovers ≥ X% of aged-inventory margin vs the flat-15% baseline; spiff/markdown signage auto-generated.
9. Margin-floor breaches captured with override reason; breach-rate trended.

**Adoption / parity-vs-competitor:**
10. The Profit module exposes the full B-list of `wf1_consolidated.md` "Best-in-Class — Profit Intelligence" features (waterfall, PVM, what-if, gold pass-through, MTM, ABC, AIMS, floor-price, RAG recs, DQ guardrail, interchange tiering) — a superset no single competitor offers. Validated by a feature-coverage checklist mapped 1:1 to that list.

---

### Key file-path index (all absolute)
- Profit math (new): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/services/profit_math.py`
- Profit API (edit): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/profit_intelligence.py`
- Hooks (must edit): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/hooks.py` (`on_submit`/`on_cancel`/`scheduler_events`)
- SCB doctype (extend): `/workspace/development/frappe-bench/apps/zevar_core/zevar_core/unified_retail_management_system/doctype/sale_cost_breakdown/sale_cost_breakdown.json`
- 7-way margin refactor sites: `…/zevar_core/api/commission.py:104`, `…/api/top_profitability_by_product.py:70`, `…/api/analytics_hub.py:1012`, `…/rag/tools/pricing_tools.py:210`, `…/api/repair_accounting.py:704`, `…/services/pricing/gemstone_value_service.py:125`, `…/api/finance.py:351`
- Frontend dashboard (rebuild): `/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/src/pages/dashboards/ProfitIntelligence.vue` + `…/components/pricing/WhatIfSimulator.vue`, `…/components/pricing/PricingRecommendationsPanel.vue`, `…/components/profit/{ProfitOverview,CostBreakdownChart,MarginHeatmap}.vue`
- New chart component: `…/frontend/zevar_ui/src/components/charts/WaterfallChart.vue`
- New doctypes: `what_if_simulation_run`, `margin_floor_rule`, `overhead_driver`, `aged_inventory_recovery_run`, `interchange_tier` under `…/unified_retail_management_system/doctype/`
