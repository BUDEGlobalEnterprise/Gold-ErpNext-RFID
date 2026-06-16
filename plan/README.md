# Zevar Monitor Suite — Master Plan

> Make **Live Monitor, Sales Monitor, Profit Intelligence, and Workforce Intelligence** the best-in-class core of the world's leading jewelry POS — by fusing the strongest features from global jewelry/retail leaders into one refined superset, implemented module-by-module on the Frappe/ERPNext stack.

This folder is the complete, evidence-backed plan: competitive research → current-state audit → target designs → phased roadmap. **Start with [`EXECUTIVE_SUMMARY.md`](./EXECUTIVE_SUMMARY.md).**

---

## TL;DR

- **The backends are ahead of the frontends; the integration layer is the dominant flaw.** Three of the four modules currently emit partially-zero or stub data in a live system because of unwired hooks — *not* because the logic is missing.
- **The single most important finding (verified by direct code read of `hooks.py`):** `calculate_sale_cost_breakdown` and the *entire* `log_*_event` family are **not registered** → Sale Cost Breakdown and Performance Log tables are **empty in production** → Profit Intelligence returns zeros and Workforce's revenue axis is always 0. Both are **payroll-affecting**.
- **Recommended order:** Shared Platform (kill 7 P0 bugs) → **Profit** (one true margin) → **Sales** (volume spine) → **Workforce** (unlock the rich-but-dark backend) → **Live Monitor** (realtime capstone). See [`04_roadmap/`](./04_roadmap/).
- **Ship a Quick-Win Sprint first (S1):** wire the hooks, backfill history, fix 4 broken UI↔API contracts, resurrect dead realtime, add live sales to the wall, surface zero-cost KPIs (UPT/run-rate), adopt one chart lib, collapse the 4 live screens into one command center. Stakeholder-visible value on ~day 5.

---

## Document map

| Read | Document | What it is |
|---|---|---|
| **1st** | [`EXECUTIVE_SUMMARY.md`](./EXECUTIVE_SUMMARY.md) | The whole plan on ~2 pages: vision, differentiation, current state, P0s, sequencing, MVPs, success metrics, "what to do Monday". |
| 2nd | [`04_roadmap/IMPLEMENTATION_ROADMAP.md`](./04_roadmap/IMPLEMENTATION_ROADMAP.md) | Phased, dependency-ordered, sprint-by-sprint plan + risk register + portfolio success metrics. The execution blueprint. |
| 3rd | [`03_target_design/00_SHARED_PLATFORM.md`](./03_target_design/00_SHARED_PLATFORM.md) | The shared spine all 4 modules build on: realtime/event bus, unified KPI+calc layer (`profit_math`, rollups), design system, dashboard shell, role model. |
| 4th | [`03_target_design/01_LIVE_MONITOR.md`](./03_target_design/01_LIVE_MONITOR.md) · [`02_SALES_MONITOR.md`](./03_target_design/02_SALES_MONITOR.md) · [`03_PROFIT_INTELLIGENCE.md`](./03_target_design/03_PROFIT_INTELLIGENCE.md) · [`04_WORKFORCE_INTELLIGENCE.md`](./03_target_design/04_WORKFORCE_INTELLIGENCE.md) | Engineering-ready target design per module: vision, feature set, IA, data model, API surface, KPIs (with formulas), UX, permissions, phased build, acceptance criteria. |
| Reference | [`02_current_state_audit/EXECUTIVE_SUMMARY.md`](./02_current_state_audit/EXECUTIVE_SUMMARY.md) + [`CURRENT_STATE_AUDIT.md`](./02_current_state_audit/CURRENT_STATE_AUDIT.md) | Honest baseline of what exists today, file:line grounded, with the verified P0 corrections. |
| Reference | [`01_research/FEATURE_MATRIX.md`](./01_research/FEATURE_MATRIX.md) + [`research_digest.md`](./01_research/research_digest.md) | Competitive teardown of 10 global leaders (The Edge, RICS, Valigara, Lightspeed, Shopify, ERPNext/Frappe, Pricefx, commission SaaS, live-ops, workforce/gamification), 261 sources. |
| Raw | [`00_raw/`](./00_raw/) | Consolidated synthesis (`wf1_consolidated.md`) + structured JSON (research, audits, args). |

---

## Suggested reading order

1. **`EXECUTIVE_SUMMARY.md`** — orient.
2. **`04_roadmap/IMPLEMENTATION_ROADMAP.md`** §0–§4 — see the verified baseline, the recommended order, and the Quick-Win Sprint.
3. **`03_target_design/00_SHARED_PLATFORM.md`** — the foundation (do Phase 0 first).
4. Each module design in roadmap order (Profit → Sales → Workforce → Live).
5. Drop into `01_research/` and `02_current_state_audit/` for source detail.

---

## How this plan was produced (provenance)

- **Competitive research:** 12 parallel web-research agents over global jewelry/retail POS leaders, consolidated into a best-in-class feature matrix.
- **Current-state audit:** 5 parallel auditors read the actual Zevar code (backends + frontends + hooks), producing file:line findings.
- **Verification:** every load-bearing claim (unwired hooks, dead realtime, 7-way margin) was **re-confirmed by direct grep/read of `hooks.py` and the source**, and supersedes an earlier rate-limited audit pass that was wrong on two counts. The design and roadmap agents independently re-read the code and restate the corrected baseline.
- **Design + roadmap:** 6 agents (1 platform → 4 module designs → 1 roadmap) authored against the verified audit + research.

> ⚠️ Note: `02_current_state_audit/module_audit_raw.json` is the *pre-correction* WF1 raw artifact and contains two known-wrong claims (that the Profit hook is wired and the Workforce layaway/repair/attendance hooks are wired). **`CURRENT_STATE_AUDIT.md` is the authoritative, corrected version** — all P0 claims in it were re-verified by direct read of `hooks.py`.
