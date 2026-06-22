# How to Execute the Inventory Plan

Copy-paste prompts for an agent (Claude Code). Run in `/workspace/development/frappe-bench/apps/zevar_core`.

Read [`INVENTORY_PLAN.md`](./INVENTORY_PLAN.md) first — this doc is the *how*, that doc is the *what & why*.

The agent does **local edits + commits + verification** only. It does **not** push or open PRs unless you explicitly say so (guardrail G1).

---

## Hard guardrails (apply to every prompt)

- **G1 — No push/PR unless told.** Local commits only. When you're happy with a batch, say *"push and open a PR for the last N commits."*
- **G2 — Two-repo sync.** Edit the **running bench copy** here (`apps/zevar_core`). After committing, **sync the same changes to the git source at `/workspace/zevar_core`** so they don't diverge. (This is a known repo gotcha — the running bench copy ≠ the git source.)
- **G3 — Verify via `bench console`, not `bench run-tests`.** `bench run-tests` cannot run in this dev environment (stale test-site DB users + ERPNext test-utils `DuplicateEntryError` on `zevar.localhost`). Verify behavior by exercising the real code path through `bench --site zevar.localhost console` (heredoc-piped), using idempotent helpers in `zevar_core/tests/utils.py` (`ensure_customer`, `ensure_warehouse`, `ensure_item`), wrapped in try/finally + `frappe.db.delete`/`delete_doc(force=1)` cleanup. CI uses a fresh `test_site` and is unaffected — still write unit tests for CI.
- **G4 — Never trust a comp / margin / price number until the math ships.** Until **0a (pricing) lands**, every quote understates making/wastage and every invoice mis-applies GST. Don't run commission or profitability reporting against real payouts expecting correctness until 0a + the Profit Intelligence `profit_math` work (Monitor Suite Phase 1) are both shipped.
- **G5 — Re-verify every `file:line` citation before editing.** The code moves; the plan's citations are point-in-time (2026-06-22). `grep` the symbol first.
- **G6 — Fixtures are the source of truth for Item fields.** New Item fields go in `zevar_core/fixtures/custom_field.json` (registered in `hooks.py` fixtures list), then `bench migrate` + `bench clear-cache`.
- **G7 — One workstream (or small related group) per commit.** Run verification after each. Stop for review at the milestones marked in each prompt.

---

## Verification recipe (reusable) — pricing & price-touching work

Because `run-tests` is blocked locally, verify price math with a console heredoc. Save as `scripts/verify_pricing.py` and run `bench --site zevar.localhost execute zevar_core.scripts.verify_pricing.run` (or pipe to `bench console`):

```python
import frappe
from zevar_core.api import pricing  # confirm actual import path first (G5)

def run():
    # pick items that actually have making-charge data
    rows = frappe.db.sql("""
        select name, custom_making_charge_type, custom_making_charge_value,
               custom_gross_weight_g, custom_net_weight_g, custom_metal_type, custom_purity
        from tabItem
        where is_stock_item=1 and ifnull(custom_making_charge_value,0) > 0
        limit 5
    """, as_dict=True)
    for it in rows:
        price = pricing.get_item_price(it.name)          # <-- confirm signature (G5)
        # hand-compute expected: gold_value + making + ... and print side-by-side
        print(it.name, it.custom_making_charge_type, it.custom_making_charge_value, "=>", price)
        # assert making > 0 in the decomposition; assert gold+making+gems+hallmark sums to price
    print("OK" if rows else "NO ITEMS WITH MAKING DATA — fix data before trusting math")
```

**Definition of done for any price change:** (1) the decomposition prints making+wastage+hallmark > 0 for sample items; (2) a printed quote/tag shows the making line; (3) a test Sales Invoice (`is_pos=1`) splits GST correctly across metal vs making; (4) `services/profit_math.py` + `sale_cost_breakdown` making/wastage are populated, not `0.0`.

---

## Prompt 1 — 0a: Complete the pricing engine *(start here)*

```text
Read and internalize plan/inventory/INVENTORY_PLAN.md (especially §2 gap #1, §5
primitive 3, §6 P0-0a, and §9 re: Profit Intelligence). Re-verify every citation
against the live code (guardrail G5) before editing.

GOAL: complete the sell-price math so making charges, wastage, hallmarking, and
split-rated GST are reflected in every quote and invoice — and stop the 0.0
placeholders in services/profit_math.py / sale_cost_breakdown.

STEP 0 (data audit — do this FIRST, report before continuing):
- Count stock items and the % with custom_making_charge_type / custom_making_charge_value populated.
  Flag any category/source that's blank — fixing math is pointless if the data is missing.
- Confirm the exact field definitions in fixtures/custom_field.json (making type/value; is there a wastage field? a hallmark field?).
- Trace get_item_price end-to-end (zevar_core/api/pricing.py) and the duplicated calc in catalog.py (~line 340-368). Confirm zero making/wastage/hallmark references today.
- Confirm how GST is applied today: zevar_core/tax_events.py apply_store_tax + Store Location tax_template. Document whether making is taxed at a different rate than metal in your jurisdiction (in India, gold and making are typically split-rated) and confirm the current rate values.
STOP AND REPORT step 0 before coding.

STEP 1 (schema): add any missing Item fields via fixtures/custom_field.json (guardrail G6):
- custom_wastage_type (Select: None / Percentage / Per-Gram / Flat) + custom_wastage_value (Float)
- custom_hallmark_charge (Currency)
- (custom_making_charge_type / _value already exist — confirm.)

STEP 2 (pricing.py): extend get_item_price so price =
  gold_value + making_charge + wastage + gemstone_value + hallmark_charge, where
  making = Fixed->value | Percentage->% of gold_value | (and Per-Gram->value*net_weight_g if used),
  wastage = Percentage->% of gold_value | Per-Gram->*net_weight_g | else 0,
  hallmark = flat per piece.
  Preserve the MSRP > Calculated > Standard Rate hierarchy. Return the decomposition too (gold/making/wastage/gems/hallmark) so callers can show it.

STEP 3 (dedupe): make catalog.py's inline calc call pricing.py — one source of truth.

STEP 4 (GST split): ensure the invoice tax breakdown applies the correct rate per component (metal vs making) via tax_events / Store Location tax_template. Confirm against a real test invoice.

STEP 5 (downstream): populate the making/wastage fields in services/profit_math.py and sale_cost_breakdown — remove the 0.0 placeholders.

STEP 6 (verify): use the verification recipe in HOW_TO_EXECUTE.md (bench console, guardrail G3). Print the decomposition for 5 real items; create a test is_pos=1 Sales Invoice and check the tax split; clean up.

HARD GUARDRAILS: G1 (no push), G2 (sync to /workspace/zevar_core), G3 (console verify), G4 (don't trust comp/margin until this + Profit Intelligence ship), G6 (fixtures), G7 (one commit per step group, verify each).

One step-group per commit. STOP for review after STEP 0 (data audit) and after STEP 6 (verification). Summarize: what changed (file:line), the data-coverage % you found, the verification output, and anything that contradicts the plan.
```

---

## Prompt 2 — 0b (HUID) + 0c (unify holds)

```text
Plan context: plan/inventory/INVENTORY_PLAN.md §6 P0-0b and §5 primitive 2 / P0-0c.
Re-verify citations (G5).

0b — HUID/hallmark compliance field:
- Add to fixtures/custom_field.json: custom_huid (Data, 6-char, indexed/searchable),
  custom_hallmark_date (Date), custom_hallmark_center (Link or Data).
- Surface HUID in catalog item details (api/catalog.py get_item_details) and on the printed
  jewelry tag (components/TagPrintPreview.vue, ZPL in services/HardwareService.js).
- Verify via console: create/update an Item with custom_huid, confirm it's searchable and prints.

0c — unify the reservation systems into one hold ledger (primitive 2):
- The three systems: services/reservation_manager.py (soft/hard, custom Stock Reservation),
  api/layaway.py:_reserve_inventory (ERPNext Stock Reservation Entry), services/inventory_locking.py (Redis).
- Goal: ONE hold ledger + ONE check_availability() everyone calls. Types: cart-hold | layaway |
  memo-out | repair-in | display-locked, each with expiry. Keep inventory_locking.py as the
  concurrency guard UNDERNEATH (don't remove the Redis row-lock). Migrate layaway off ERPNext SRE.
- This is the riskiest P0 refactor — do it behind the existing behavior, verify no double-count
  on a layaway + soft-hold of the same serial, and confirm checkout still locks.
- STOP for review after 0b, then again after the 0c design before migrating layaway.

Guardrails G1/G2/G3/G7 apply.
```

---

## Prompt 3 — P1 (ownership/memo, GMROI analytics, replenishment)

```text
Plan context: plan/inventory/INVENTORY_PLAN.md §5 (primitives 1,3,4) and §6 P1.
Prerequisite: 0a (pricing) and 0c (unified holds) should be shipped first — confirm before starting.

1a — Ownership dimension + vendor-memo engine (primitive 1):
- Promote the partial Vendor Memo (currently only inside api/special_order.py for memo-sourced
  stones) to a first-class Vendor Memo doctype. Ownership states: Owned | Vendor-Memo |
  Consignment | Customer-Approval-Out, backed by an ownership LEDGER (transitions auditable).
- Lifecycle: receive (as Memo, NOT Owned) -> per-vendor daily aging 0-30/31-60/61-90/90+ with
  60/75/85-day alerts -> on sale, auto-create vendor payable at memo cost -> return with
  signed-slip capture + partial returns -> close. Add customer on-approval outbound memo.
- Make EVERY report/count/valuation ownership-aware (memo in its own column).

1b — Merchandising analytics (depends on primitive 3, landed cost):
- Add to inventory_dashboard.py / analytics_hub.py: GMROI (gross margin / avg inv at cost),
  turnover (COGS / avg inv at cost), sell-through, days-of-supply, ABC classification.
- Wire the existing overage scorer (analytics_hub.py) to GMROI so markdown recs are margin-aware.

1c — Replenishment 2.0:
- Min/max + safety stock from per-store velocity + seasonality + supplier lead time.
- Extend the raise_mr row-action (reports.py ~1422) into full Material Request / PO automation.
- JIT "top sellers at risk of stockout" view.

Also land primitive 4 (receipt-date-based aging) as part of 1b — reconcile inventory_dashboard.py
aging to the overage scorer's true days-in-inventory.

Guardrails G1/G2/G3/G4/G7. STOP for review at each of 1a/1b/1c.
```

---

## Prompt 4 — P2 (multi-store) then P3 (differentiators)

```text
Plan context: plan/inventory/INVENTORY_PLAN.md §6 P2 and P3. Prerequisite: P1 shipped.

P2:
- 2a cross-store: live "locate at another store" in api/catalog.py get_pos_items + one-click
  request transfer; extend api/inventory.py transfers (~165-264) to bulk/weight (findings,
  chain-by-gram, scrap lots) via a real batch/lot dimension.
- 2b store lifecycle: add store-onboarding to frontend Settings.vue (create store -> provisions
  Warehouse + POS Profile + Store Location + zones); add store-scoped roles/permissions.
- 2c consolidated + per-store reporting on every dashboard; document multi-company as a future
  layer (design ownership+warehouse so multi-company is additive).

P3 (pick per stakeholder priority):
- 3a RFID: daily open/close case-count routine as policy; real-time zone anti-theft alerts;
  lost/missing-vs-memo reconciliation.
- 3b repair/special-order: barcoded repair envelope (track the customer's actual piece, not the
  REPAIR-ITEM placeholder) + customer auto-notify; special-order criteria -> vendor-catalog
  filtering (MaxiTurn-style); close scrap->refining->new-stock loop via Job Bag + karigar
  wastage ledger.
- 3c salesperson commission engine + lead-source attribution; tag-reprint/re-tag queue that
  fires when metal rates cross a threshold or HUID is added.

Guardrails G1/G2/G3/G7. STOP for review at each sub-item.
```

---

## Good to know

- **Paths** are absolute under `/workspace/development/frappe-bench/apps/zevar_core/` — run the agent there so they resolve.
- **`apps/zevar_core` ↔ `/workspace/zevar_core` sync** (guardrail G2) is the #1 gotcha — the running bench copy is not the git source. Sync after every commit.
- **`bench run-tests` is blocked locally** (guardrail G3) — use `bench --site zevar.localhost console`. Still write unit tests; CI runs them on a fresh `test_site`.
- **`Performance Log` is immutable** — its `on_trash` throws "cannot be deleted." Clean up test logs via raw `frappe.db.delete("Performance Log", ...)` (bypasses `on_trash`); any backfill must check-before-insert, never delete-and-recreate.
- **Default behavior:** agent commits locally and waits for review. When a batch is good, tell it *"push and open a PR for the last N commits."*
- **When the plan and the code disagree, trust the code** — flag the discrepancy in your review summary rather than blindly following the plan (the Monitor Suite plan already drifted on the performance-log hooks; see INVENTORY_PLAN.md §9).
