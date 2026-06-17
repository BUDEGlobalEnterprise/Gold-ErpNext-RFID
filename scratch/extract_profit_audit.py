#!/usr/bin/env python3
"""Extract the profit-intelligence audit JSON from the agent JSONL transcript.
Parses each JSONL line, walks decoded string values, finds the assistant message
containing the audit, then pulls the ```json block (operating on DECODED text so
quotes/backticks are real). Keeps the transcript out of context."""
import json, re, os

SRC = "/tmp/claude-1000/-workspace-development/27b6e208-e4f2-40e3-a30a-396b2271c800/tasks/ac8b63340ef30a91e.output"
OUT = "/workspace/development/frappe-bench/apps/zevar_core/plan/02_current_state_audit/profit_intelligence_audit.json"

raw = open(SRC, encoding="utf-8").read()

def walk_strings(x, out):
    if isinstance(x, str):
        out.append(x)
    elif isinstance(x, dict):
        for v in x.values():
            walk_strings(v, out)
    elif isinstance(x, list):
        for v in x:
            walk_strings(v, out)

candidates = []
for ln in raw.splitlines():
    ln = ln.strip()
    if not ln:
        continue
    try:
        obj = json.loads(ln)
    except Exception:
        continue
    texts = []
    walk_strings(obj, texts)
    for t in texts:
        if "math_integrity" in t and "Profit Intelligence" in t and '"module"' in t:
            candidates.append(t)

if not candidates:
    raise SystemExit("ERROR: no candidate assistant message found containing the profit audit")

# longest candidate == most complete
text = max(candidates, key=len)
print("candidate text length:", len(text))

js = None
m = re.search(r"```json\s*(.*?)```", text, re.S)
if m:
    js = m.group(1).strip()
else:
    # balanced brace extraction on decoded text (real quotes)
    start = text.find("{")
    depth, in_str, esc, i = 0, False, False, start
    while i < len(text):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    js = text[start:i+1]
                    break
        i += 1

if not js:
    raise SystemExit("ERROR: could not isolate JSON object")

obj = json.loads(js)
json.dump(obj, open(OUT, "w"), indent=2)
print("saved:", OUT)
print("module:", obj.get("module"))
print("keys:", list(obj.keys()))
print("gaps:", len(obj.get("gaps", [])), "| structural:", len(obj.get("structural_issues", [])), "| recs:", len(obj.get("recommendations", [])))
mi = obj.get("math_integrity", {})
print("inconsistent margin sites:", len(mi.get("inconsistent_sites", [])))
print("size KB:", round(os.path.getsize(OUT)/1024, 1))
