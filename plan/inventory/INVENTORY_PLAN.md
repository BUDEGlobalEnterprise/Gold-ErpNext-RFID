# Jewelry POS Inventory — Master Plan

> Make **zevar_core's inventory** the best in the jewelry-POS business — for a single store and for a chain — by fusing the strongest inventory features from industry leaders (The Edge, WJewel, Lightspeed, Indian jewellery ERP) into one refined layer on the Frappe/ERPNext stock engine.

This folder is the complete, evidence-backed inventory plan: competitive research → current-state audit (verified against live code) → target architecture → phased roadmap. **To actually build it, read [`HOW_TO_EXECUTE.md`](./HOW_TO_EXECUTE.md).**

---

## TL;DR

- **The inventory layer is already strong — it doesn't feel best-in-class because a few load-bearing pieces are broken, missing, or fragmented**, not because features are broadly absent.
- **The single most important finding (verified 2026-06-22):** the sell-price math ignores making charges, wastage, GST split, and hallmarking. `grep` for `making|wastage|hallmark|huid` in `zevar_core/api/pricing.py` and `zevar_core/api/catalog.py` returns **zero matches**. Every quote is under-decomposed and every invoice is mis-taxed. This is revenue leakage *and* compliance exposure on every transaction.
- **Four foundational primitives** must land first — they unblock almost everything: (1) ownership dimension + ledger, (2) unified hold/reservation ledger, (3) landed-cost basis, (4) receipt-date-based aging.
- **Seven workstreams, phased P0→P3.** P0 = fix the broken/compliance items (pricing, HUID, unify holds). P1 = vendor-memo engine + GMROI analytics + demand-aware replenishment. P2 = multi-store leadership. P3 = RFID routine, repair/special-order polish, commissions.
- **Recommended start:** **0a — the pricing engine.** Highest ROI, touches every transaction, feeds the Profit Intelligence / margin work, and is self-contained. See [`HOW_TO_EXECUTE.md`](./HOW_TO_EXECUTE.md) Prompt 1.

---

## How to use this folder

| Want | Read |
|---|---|
| The what & why (this is it) | `INVENTORY_PLAN.md` |
| The how & when — copy-paste agent prompts + step-by-step + guardrails | [`HOW_TO_EXECUTE.md`](./HOW_TO_EXECUTE.md) |
| How this connects to the existing Monitor Suite plan (Profit Intelligence, margin) | §9 below |

---

## Provenance

- **Codebase audit:** 3 deep read-agents over the zevar_core backend (`api/`, `services/`, doctypes, `hooks.py`) and the Vue frontend (`frontend/zevar_ui/`).
- **Industry research:** The Edge (legacy US leader), WJewel (vendor-memo + RFID), Lightspeed (multi-store), Indian jewellery ERP (HUID/making/karigar), GMROI/turnover benchmarks, RFID loss-prevention. ~20 sources (linked in §8).
- **Verification:** every load-bearing claim here was re-confirmed by direct `grep`/`read` of the **current** code on 2026-06-22. `file:line` citations are point-in-time and the code moves — **re-verify before editing** (the audit found one prior planning doc, the Monitor Suite exec summary, had already gone stale — see §9).

---

## §1 Current state — what already exists (and is good)

zevar_core builds on ERPNext's stock engine and adds substantial jewelry-specific capability. This is the baseline to protect, not rebuild.

| Area | What exists | Where |
|---|---|---|
| **Stock engine** | ERPNext native: `Item`, `Serial No`, `Bin`, `Stock Ledger Entry`, `Stock Entry` | erpnext core |
| **Jewelry item model** | 64 custom fields: metal, purity (24K/22K/18K…), gross/net/stone weight (net auto-computed), gemstone child table with 4C grading (carat/clarity/cut/color), making-charge fields, vendor, dimensions | `fixtures/custom_field.json`, `api/catalog.py` |
| **Live metal pricing** | `Gold Rate Log`, scheduled gold-rate fetch (every 15 min), price = `gold_value + gemstone_value`, hierarchy MSRP > Calculated > Standard | `api/pricing.py`, `tasks.fetch_live_gold_rate` |
| **Serialization** | Per-piece Serial No; pessimistic Redis row-locking at checkout | `services/inventory_locking.py` |
| **Piece lifecycle** | Full per-piece history (sale/return/receipt/transfer/audit) | `api/inventory.py:409-462` |
| **Stocktake / audit** | RFID/barcode counts with **two-person sign-off**, **store-freeze on variance**, discrepancy resolution | `api/inventory_audit.py`, `InventoryAudit.vue`, `DiscrepancyBoard.vue` |
| **Inter-store transfer** | Serial-scoped dispatch → transit warehouse → receive, with variance flagging | `api/inventory.py:165-264`, `StoreTransferModal.vue` |
| **Old-gold / scrap buyback** | Gold Purchase → Material Receipt of scrap (`SCRAP-{metal}-{purity}` by grams) + payment | `doctype/gold_purchase/`, `api/gold_purchase.py` |
| **Repair job-work** | Repair Order + parts consumption (Material Issue) + store-to-store transfer + external bench | `api/repair.py`, `doctype/repair_order/` |
| **Special orders + job bags** | Wizard + shop-floor Kanban + customer portal; inventory lock for in-stock stones | `api/special_order.py`, `pages/SpecialOrders.vue` |
| **Layaway** | Contract + inventory reservation | `api/layaway.py` |
| **Audit trail** | `POS Audit Log` (who/what/when/severity) + CSV/Excel export | `doctype/pos_audit_log/`, `api/audit_log.py` |
| **Inventory dashboard** | Aging buckets, 6-month shrinkage trend, store scorecard, dead-stock/overage scoring with markdown % | `api/inventory_dashboard.py`, `api/analytics_hub.py` |
| **Tag printing** | Jewelry-tag ZPL rendering, integrated at item-create | `components/TagPrintPreview.vue`, `services/HardwareService.js` |

---

## §2 The gaps (verified)

These are the reasons it doesn't *feel* best-in-class. Ordered by impact.

1. **🔴 Sell-price math is incomplete — making/wastage/GST/hallmark all ignored.** `get_item_price` computes `gold_value + gemstone_value` only; making-charge fields exist on the Item but are never read into price. **Verified:** zero `making|wastage|hallmark|huid` references in `pricing.py`/`catalog.py`. The placeholder in `services/profit_math.py` is `0.0` with the comment *"Populated when item-level making decomposition lands; 0 until then."* **Affects every transaction; mis-taxes every invoice** (making is typically GST-rated differently from metal).
2. **🔴 No HUID / hallmark field anywhere.** Compliance gap — HUID is mandatory for hallmarked jewelry sold in India since June 2022. **Verified:** `grep huid|hallmark` across the app returns no Item field.
3. **🟠 Three reservation systems that don't coordinate** → double-counting / double-sell risk. `services/reservation_manager.py` (soft/hard hold, custom `Stock Reservation`), `api/layaway.py:_reserve_inventory` (ERPNext `Stock Reservation Entry`), `services/inventory_locking.py` (Redis concurrency guard). A layaway-held serial and a soft-held-cart serial can both show "available."
4. **🟠 No merchandising intelligence** — no GMROI, inventory turnover, sell-through, or days-of-supply. You cannot answer "which inventory makes me money" — *the* question for a category that turns only 1–2×/yr. Dead-stock/overage scoring exists but isn't margin-aware.
5. **🟠 No ownership dimension** — every piece is implicitly "owned." Industry leaders tag every line `Owned | Vendor-Memo | Consignment | Customer-Approval-Out`; this one field gates accounting, aging, vendor settlement, and physical-count separation. (A partial Vendor Memo exists only inside `special_order.py` for memo-sourced stones.)
6. **🟡 Shallow replenishment** — static `Item.reorder_level` field only; no velocity/seasonality/lead-time awareness, no auto-PO (a `raise_mr` row-action exists at `reports.py:1422`).
7. **🟡 Multi-store is single-company, serial-only.** Transfers are serial-scoped (no bulk/weight transfer for findings/metals); `Store Location` + `Warehouse` must be created in Frappe Desk (no POS-UI onboarding); no multi-company/legal-entity support.
8. **🟡 Aging is movement-based, not receipt-based.** `inventory_dashboard.py` ages by "days since last SLE movement" while the overage scorer computes true days-in-inventory — they don't reconcile.
9. **🟡 No batch/lot at POS** (only serials); **exchange is non-atomic** (return + separate sale); **held carts don't reserve stock**; **no scrap→refining→new-stock loop** (scrap is receipted and stops there); **no tag-reprint queue** (tagging is one-shot at create).
10. **🟡 No salesperson commission engine / lead-source attribution** (salespersons are captured but not compensated).

---

## §3 What industry leaders do (research synthesis)

### The Edge — the legacy US gold-standard for independent jewelers
- Piece tracking by **barcode or RFID chip**; jewelry **tag printers** as first-class hardware (not an afterthought).
- Per item: cost, sale price, **margin, and a floor/lowest-acceptable price** the clerk can negotiate down to — never sell below floor.
- **"MaxiTurn":** browse/select/order from **vendor catalogs inside the POS**; just-in-time replenishment surfaces top-sellers at risk of stockout.
- **Repair/custom:** request at POS → generates a **barcoded envelope** to physically track the customer's piece through the job; **auto-texts the customer** when complete. Special orders capture structured criteria (metal/gem/size/budget) and **filter the vendor catalog** against them.
- Layaway, appraisals, gift certificates, and **trade-in/buy** are all transaction types in one POS. Auto salesperson **commissions** + lead-source attribution. CRM logs every transaction/repair/appraisal per customer with item images.
- *Constraint to mirror:* locally installed, offline-first, multi-store built ground-up (per-store + per-register licensing).

### Vendor memo / consignment (WJewel) — the model you're missing
- Every inventory line carries an **ownership flag: Owned / Memo / Consignment.** Memo = vendor lends a piece for 30/60/90 days, title stays with vendor; both are **off-balance-sheet until sold.**
- Per-line metadata: ownership + **vendor reference + vendor memo number + receive date + due date**, visible at POS so the clerk knows it's borrowed.
- Memo stock tracked **in a separate column in every report** — mixing memo into owned is the #1 cause of inflated assets / inflated insurance premiums / audit findings.
- **Aging by vendor** (0-30/31-60/61-90/90+), computed **daily**, alerts at 60/75/85 days.
- On sale: **auto-creates a payable to the vendor at memo cost** → pushes to accounting with no double entry. Margin = retail − memo cost.
- Return: scan out, **capture vendor-signed return slip**, partial returns supported (each piece its own line). End-of-period unsold → returned, memo closes.
- **Lost/missing reconciliation** ("on memo but not located on last audit") is a built-in report. Every status change stamped user + timestamp.
- Two extra flows: **customer on-approval** (owned stock goes OUT to a customer to take home, own aging) and **outbound memo** (wholesaler→retailer, same model reversed).

### RFID real-time + loss prevention
- **Daily open/close case count in ~5 minutes** (vs hours manual). Manual counts are inaccurate by **15–25%** on any given day — RFID eliminates that.
- **Real-time zone anti-theft alerts** when a tagged piece leaves a defined zone; concealed in-case antennas for live stock visibility.
- Discrepancy detection during audits; POS scan-at-checkout instantly updates counts; multi-store + e-commerce sync.

### GMROI / merchandising math
- **GMROI = Gross Margin ÷ Average Inventory at Cost** — profit per dollar invested in inventory. **Inventory turnover = COGS ÷ Average Inventory at Cost.** Sell-through = units sold ÷ (units sold + on-hand).
- Jewelry turns **1–2×/yr** vs 4–8× for general retail → GMROI is *the* decisive metric; turnover alone is misleading.
- Exclude aged/dead stock from average inventory so it doesn't deflate GMROI — track it separately with a markdown engine.

### Indian-market specifics (HUID / making / karigar)
- **HUID** (6-char Hallmark Unique ID) mandatory since June 2022.
- **Price formula:** `(gold rate/g × net gold weight) + making charge + wastage + GST + hallmarking charge`. Making can be **per-gram, percentage of gold value, or flat**; wastage typically 5–12%.
- **GST is split-rated** (gold and making attract different rates) → decomposition is required for correct tax.
- **Karigar (artisan) job work:** track metal issued/returned, wastage ledgers, refining batches.

---

## §4 The benchmark table

| Capability | Leaders | Your state | Gap |
|---|---|---|---|
| Piece tracking (barcode+RFID) | ✅ standard | ✅ Serial No + RFID + barcode | — |
| Daily case count / freeze-on-variance | ✅ RFID ~5 min | ✅ strong | add the *daily routine* as policy |
| Ownership model (Owned/Memo/Consignment) | ✅ first-class | ❌ none | **critical** |
| Vendor memo lifecycle | ✅ full | ❌ partial only | **high** |
| Pricing (metal+making+wastage+GST+hallmark, floor price) | ✅ | ❌ metal+gems only | **broken** |
| GMROI / turnover / sell-through | ✅ | ❌ velocity labels only | **leadership metric** |
| Demand/seasonality replenishment | ✅ JIT + auto-order | ⚠️ static reorder_level | shallow |
| Multi-store (locate/transfer/store-onboarding) | ✅ ground-up | ⚠️ intra-company, serial-only | partial |
| Special order → vendor catalog match | ✅ | ⚠️ wizard, no match | partial |
| Repair (envelope + auto-notify) | ✅ | ⚠️ no envelope/notify | partial |
| HUID/hallmark | ✅ mandatory | ❌ no field | **compliance** |
| Scrap → refining → new stock | ✅ | ❌ stops at scrap receipt | partial |
| Commissions / attribution | ✅ | ⚠️ captured, not paid | partial |
| Tag reprint queue | ✅ | ⚠️ one-shot at create | partial |

---

## §5 Target architecture — the 4 foundational primitives

Small, foundational, and they unblock almost every workstream. **Build these before piling on features.**

### Primitive 1 — Ownership dimension + ledger
Every piece carries ownership state `Owned | Vendor-Memo | Consignment | Customer-Approval-Out`, backed by an **ownership ledger** (who held it, when, why) rather than a static field, so transitions are auditable. Transforms reporting, counting, valuation, and accounting simultaneously.

### Primitive 2 — Unified hold/reservation ledger
Collapse the three systems (`reservation_manager.py`, `layaway.py:_reserve_inventory`, `inventory_locking.py`) into **one source of truth**: a hold ledger with types `cart-hold | layaway | memo-out | repair-in | display-locked`, each with expiry. One `check_availability()` query everyone calls. Keep Redis locking as the concurrency guard *underneath*. **Kills the double-count bug permanently.**

### Primitive 3 — Landed-cost basis
Every piece stores true landed cost (metal at receipt + gemstones + making + duty/freight). You have `custom_cost_price` — promote it to a real, computed landed cost. **GMROI is impossible without this.**

### Primitive 4 — Receipt-date-based aging
Reconcile the dashboard aging (`inventory_dashboard.py`) to **receipt date**, matching the overage scorer's true days-in-inventory, so aging is honest and the two agree.

---

## §6 The 7 workstreams

### P0 — Fix what's broken or non-compliant *(now, ~1–2 weeks each)*
- **0a — Complete the pricing engine.** Wire making + wastage + hallmark into `get_item_price`; collapse the duplicated calc in `catalog.py` to one source; apply the split-rated GST; populate the `0.0` placeholders in `services/profit_math.py` + `sale_cost_breakdown`. *Highest ROI on the list; feeds Profit Intelligence.*
- **0b — HUID/hallmark compliance.** Add `custom_huid`, `custom_hallmark_date`, `custom_hallmark_center` to Item; make HUID searchable + printed on tags.
- **0c — Unify the reservation systems** into Primitive 2; migrate layaway off ERPNext SRE onto the single ledger.

### P1 — Foundation that multiplies value *(~2–4 weeks)*
- **1a — Ownership dimension + vendor-memo engine.** Promote the partial Vendor Memo to a full doctype: receive (as Memo, not Owned) → per-vendor daily aging (0-30/31-60/61-90/90+) → on sale auto-create vendor payable at memo cost → return with signed-slip + partial returns → close. Make **every report/count/valuation ownership-aware.** Add **customer on-approval** outbound memo.
- **1b — Merchandising analytics core.** Add GMROI, turnover, sell-through, days-of-supply, ABC classification to `inventory_dashboard.py`/`analytics_hub.py`; wire the existing overage scorer to GMROI.
- **1c — Replenishment 2.0.** Min/max + safety stock from per-store velocity + seasonality + supplier lead time; extend `reports.py:1422` `raise_mr` into full PO automation; JIT "top sellers at risk" view.

### P2 — Multi-store leadership *(~4–8 weeks)*
- **2a — Cross-store operating model.** Live "locate at another store" in the catalog + one-click request transfer; extend transfers to **bulk/weight** (findings, chain-by-gram, scrap lots) via a real **batch/lot** dimension.
- **2b — Store lifecycle in POS UI.** Add store-onboarding to `Settings.vue` (create store → provisions Warehouse + POS Profile + Store Location + zones); add store-scoped roles/permissions.
- **2c — Consolidated + per-store reporting** on every dashboard; document the multi-company roadmap as a future layer (design ownership + warehouse so multi-company is an addition, not a rewrite).

### P3 — Differentiators *(ongoing)*
- **3a — RFID real-time + loss prevention.** Daily open/close case-count routine as policy; real-time zone anti-theft alerts; lost/missing-vs-memo reconciliation.
- **3b — Repair + special-order modernization.** Barcoded repair envelope (track the customer's actual piece, not a placeholder); auto-notify on status; special-order criteria → vendor-catalog filtering (MaxiTurn-style); close the scrap→refining→new-stock loop via the Job Bag + a karigar wastage ledger.
- **3c — Commissions, attribution & tag management.** Salesperson commission engine + lead-source attribution; tag-reprint/re-tag queue that fires when metal rates cross a threshold or HUID is added.

---

## §7 Sequencing & roadmap

| Phase | Workstreams | Outcome | Why this order |
|---|---|---|---|
| **P0** | 0a pricing, 0b HUID, 0c unify holds | Correct quotes, compliant, no double-sell | Fix broken/blocking first |
| **P1** | 1a ownership/memo, 1b GMROI analytics, 1c replenishment | "Best-in-class single store" | What makes you *feel* intelligent; depends on P0 primitives |
| **P2** | 2a cross-store, 2b store lifecycle, 2c reporting | "Best-in-class multi-store" | Builds on P1's clean model |
| **P3** | 3a RFID routine, 3b repair/special-order, 3c commissions | Differentiators | Polish layer |

**First 30 days:** ship **0a** and **0b** (small, immediate revenue + compliance value); spec **0c** (highest-risk refactor). Everything compounds on these. Detailed step-by-step in [`HOW_TO_EXECUTE.md`](./HOW_TO_EXECUTE.md).

---

## §8 Sources

- [The Edge review — CardFellow](https://www.cardfellow.com/blog/the-edge-jewelry-pos-review)
- [The Edge (official)](https://www.theedgeforjewelers.com/features)
- [Vendor memo & consignment tracking — WJewel](https://www.wjewel.com/blog/memo-and-consignment-tracking-jewelers.php)
- [Jewelry inventory software (RFID) — WJewel](https://www.wjewel.com/jewelry-inventory-software.php)
- [Multi-store inventory transfers — Lightspeed Retail](https://shopkeep-support.lightspeedhq.com/hc/en-us/articles/47479991501083-Multi-Store-Management)
- [What is a good inventory turnover ratio for jewelry — Jewel360](https://jewel360.com/blog/what-is-a-good-inventory-turnover-ratio)
- [What is GMROI — Retalon](https://retalon.com/blog/what-is-gmroi)
- [GMROI — ShipBob](https://www.shipbob.com/blog/gmroi/)
- [Gold making charges & GST — ClearTax](https://cleartax.in/s/gold-making-charges)
- [How gold price is calculated — Ujjivan SFB](https://www.ujjivansfb.bank.in/banking-blogs/gold-loan/how-gold-price-is-calculated-by-jewellers)
- [How to choose the best jewelry POS — LogicMate](https://www.logicmate.com/how-to-choose-the-best-jewelry-pos-software/)
- [Best jewelry POS 2025/2026 — jewelrypos.net](https://jewelrypos.net/comparison)
- [Jewelry store inventory management guide — ELO ERP](https://eloerp.net/blog/jewelry-store-inventory-management/)

---

## §9 Relationship to the Monitor Suite plan (`plan/EXECUTIVE_SUMMARY.md`)

This inventory plan is **complementary, not overlapping**, with one intentional seam:

- **Profit Intelligence (Monitor Suite, Phase 1)** owns *post-sale margin/COGS decomposition* — `profit_math`, the "one true margin," the Margin Waterfall, and `Sale Cost Breakdown`. **Inventory 0a owns the *sell-price* decomposition** (`get_item_price`). They share one dependency: **the making-charge value on the Item**. Landing 0a produces the item-level making value that `profit_math` needs, so 0a should land **before or alongside** Profit Intelligence.
- **Verified drift in the Monitor Suite docs (2026-06-22):** its exec summary's P0 #2 claims "the *entire* Performance Log event stream is dead." The **current** `hooks.py` wires `log_sale_event`, `log_sale_cancel_event`, `log_layaway_event`, `log_repair_event`, and `log_attendance_event` — so that P0 is **resolved**. `calculate_sale_cost_breakdown` is **still not wired** into `Sales Invoice on_submit` (only `commission.calculate_commissions` and `performance.log_sale_event` are). Re-verify the Monitor Suite roadmap against live `hooks.py` before acting on it.
- **Shared guardrails** (bench copy ↔ git-source sync, console-not-run-tests verification, never trust comp/margin until math ships) apply to both plans — carried into [`HOW_TO_EXECUTE.md`](./HOW_TO_EXECUTE.md).
