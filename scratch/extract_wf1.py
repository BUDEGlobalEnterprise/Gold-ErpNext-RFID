#!/usr/bin/env python3
"""Extract digest + artifacts from Workflow 1 raw output."""
import json, os

SRC = "/tmp/claude-1000/-workspace-development/27b6e208-e4f2-40e3-a30a-396b2271c800/tasks/wio3i4xfk.output"
PLAN = "/workspace/development/frappe-bench/apps/zevar_core/plan"

raw = open(SRC, encoding="utf-8").read()
try:
    data = json.loads(raw)
except Exception:
    i, j = raw.find("{"), raw.rfind("}")
    data = json.loads(raw[i:j+1])

# output wrapper: {summary, agentCount, logs, result}
result = data.get("result", data)
if isinstance(result, str):
    try:
        result = json.loads(result)
    except Exception:
        i, j = result.find("{"), result.rfind("}")
        result = json.loads(result[i:j+1])

research = result.get("research", [])
audits = result.get("audits", [])
consolidated = result.get("consolidated", {})

print("== TOP LEVEL ==", list(data.keys()))
print("research:", len(research), " audits:", len(audits), " consolidated keys:", list(consolidated.keys()))

os.makedirs(PLAN + "/00_raw", exist_ok=True)
with open(PLAN + "/00_raw/wf1_consolidated.json", "w") as f:
    json.dump(consolidated, f, indent=2)
with open(PLAN + "/01_research/competitive_research_raw.json", "w") as f:
    json.dump(research, f, indent=2)
with open(PLAN + "/02_current_state_audit/module_audit_raw.json", "w") as f:
    json.dump(audits, f, indent=2)
print("saved raw artifacts to plan/{00_raw,01_research,02_current_state_audit}/")

print("\n" + "="*80 + "\n== RESEARCH VENDORS ==")
for r in research:
    print(f"\n### {r.get('vendor','?')}")
    print(f"   category: {r.get('category','')} | region: {r.get('region','')} | confidence: {r.get('confidence','')}")
    print("   worth_copying:")
    for w in r.get("worth_copying", [])[:8]:
        print("     -", w)
    print("   differentiators:")
    for d in r.get("differentiators", [])[:5]:
        print("     -", d)

print("\n" + "="*80 + "\n== AUDITS (current state) ==")
for a in audits:
    print(f"\n### {a.get('module','?')}")
    print("summary:", a.get("summary", ""))
    print("current_capabilities:")
    for c in a.get("current_capabilities", []):
        print("  +", c)
    print("strengths:")
    for s in a.get("strengths", []):
        print("  *", s)
    print("gaps:")
    for g in a.get("gaps", []):
        print("  -", g)
    print("structural_issues:")
    for s in a.get("structural_issues", []):
        print("  !", s)
    print("recommendations:")
    for r2 in a.get("recommendations", []):
        print("  >", r2)

print("\n" + "="*80 + "\n== CONSOLIDATED ==")
bic = consolidated.get("best_in_class", {})
for mod in ["live_monitoring", "sales_monitoring", "profit_intelligence", "workforce_intelligence"]:
    print(f"\n--- best_in_class.{mod} ---")
    for p in bic.get(mod, []):
        print("  *", p)

print("\n--- combined_vision ---\n", consolidated.get("combined_vision", ""))
print("\n--- differentiation_thesis ---\n", consolidated.get("differentiation_thesis", ""))

print("\n--- strategic_pillars ---")
for p in consolidated.get("strategic_pillars", []):
    print("  -", p)
print("\n--- shared_platform_requirements ---")
for p in consolidated.get("shared_platform_requirements", []):
    print("  -", p)
print("\n--- gap_matrix ---")
for p in consolidated.get("gap_matrix", []):
    print("  -", p)
print("\n--- quick_wins ---")
for p in consolidated.get("quick_wins", []):
    print("  -", p)
