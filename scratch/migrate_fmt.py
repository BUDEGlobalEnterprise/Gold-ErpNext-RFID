#!/usr/bin/env python3
"""Q9: migrate the 10 remaining local fmt() definitions to utils/format.js.

Removes each file's local `function fmt(...)` block (balanced-brace aware, so the
OveragePanel toLocaleString variant is handled too). Then, only if the file still
references fmt(), adds `import { fmt } from '@/utils/format'` after <script>.
RepairsTab defines fmt but never uses it -> def removed, no import.
"""
import pathlib, re

ROOT = pathlib.Path("/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui")
FILES = [
    "src/components/analytics/drawers/CashVarianceDrawer.vue",
    "src/components/analytics/drawers/DetailListDrawer.vue",
    "src/components/analytics/OveragePanel.vue",
    "src/components/analytics/drawers/LayawayDetailDrawer.vue",
    "src/components/reports/DailyBrief.vue",
    "src/pages/reports/RevenueTab.vue",
    "src/pages/reports/InventoryTab.vue",
    "src/pages/reports/CustomersTab.vue",
    "src/pages/reports/FinanceTab.vue",
    "src/pages/reports/RepairsTab.vue",
]


def remove_func(s, sig="function fmt("):
	i = s.find(sig)
	if i < 0:
		return s, False
	op = s.find("{", i)
	if op < 0:
		return s, False
	depth, j, in_str, q = 0, op, False, None
	while j < len(s):
		ch = s[j]
		if in_str:
			if ch == q:
				in_str = False
		elif ch in ("'", '"', "`"):
			in_str, q = True, ch
		elif ch == "{":
			depth += 1
		elif ch == "}":
			depth -= 1
			if depth == 0:
				break
		j += 1
	end = j + 1
	# swallow one trailing newline + collapse a leftover blank line
	if end < len(s) and s[end] == "\n":
		end += 1
	chunk = s[i:end]
	# drop a single immediately-preceding blank line if present
	if i >= 1 and s[i - 1] == "\n" and (i >= 2 and s[i - 2] == "\n"):
		i -= 1
	return s[:i] + s[end:], True


for rel in FILES:
	p = ROOT / rel
	s = p.read_text()
	s2, removed = remove_func(s)
	if not removed:
		print(f"WARN  {rel}: no fmt def found")
		continue
	# collapse 3+ consecutive newlines to 2 (cosmetic, avoids eslint no-multiple-empty-lines)
	s2 = re.sub(r"\n{3,}", "\n\n", s2)
	needs = re.search(r"\bfmt\(", s2) is not None
	has_import = "@/utils/format" in s2
	import_added = False
	if needs and not has_import:
		new, n = re.subn(r"(<script[^>]*>\n)", r"\1import { fmt } from '@/utils/format'\n", s2, count=1)
		if n:
			s2 = new
			import_added = True
	p.write_text(s2)
	print(f"OK    {rel}: removed_def  import={'added' if import_added else ('present' if has_import else 'not needed')}")
