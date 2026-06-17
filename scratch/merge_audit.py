#!/usr/bin/env python3
"""Build a complete, authoritative current-state audit report (4 WF1 audits
+ the corrected profit audit) into 02_current_state_audit/CURRENT_STATE_AUDIT.md."""
import json, os

PLAN = "/workspace/development/frappe-bench/apps/zevar_core/plan"
ORDER = [
    ("profit_intelligence", "Profit Intelligence", PLAN + "/02_current_state_audit/profit_intelligence_audit.json"),
    ("live_monitor", "Live Monitor", None),
    ("sales_monitor", "Sales Monitor", None),
    ("workforce_intelligence", "Workforce Intelligence", None),
    ("cross_cutting", "Cross-cutting Architecture", None),
]

# load the 4 WF1 audits
raw = json.load(open(PLAN + "/02_current_state_audit/module_audit_raw.json"))
def norm(m):
    m = (m or "").lower()
    if "profit" in m: return "profit_intelligence"
    if "live" in m: return "live_monitor"
    if "sales" in m: return "sales_monitor"
    if "workforce" in m or "performance" in m: return "workforce_intelligence"
    if "cross" in m: return "cross_cutting"
    return "other"
by_key = {}
for a in raw:
    by_key.setdefault(norm(a.get("module")), a)

def bul(items):
    return "\n".join(f"- {x}" for x in items) if items else "_(none)_"

out = ["# Zevar Monitor Suite — Current-State Audit\n",
       "> Authoritative baseline for the 4 monitoring modules + cross-cutting architecture. ",
       "> Grounded in direct code reads with file:line references. ",
       "> **Note:** the Profit Intelligence audit below CORRECTS an earlier rate-limited pass that falsely claimed the `calculate_sale_cost_breakdown` hook is wired and that margin math is centralized — both are false (see Profit section).\n"]

for key, label, override in ORDER:
    a = json.load(open(override)) if override and os.path.exists(override) else by_key.get(key)
    if not a:
        continue
    out.append(f"\n---\n\n# {label}\n")
    out.append(f"\n**Summary:** {a.get('summary','')}\n\n")
    for h, fkey in [("Files read", "files"), ("Endpoints", "endpoints"),
                    ("Current capabilities", "current_capabilities"), ("Strengths", "strengths"),
                    ("Gaps", "gaps"), ("Structural issues", "structural_issues"),
                    ("Data model", "data_model"), ("Tech debt", "tech_debt"),
                    ("Recommendations", "recommendations")]:
        vals = a.get(fkey, [])
        if vals:
            out.append(f"\n## {h}\n\n")
            if fkey in ("files", "endpoints"):
                out.append("\n".join(f"- `{x}`" for x in vals))
            else:
                out.append(bul(vals))
            out.append("\n")
    if isinstance(a.get("math_integrity"), dict):
        mi = a["math_integrity"]
        out.append("\n## Margin Math Integrity (Profit)\n\n")
        out.append(f"**Canonical:** {mi.get('canonical_definition','')}\n\n")
        out.append(f"**Net assessment:** {mi.get('net_assessment','')}\n\n")
        out.append("**Inconsistent sites:**\n\n")
        for s in mi.get("inconsistent_sites", []):
            out.append(f"- `{s.get('where','')}` — {s.get('formula','')} — missing: {s.get('buckets_missing','')} — **impact:** {s.get('impact','')}\n")

dest = PLAN + "/02_current_state_audit/CURRENT_STATE_AUDIT.md"
open(dest, "w").write("".join(out))
print("wrote", dest, "(", round(os.path.getsize(dest)/1024,1), "KB )")
print("modules:", [k for k, _, _ in ORDER if (os.path.exists(ORDER[[x[0] for x in ORDER].index(k)][2]) if k=='profit_intelligence' else (k in by_key))])
