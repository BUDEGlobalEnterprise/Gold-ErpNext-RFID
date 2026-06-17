#!/usr/bin/env python3
"""Build the combined args payload for Workflow 2 (design + roadmap).
Usage: build_args.py [path_to_profit_audit_json]
Reads WF1 output; optionally merges a separately-run profit audit."""
import json, os, sys

SRC = "/tmp/claude-1000/-workspace-development/27b6e208-e4f2-40e3-a30a-396b2271c800/tasks/wio3i4xfk.output"
PLAN = "/workspace/development/frappe-bench/apps/zevar_core/plan"

data = json.loads(open(SRC).read())
result = data.get("result", data)
if isinstance(result, str):
    result = json.loads(result)

consolidated = result.get("consolidated", {})
research = result.get("research", [])
audits = result.get("audits", [])

# compact research (drop long narrative, keep decision-relevant lists)
research_compact = []
for r in research:
    research_compact.append({
        "vendor": r.get("vendor"),
        "category": r.get("category"),
        "region": r.get("region"),
        "module_coverage": r.get("module_coverage", {}),
        "kpis": r.get("kpis", []),
        "ux_patterns": r.get("ux_patterns", []),
        "data_model_hints": r.get("data_model_hints", []),
        "differentiators": r.get("differentiators", []),
        "worth_copying": r.get("worth_copying", []),
        "weaknesses": r.get("weaknesses", []),
        "sources": r.get("sources", [])[:12],
        "confidence": r.get("confidence"),
    })

# key audits by module
def norm(m):
    m = (m or "").lower()
    if "live" in m: return "live_monitor"
    if "sales" in m: return "sales_monitor"
    if "profit" in m: return "profit_intelligence"
    if "workforce" in m or "performance" in m: return "workforce_intelligence"
    if "cross" in m: return "cross_cutting"
    return "other"

audits_by_key = {}
for a in audits:
    k = norm(a.get("module"))
    audits_by_key.setdefault(k, []).append(a)
audits_by_key = {k: v[0] for k, v in audits_by_key.items() if v}

# optionally merge profit audit from a separate file
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    raw = open(sys.argv[1]).read()
    # the file may be the agent's final text (JSON) or wrapped
    try:
        pa = json.loads(raw)
    except Exception:
        i, j = raw.find("{"), raw.rfind("}")
        pa = json.loads(raw[i:j+1])
    # if wrapped in {result: ...} or {output: ...}
    for wrap in ("result", "output", "final_message"):
        if isinstance(pa, dict) and wrap in pa and isinstance(pa[wrap], str):
            try:
                pa = json.loads(pa[wrap])
            except Exception:
                pass
    if isinstance(pa, dict):
        audits_by_key["profit_intelligence"] = pa
        print("MERGED profit audit from", sys.argv[1])
    else:
        print("WARN: profit audit file did not parse to a JSON object")

critical_corrections = [
    "PROFIT (CORRECTS the earlier failed audit, which misled the consolidation): calculate_sale_cost_breakdown is NOT registered in hooks.py doc_events for Sales Invoice on_submit/on_cancel — Sale Cost Breakdown records are never auto-created, so get_profit_summary/get_margin_analysis/get_margin_heatmap/get_cost_component_trends ALL return zero in a live system. This is a P0 and is the profit-module equivalent of the workforce wiring bug. ALSO: generate_pricing_recommendations is NOT scheduled (Pricing tab permanently empty); 4 frontend/backend contracts are broken (create_recommendation endpoint does not exist -> 404; review_recommendation expects lowercase 'approve'/'reject' but UI sends 'Approved'/'Rejected'; get_margin_heatmap returns a flat array but the UI expects a pivoted shape; confidence_level is a High/Med/Low string but the UI treats it as a numeric %). MARGIN is defined 7 INCONSISTENT ways across the repo (commission.py pays real commissions on a 1-bucket valuation_rate margin that ignores gemstone/labor/commission/payment/overhead — financial impact). COGS model lacks making charge, alloy/wastage, and labor_burden_percent (field exists, unused). Cost Center Allocation is a singleton (no per-store). The consolidated best_in_class is still valid as a target, but treat any prior 'hook is wired / margin centralized' statement as FALSE.",
    "WORKFORCE: log_sale_event and log_sale_cancel_event are NOT registered in hooks.py on_submit/on_cancel for Sales Invoice — 'Sale Completed' / 'Return Processed' Performance Logs are never created, so the revenue scorecard axis (default 50% weight) is always 0 in every scoreboard, comp calculation, and quarterly review. Payroll-affecting P0.",
    "LIVE: publish_anomaly_alert is DEAD CODE (defined live_monitor.py:37, never called) and anomaly detection has NO scheduler entry; publish_employee_event is never invoked from the pos.py sale path; AdminMonitor polls every 30s instead of subscribing to pos_sale_event (which IS published); all live_monitor.py publish_realtime calls (lines 30/39/55) omit user=/room= so employee-attributed events broadcast to every socket; _get_store_metrics SKIPS zero-repair stores (quiet stores vanish from the wall).",
]

args = {
    "consolidated": consolidated,
    "audits": audits_by_key,
    "research_compact": research_compact,
    "critical_corrections": critical_corrections,
}
out = PLAN + "/00_raw/wf2_args.json"
json.dump(args, open(out, "w"), indent=2)
print("wrote", out)
print("audit keys present:", sorted(audits_by_key.keys()))
print("research_compact vendors:", len(research_compact))
print("payload size (KB):", round(os.path.getsize(out)/1024, 1))
