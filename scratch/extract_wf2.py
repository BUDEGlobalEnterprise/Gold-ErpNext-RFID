#!/usr/bin/env python3
"""Extract WF2 (platform + 4 designs + roadmap) into plan/03_target_design and plan/04_roadmap."""
import json, os

SRC = "/tmp/claude-1000/-workspace-development/27b6e208-e4f2-40e3-a30a-396b2271c800/tasks/wu6dow49k.output"
PLAN = "/workspace/development/frappe-bench/apps/zevar_core/plan"

data = json.loads(open(SRC).read())
result = data.get("result", data)
if isinstance(result, str):
    result = json.loads(result)

platform = result.get("platform") or {}
designs = result.get("designs") or []
roadmap = result.get("roadmap") or {}

os.makedirs(PLAN + "/03_target_design", exist_ok=True)
os.makedirs(PLAN + "/04_roadmap", exist_ok=True)

written = []

# platform
if platform.get("markdown"):
    p = PLAN + "/03_target_design/00_SHARED_PLATFORM.md"
    open(p, "w").write(platform["markdown"])
    written.append(("00_SHARED_PLATFORM.md", len(platform["markdown"]), platform.get("title", "")))

# designs — map by keyword
def slot(title):
    t = (title or "").lower()
    if "workforce" in t: return "04_WORKFORCE_INTELLIGENCE.md"
    if "profit" in t: return "03_PROFIT_INTELLIGENCE.md"
    if "sales" in t: return "02_SALES_MONITOR.md"
    if "live" in t: return "01_LIVE_MONITOR.md"
    return None

for d in designs:
    s = slot(d.get("title"))
    if s and d.get("markdown"):
        open(PLAN + "/03_target_design/" + s, "w").write(d["markdown"])
        written.append((s, len(d["markdown"]), d.get("title", "")))

# roadmap
if roadmap.get("markdown"):
    r = PLAN + "/04_roadmap/IMPLEMENTATION_ROADMAP.md"
    open(r, "w").write(roadmap["markdown"])
    written.append(("04_roadmap/IMPLEMENTATION_ROADMAP.md", len(roadmap["markdown"]), roadmap.get("title", "")))

print("platform:", bool(platform.get("markdown")), "| designs:", len(designs), "| roadmap:", bool(roadmap.get("markdown")))
print(f"\n{'file':<50} {'chars':>8}  title")
for f, n, t in written:
    print(f"{f:<50} {n:>8}  {t[:60]}")
