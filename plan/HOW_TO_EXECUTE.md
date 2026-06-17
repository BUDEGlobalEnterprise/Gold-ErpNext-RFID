# How to Execute This Plan

Copy-paste prompts for an agent (Claude Code). Run in `/workspace/development/frappe-bench/apps/zevar_core`.

The agent does **local wiring/fixing + commits + tests** only. It does **not** push or open PRs unless you explicitly say so (see guardrail).

---

## Prompt 1 — Quick-Win Sprint (start here)

```text
Read and internalize the plan in ./plan/ — start with plan/README.md,
then plan/EXECUTIVE_SUMMARY.md, then plan/04_roadmap/IMPLEMENTATION_ROADMAP.md
(especially §0 grounding facts and §4 Quick-Win Sprint), and
plan/03_target_design/00_SHARED_PLATFORM.md §0 (the 7 P0 bugs) and §2 (profit_math).

Your job: execute the Quick-Win Sprint (Q1–Q10) from roadmap §4, in order,
on a new feature branch. These are mostly wiring + contract fixes.

HARD GUARDRAILS:
- Do NOT git push or open any PR unless I explicitly tell you to. Local commits only.
- Edit the RUNNING BENCH copy here (apps/zevar_core). After committing, sync the
  same changes to the git source at /workspace/zevar_core so they don't diverge.
- Do NOT run any compensation calculation, commission run, or Salary Slip against
  real/production payouts until Q1, Q2 (wired hooks) AND Q4 (backfill) have all
  shipped. The current margin math pays commissions on an inflated margin — fix
  before trusting any comp number.
- Backfills (Q4: zevar-backfill-scb + backfill-performance-logs) MUST be idempotent
  (natural keys: SCB by sales_invoice; Performance Log by (employee, event_date,
  reference_document)). Add them as bench commands; run on a dev site with a
  --dry-run first; never re-create duplicates.
- Q1/Q2 wiring goes in zevar_core/hooks.py: add
  zevar_core.api.profit_intelligence.calculate_sale_cost_breakdown to
  Sales Invoice on_submit (AFTER commission.calculate_commissions) and an on_cancel
  handler; add performance.log_sale_event / log_sale_cancel_event to on_submit/on_cancel.
- Re-verify the claim yourself before wiring: grep hooks.py doc_events.

WORKING STYLE:
- One quick-win (or a small related group) per commit. After each, run the relevant
  bench tests + any new unit test you add, and run the grep gates from roadmap §7
  (e.g. after Q9: grep -rc "function fmt(" frontend/zevar_ui/src/pages/dashboards → 0;
  after Q10: no window.location.href in ReportsHub.vue).
- Stop and report after Q1–Q5 (the data-integrity batch: SCB + workforce hooks,
  schedulers, backfill, the 4 broken Profit contracts) before touching the
  frontend/realtime batch (Q6–Q10). Summarize: what changed (file:line), test
  results, and any deviation from the plan.
- Flag anything in the plan that conflicts with what you actually find in the code
  rather than blindly following it.

Start now with Q1.
```

---

## Prompt 2 — Continue to later phases

```text
The Quick-Win Sprint is done and verified. Now execute Phase 0 finish + Phase 1
(Profit Intelligence) from plan/04_roadmap/IMPLEMENTATION_ROADMAP.md §2, in order.

Same guardrails as before: local commits only (no push/PR unless I say so); edit the
bench copy then sync to /workspace/zevar_core; never run comp calcs until Phase 0
fully ships; gate the "one true margin" with the integration test from roadmap §7
(gross_margin_pct identical on 5 surfaces). One phase section per review batch; stop
for review at each milestone (M0, M1).
```

---

## Good to know
- Paths in the plan are absolute under `/workspace/development/frappe-bench/apps/zevar_core/` — run the agent there so they resolve.
- The `apps/zevar_core` ↔ `/workspace/zevar_core` sync is a known repo gotcha (running bench copy ≠ git source) — it's in the guardrails.
- Default behavior: agent commits locally and waits for your review. When you're happy with a batch, tell it "push and open a PR for the last N commits."
