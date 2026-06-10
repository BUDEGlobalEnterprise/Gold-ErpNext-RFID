"""
Repair Analytics API — Deep analytics, trend analysis, and AI insights
for the Repair Analytics Dashboard (Phase 2).
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import add_days, add_months, cint, flt, getdate, today


@frappe.whitelist(allow_guest=False)
def get_repair_analytics(
	warehouse: str | None = None,
	period: int = 30,
) -> dict[str, Any]:
	"""Master analytics endpoint for the Repair Analytics Dashboard.

	Returns KPIs, trend data, type breakdown, technician leaderboard,
	customer insights, and SLA compliance metrics.
	"""
	frappe.has_permission("Repair Order", ptype="read", throw=True)

	today_date = getdate(today())
	from_date = add_days(today_date, -period)
	prev_from = add_days(from_date, -period)

	wh_cond = ""
	vals: dict[str, Any] = {
		"from_date": str(from_date),
		"to_date": str(today_date),
		"prev_from": str(prev_from),
		"prev_to": str(from_date),
	}
	if warehouse:
		wh_cond = "AND warehouse = %(warehouse)s"
		vals["warehouse"] = warehouse

	result: dict[str, Any] = {}

	# ── KPIs ──
	result["kpis"] = _build_kpis(wh_cond, vals)

	# ── Daily volume trend ──
	result["daily_trend"] = _daily_trend(wh_cond, vals, from_date, today_date)

	# ── Repair type breakdown ──
	result["type_breakdown"] = _type_breakdown(wh_cond, vals)

	# ── Technician leaderboard ──
	result["tech_leaderboard"] = _tech_leaderboard(wh_cond, vals)

	# ── SLA compliance ──
	result["sla"] = _sla_metrics(wh_cond, vals)

	# ── Revenue by month (last 6 months) ──
	result["monthly_revenue"] = _monthly_revenue(wh_cond, vals, today_date)

	# ── Customer return rate ──
	result["customer_insights"] = _customer_insights(wh_cond, vals)

	return result


def _build_kpis(wh_cond: str, vals: dict) -> dict[str, Any]:
	"""Calculate headline KPI cards with period-over-period comparison."""

	# Current period totals
	cur = frappe.db.sql(  # nosemgrep
		f"""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) as completed,
            COALESCE(SUM(total_cost), 0) as revenue,
            COALESCE(AVG(CASE WHEN status = 'Delivered' AND delivered_date IS NOT NULL AND received_date IS NOT NULL
                THEN DATEDIFF(delivered_date, received_date) END), 0) as avg_days
        FROM `tabRepair Order`
        WHERE received_date >= %(from_date)s AND received_date <= %(to_date)s
        {wh_cond}
        """,
		vals,
		as_dict=True,
	)[0]

	# Previous period totals
	prev = frappe.db.sql(  # nosemgrep
		f"""
        SELECT
            COUNT(*) as total,
            COALESCE(SUM(total_cost), 0) as revenue
        FROM `tabRepair Order`
        WHERE received_date >= %(prev_from)s AND received_date < %(from_date)s
        {wh_cond}
        """,
		vals,
		as_dict=True,
	)[0]

	# Active repairs right now
	active = cint(
		frappe.db.sql(  # nosemgrep
			f"""
        SELECT COUNT(*) FROM `tabRepair Order`
        WHERE status NOT IN ('Delivered', 'Cancelled') {wh_cond}
        """,
			vals,
		)[0][0]
	)

	def pct_change(cur_val, prev_val):
		if not prev_val:
			return 0
		return round(((cur_val - prev_val) / prev_val) * 100, 1)

	return {
		"total_repairs": cint(cur.total),
		"total_change_pct": pct_change(cur.total, prev.total),
		"completed": cint(cur.completed),
		"revenue": flt(cur.revenue, 2),
		"revenue_change_pct": pct_change(cur.revenue, prev.revenue),
		"avg_turnaround_days": round(flt(cur.avg_days), 1),
		"active_repairs": active,
	}


def _daily_trend(wh_cond: str, vals: dict, from_date, to_date) -> dict:
	"""Daily repair volume + revenue for sparkline charts."""
	rows = frappe.db.sql(  # nosemgrep
		f"""
        SELECT DATE(received_date) as dt, COUNT(*) as cnt, COALESCE(SUM(total_cost),0) as rev
        FROM `tabRepair Order`
        WHERE received_date >= %(from_date)s AND received_date <= %(to_date)s {wh_cond}
        GROUP BY DATE(received_date) ORDER BY dt
        """,
		vals,
		as_dict=True,
	)
	lookup = {r.dt: r for r in rows}
	labels, counts, revenues = [], [], []
	cur = from_date
	while cur <= to_date:
		labels.append(cur.strftime("%m-%d"))
		r = lookup.get(cur)
		counts.append(r.cnt if r else 0)
		revenues.append(flt(r.rev, 2) if r else 0)
		cur = add_days(cur, 1)

	return {"labels": labels, "counts": counts, "revenues": revenues}


def _type_breakdown(wh_cond: str, vals: dict) -> list[dict]:
	"""Repair volume and revenue grouped by repair type."""
	rows = frappe.db.sql(  # nosemgrep
		f"""
        SELECT repair_type, COUNT(*) as cnt, COALESCE(SUM(total_cost),0) as rev,
               COALESCE(AVG(CASE WHEN status='Delivered' AND delivered_date IS NOT NULL AND received_date IS NOT NULL
                   THEN DATEDIFF(delivered_date, received_date) END),0) as avg_days
        FROM `tabRepair Order`
        WHERE received_date >= %(from_date)s AND received_date <= %(to_date)s {wh_cond}
        GROUP BY repair_type ORDER BY cnt DESC LIMIT 10
        """,
		vals,
		as_dict=True,
	)
	total = sum(r.cnt for r in rows) or 1
	return [
		{
			"type": r.repair_type or "Unspecified",
			"count": r.cnt,
			"pct": round((r.cnt / total) * 100, 1),
			"revenue": flt(r.rev, 2),
			"avg_days": round(flt(r.avg_days), 1),
		}
		for r in rows
	]


def _tech_leaderboard(wh_cond: str, vals: dict) -> list[dict]:
	"""Technician performance ranking."""
	rows = frappe.db.sql(  # nosemgrep
		f"""
        SELECT assigned_to, COUNT(*) as total,
               SUM(CASE WHEN status='Delivered' THEN 1 ELSE 0 END) as completed,
               COALESCE(SUM(total_cost),0) as revenue,
               COALESCE(AVG(CASE WHEN status='Delivered' AND delivered_date IS NOT NULL AND received_date IS NOT NULL
                   THEN DATEDIFF(delivered_date, received_date) END),0) as avg_days
        FROM `tabRepair Order`
        WHERE assigned_to IS NOT NULL AND assigned_to != ''
          AND received_date >= %(from_date)s AND received_date <= %(to_date)s {wh_cond}
        GROUP BY assigned_to ORDER BY completed DESC LIMIT 8
        """,
		vals,
		as_dict=True,
	)
	result = []
	for r in rows:
		name = frappe.db.get_value("User", r.assigned_to, "full_name") or r.assigned_to
		result.append(
			{
				"user": r.assigned_to,
				"name": name,
				"total": r.total,
				"completed": r.completed,
				"revenue": flt(r.revenue, 2),
				"avg_days": round(flt(r.avg_days), 1),
				"completion_rate": round((r.completed / r.total) * 100, 1) if r.total else 0,
			}
		)
	return result


def _sla_metrics(wh_cond: str, vals: dict) -> dict:
	"""SLA / on-time delivery metrics."""
	total_delivered = frappe.db.sql(  # nosemgrep
		f"""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN delivered_date <= promised_date THEN 1 ELSE 0 END) as on_time
        FROM `tabRepair Order`
        WHERE status = 'Delivered' AND promised_date IS NOT NULL
          AND delivered_date IS NOT NULL
          AND received_date >= %(from_date)s AND received_date <= %(to_date)s {wh_cond}
        """,
		vals,
		as_dict=True,
	)[0]

	overdue_now = cint(
		frappe.db.sql(  # nosemgrep
			f"""
        SELECT COUNT(*) FROM `tabRepair Order`
        WHERE status NOT IN ('Delivered','Cancelled')
          AND promised_date IS NOT NULL AND promised_date < CURDATE() {wh_cond}
        """,
			vals,
		)[0][0]
	)

	total = cint(total_delivered.total)
	on_time = cint(total_delivered.on_time)
	return {
		"total_delivered": total,
		"on_time": on_time,
		"on_time_pct": round((on_time / total) * 100, 1) if total else 0,
		"overdue_now": overdue_now,
	}


def _monthly_revenue(wh_cond: str, vals: dict, today_date) -> dict:
	"""Revenue trend by month for last 6 months."""
	six_months_ago = add_months(today_date, -6)
	rows = frappe.db.sql(  # nosemgrep
		f"""
        SELECT DATE_FORMAT(received_date, '%%Y-%%m') as month,
               COUNT(*) as cnt, COALESCE(SUM(total_cost),0) as rev
        FROM `tabRepair Order`
        WHERE received_date >= %(start)s AND received_date <= %(end)s {wh_cond}
        GROUP BY month ORDER BY month
        """,
		{**vals, "start": str(six_months_ago), "end": str(today_date)},
		as_dict=True,
	)
	return {
		"labels": [r.month for r in rows],
		"counts": [r.cnt for r in rows],
		"revenues": [flt(r.rev, 2) for r in rows],
	}


def _customer_insights(wh_cond: str, vals: dict) -> dict:
	"""Customer repeat rate and top customers."""
	repeat = frappe.db.sql(  # nosemgrep
		f"""
        SELECT customer, COUNT(*) as cnt
        FROM `tabRepair Order`
        WHERE received_date >= %(from_date)s AND received_date <= %(to_date)s {wh_cond}
        GROUP BY customer HAVING cnt > 1 ORDER BY cnt DESC LIMIT 5
        """,
		vals,
		as_dict=True,
	)
	total_customers = cint(
		frappe.db.sql(  # nosemgrep
			f"""
        SELECT COUNT(DISTINCT customer) FROM `tabRepair Order`
        WHERE received_date >= %(from_date)s AND received_date <= %(to_date)s {wh_cond}
        """,
			vals,
		)[0][0]
	)

	repeat_customers = len(repeat)
	return {
		"total_customers": total_customers,
		"repeat_customers": repeat_customers,
		"repeat_pct": round((repeat_customers / total_customers) * 100, 1) if total_customers else 0,
		"top_repeat": [
			{
				"customer": r.customer,
				"count": r.cnt,
				"name": frappe.db.get_value("Customer", r.customer, "customer_name") or r.customer,
			}
			for r in repeat[:5]
		],
	}


# ──────────────────────────────────────────────────
# AI Insights (Local Qwen 3.6 Q4)
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_ai_insights(warehouse: str | None = None) -> dict[str, Any]:
	"""Generate AI-powered business insights using the local Qwen model.

	Falls back to rule-based insights if the AI model is unavailable.
	"""
	frappe.only_for(["System Manager", "Accounts Manager", "Store Manager"])

	analytics = get_repair_analytics(warehouse=warehouse, period=30)
	kpis = analytics.get("kpis", {})
	sla = analytics.get("sla", {})
	types = analytics.get("type_breakdown", [])
	techs = analytics.get("tech_leaderboard", [])

	# Build context for AI
	context = _build_ai_context(kpis, sla, types, techs)

	# Try local Qwen model first
	ai_response = _call_local_qwen(context)

	if ai_response:
		return {"source": "qwen", "insights": ai_response, "raw_kpis": kpis}

	# Fallback: rule-based insights
	return {"source": "rules", "insights": _rule_based_insights(kpis, sla, types, techs), "raw_kpis": kpis}


def _build_ai_context(kpis: dict, sla: dict, types: list, techs: list) -> str:
	"""Build a structured context string for the AI model."""
	lines = [
		"You are a jewelry repair business analyst. Provide 3-5 actionable insights.",
		"Keep each insight to 1-2 sentences. Use bullet points. Be specific with numbers.",
		"",
		"=== Repair KPIs (Last 30 Days) ===",
		f"Total repairs: {kpis.get('total_repairs', 0)} ({kpis.get('total_change_pct', 0):+.1f}% vs prior period)",
		f"Revenue: ${kpis.get('revenue', 0):,.2f} ({kpis.get('revenue_change_pct', 0):+.1f}%)",
		f"Avg turnaround: {kpis.get('avg_turnaround_days', 0)} days",
		f"Active repairs: {kpis.get('active_repairs', 0)}",
		"",
		"=== SLA ===",
		f"On-time delivery: {sla.get('on_time_pct', 0)}%",
		f"Currently overdue: {sla.get('overdue_now', 0)}",
		"",
		"=== Top Repair Types ===",
	]
	for t in types[:5]:
		lines.append(f"- {t['type']}: {t['count']} repairs, ${t['revenue']:,.0f} rev, {t['avg_days']}d avg")

	lines.append("")
	lines.append("=== Technician Performance ===")
	for t in techs[:5]:
		lines.append(
			f"- {t['name']}: {t['completed']}/{t['total']} completed, {t['avg_days']}d avg, ${t['revenue']:,.0f}"
		)

	return "\n".join(lines)


def _call_local_qwen(context: str) -> list[str] | None:
	"""Call the local Qwen 3.6 Q4 model via its HTTP API."""
	import json

	import requests

	# Common local LLM endpoints
	endpoints = [
		"http://localhost:11434/api/generate",  # Ollama
		"http://localhost:8080/v1/chat/completions",  # llama.cpp / vLLM
	]

	for url in endpoints:
		try:
			if "ollama" in url or "generate" in url:
				resp = requests.post(
					url,
					json={
						"model": "qwen3:latest",
						"prompt": context,
						"stream": False,
						"options": {"temperature": 0.3, "num_predict": 512},
					},
					timeout=30,
				)
				if resp.status_code == 200:
					data = resp.json()
					text = data.get("response", "")
					return _parse_insights(text)
			else:
				resp = requests.post(
					url,
					json={
						"model": "qwen3",
						"messages": [
							{"role": "system", "content": "You are a jewelry repair business analyst."},
							{"role": "user", "content": context},
						],
						"temperature": 0.3,
						"max_tokens": 512,
					},
					timeout=30,
				)
				if resp.status_code == 200:
					data = resp.json()
					text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
					return _parse_insights(text)
		except Exception:
			continue

	return None


def _parse_insights(text: str) -> list[str]:
	"""Parse AI response into a list of insight strings."""
	if not text:
		return []
	lines = text.strip().split("\n")
	insights = []
	for line in lines:
		cleaned = line.strip().lstrip("-•*123456789. )")
		if cleaned and len(cleaned) > 15:
			insights.append(cleaned)
	return insights[:6]


def _rule_based_insights(kpis: dict, sla: dict, types: list, techs: list) -> list[str]:
	"""Generate rule-based insights as fallback when AI is unavailable."""
	insights = []

	# Revenue trend
	rev_pct = kpis.get("revenue_change_pct", 0)
	if rev_pct > 10:
		insights.append(f"Repair revenue is up {rev_pct}% vs the prior period — strong growth momentum.")
	elif rev_pct < -10:
		insights.append(
			f"Repair revenue declined {abs(rev_pct)}% — consider promotions or outreach campaigns."
		)

	# SLA compliance
	on_time = sla.get("on_time_pct", 0)
	overdue = sla.get("overdue_now", 0)
	if on_time < 80:
		insights.append(
			f"On-time delivery is only {on_time}%. Review scheduling and parts procurement to improve SLA."
		)
	elif on_time >= 95:
		insights.append(f"Excellent SLA at {on_time}% on-time delivery — maintain current processes.")

	if overdue > 5:
		insights.append(
			f"{overdue} repairs are currently overdue. Prioritize these to prevent customer dissatisfaction."
		)

	# Top repair type insight
	if types:
		top = types[0]
		insights.append(
			f"'{top['type']}' is the most common repair ({top['count']} orders, {top['pct']}% of volume)."
		)

	# Technician efficiency
	if techs:
		fastest = min(techs, key=lambda t: t["avg_days"]) if techs else None
		if fastest and fastest["avg_days"] > 0:
			insights.append(
				f"Fastest technician: {fastest['name']} at {fastest['avg_days']} days avg turnaround."
			)

	# Turnaround warning
	avg_days = kpis.get("avg_turnaround_days", 0)
	if avg_days > 7:
		insights.append(
			f"Average turnaround is {avg_days} days — consider adding capacity or streamlining QC."
		)

	return insights[:5] if insights else ["No significant patterns detected in current data."]
