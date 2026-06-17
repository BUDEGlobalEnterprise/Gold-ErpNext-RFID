#!/usr/bin/env python3
"""Write focused markdown digests to plan/ and print consolidated+audits to stdout."""
import json, os, textwrap

SRC = "/tmp/claude-1000/-workspace-development/27b6e208-e4f2-40e3-a30a-396b2271c800/tasks/wio3i4xfk.output"
PLAN = "/workspace/development/frappe-bench/apps/zevar_core/plan"

raw = open(SRC, encoding="utf-8").read()
data = json.loads(raw)
result = data.get("result", data)
if isinstance(result, str):
    result = json.loads(result)

research = result.get("research", [])
audits = result.get("audits", [])
consolidated = result.get("consolidated", {})

def bul(items, indent=""):
    return "\n".join(f"{indent}- {x}" for x in items)

# ---------- research digest markdown ----------
rmd = ["# Competitive Research Digest — Jewelry POS Industry Leaders\n",
       f"_{len(research)} vendor/category teardowns. Full structured data: competitive_research_raw.json_\n"]
for r in research:
    rmd.append(f"\n## {r.get('vendor','?')}\n")
    rmd.append(f"- **Category:** {r.get('category','')}  |  **Region:** {r.get('region','')}  |  **Confidence:** {r.get('confidence','')}\n")
    mc = r.get("module_coverage", {})
    for k in ["live_monitoring","sales_monitoring","profit_intelligence","workforce_intelligence","cross_cutting"]:
        vals = mc.get(k, [])
        if vals:
            rmd.append(f"\n### {k.replace('_',' ').title()}\n")
            rmd.append(bul(vals, "  "))
            rmd.append("\n")
    if r.get("kpis"):
        rmd.append("\n### KPIs\n"); rmd.append(bul(r["kpis"], "  ")); rmd.append("\n")
    if r.get("ux_patterns"):
        rmd.append("\n### UX Patterns\n"); rmd.append(bul(r["ux_patterns"], "  ")); rmd.append("\n")
    if r.get("data_model_hints"):
        rmd.append("\n### Data-Model Hints\n"); rmd.append(bul(r["data_model_hints"], "  ")); rmd.append("\n")
    if r.get("differentiators"):
        rmd.append("\n### Differentiators\n"); rmd.append(bul(r["differentiators"], "  ")); rmd.append("\n")
    if r.get("worth_copying"):
        rmd.append("\n### Worth Copying\n"); rmd.append(bul(r["worth_copying"], "  ")); rmd.append("\n")
    if r.get("weaknesses"):
        rmd.append("\n### Weaknesses\n"); rmd.append(bul(r["weaknesses"], "  ")); rmd.append("\n")
    if r.get("sources"):
        rmd.append("\n### Sources\n"); rmd.append(bul(r["sources"], "  ")); rmd.append("\n")
open(PLAN + "/01_research/research_digest.md", "w").write("".join(rmd))
print("wrote research_digest.md")

# ---------- audit digest markdown ----------
amd = ["# Current-State Audit — 4 Zevar Modules\n",
       f"_{len(audits)} module audits (profit-intelligence re-running separately). Full data: module_audit_raw.json_\n"]
for a in audits:
    amd.append(f"\n# {a.get('module','?')}\n")
    amd.append(f"\n**Summary:** {a.get('summary','')}\n\n")
    for label, key in [("Files read","files"),("Endpoints","endpoints"),
                       ("Current capabilities","current_capabilities"),("Strengths","strengths"),
                       ("Gaps","gaps"),("Structural issues","structural_issues"),
                       ("Data model","data_model"),("Tech debt","tech_debt"),
                       ("Recommendations","recommendations")]:
        vals = a.get(key, [])
        if vals:
            amd.append(f"\n## {label}\n\n"); amd.append(bul(vals)); amd.append("\n")
open(PLAN + "/02_current_state_audit/audit_digest.md", "w").write("".join(amd))
print("wrote audit_digest.md")

# ---------- consolidated markdown ----------
c = consolidated
cmd = ["# Consolidated Product Direction\n"]
cmd.append("\n## Combined Vision\n\n" + c.get("combined_vision","").strip() + "\n")
cmd.append("\n## Differentiation Thesis\n\n" + c.get("differentiation_thesis","").strip() + "\n")
bic = c.get("best_in_class", {})
for mod in ["live_monitoring","sales_monitoring","profit_intelligence","workforce_intelligence"]:
    cmd.append(f"\n## Best-in-Class — {mod.replace('_',' ').title()}\n\n")
    cmd.append(bul(bic.get(mod, [])) + "\n")
cmd.append("\n## Strategic Pillars (shared platform)\n\n" + bul(c.get("strategic_pillars",[])) + "\n")
cmd.append("\n## Shared Platform Requirements\n\n" + bul(c.get("shared_platform_requirements",[])) + "\n")
cmd.append("\n## Gap Matrix (current vs best-in-class)\n\n" + bul(c.get("gap_matrix",[])) + "\n")
cmd.append("\n## Quick Wins\n\n" + bul(c.get("quick_wins",[])) + "\n")
open(PLAN + "/00_raw/wf1_consolidated.md", "w").write("".join(cmd))
print("wrote wf1_consolidated.md")

# ---------- print consolidated + audits to stdout (decision-critical) ----------
print("\n" + "#"*90 + "\nCONSOLIDATED (for design)\n" + "#"*90)
print("".join(cmd))
print("\n" + "#"*90 + "\nAUDITS (for design + audit doc)\n" + "#"*90)
for a in audits:
    print(f"\n# {a.get('module','?')}\nSummary: {a.get('summary','')}")
    print("\nGaps:")
    for g in a.get("gaps",[]): print("  -", g)
    print("\nStructural issues:")
    for s in a.get("structural_issues",[]): print("  !", s)
    print("\nRecommendations:")
    for r2 in a.get("recommendations",[]): print("  >", r2)
    print("\nCapabilities/strengths (brief):")
    for s in a.get("strengths",[])[:8]: print("  *", s)
