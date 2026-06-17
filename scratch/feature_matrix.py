#!/usr/bin/env python3
"""Generate 01_research/FEATURE_MATRIX.md — vendor x module competitive matrix."""
import json, os

PLAN = "/workspace/development/frappe-bench/apps/zevar_core/plan"
research = json.load(open(PLAN + "/01_research/competitive_research_raw.json"))
consolidated = json.load(open(PLAN + "/00_raw/wf1_consolidated.json"))

MODS = [("live_monitoring", "Live"), ("sales_monitoring", "Sales"),
        ("profit_intelligence", "Profit"), ("workforce_intelligence", "Workforce"),
        ("cross_cutting", "Platform")]

def short(name):
    name = name.replace(" (by Achieve IT Solutions / Aquifer; marketed as \"The Edge for Jewelers\" at theedgeforjewelers.com)", "")
    return name.split(" — ")[0].split(" / ")[0][:42]

rows = []
for r in research:
    mc = r.get("module_coverage", {})
    counts = {k: len(mc.get(k, [])) for k, _ in MODS}
    flagship = (r.get("worth_copying") or [""])[0]
    rows.append((short(r.get("vendor", "?")), r.get("category", "").split(" (")[0][:36],
                 counts, flagship[:90]))

hdr = "| Vendor | Category | " + " | ".join(m for _, m in MODS) + " | Flagship takeaway |"
sep = "|" + "---|" * (2 + len(MODS) + 1)
lines = ["# Competitive Feature Matrix — Jewelry POS Leaders\n",
         "Cell value = number of distinct features mapped to that module in the teardown ",
         "(depth indicator). Full detail per vendor: `research_digest.md` / `competitive_research_raw.json`.\n",
         "", hdr, sep]
for name, cat, counts, flag in sorted(rows, key=lambda x: -sum(x[2].values())):
    cells = " | ".join(str(counts[k]) for k, _ in MODS)
    lines.append(f"| {name} | {cat} | {cells} | {flag} |")

# best-in-class synthesis pointer
lines.append("\n---\n\n## Best-in-Class Synthesis (per module)\n")
lines.append("The consolidated **best-in-class target** for each module (the refined superset we will build) is in `../00_raw/wf1_consolidated.md` under “Best-in-Class — <Module>”. Summary counts:\n")
bic = consolidated.get("best_in_class", {})
lines.append("\n| Module | Target features (best-in-class count) |")
lines.append("|---|---|")
for k, m in [("live_monitoring","Live Monitor"),("sales_monitoring","Sales Monitor"),
             ("profit_intelligence","Profit Intelligence"),("workforce_intelligence","Workforce Intelligence")]:
    lines.append(f"| {m} | {len(bic.get(k, []))} |")

lines.append("\n## Sources\n")
allsrc = set()
for r in research:
    for s in r.get("sources", []):
        allsrc.add(s)
lines.append(f"{len(allsrc)} unique source URLs captured across teardowns (see `research_digest.md` per vendor).\n")

dest = PLAN + "/01_research/FEATURE_MATRIX.md"
open(dest, "w").write("\n".join(lines))
print("wrote", dest, "(", round(os.path.getsize(dest)/1024,1), "KB )")
print("vendors:", len(rows), "| sources:", len(allsrc))
