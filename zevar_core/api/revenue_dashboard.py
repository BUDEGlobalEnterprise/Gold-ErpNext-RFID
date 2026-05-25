"""
Revenue Dashboard API — Today's sales, hourly distribution,
category breakdown, and top salesperson rankings.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_days


# ---------------------------------------------------------------------------
# Aggregated snapshot (single call for the whole page)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_dashboard_data():
	"""Single-call payload for the Revenue Dashboard page."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Sales User", "Accounts Manager"]
	)
	today = nowdate()
	return {
		"summary": _get_today_summary(today),
		"hourly": _get_hourly_distribution(today),
		"categories": _get_category_breakdown(today),
		"top_salespersons": _get_top_salespersons(today),
	}


# ---------------------------------------------------------------------------
# Individual widget endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_today_summary():
	"""Today's sales total, transaction count, avg ticket, YoY change."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Sales User", "Accounts Manager"]
	)
	return _get_today_summary(nowdate())


@frappe.whitelist()
def get_hourly_distribution():
	"""Hourly sales distribution for today (9 AM – 8 PM)."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Sales User", "Accounts Manager"]
	)
	return _get_hourly_distribution(nowdate())


@frappe.whitelist()
def get_category_breakdown():
	"""Revenue breakdown by item jewelry_type category."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Sales User", "Accounts Manager"]
	)
	return _get_category_breakdown(nowdate())


@frappe.whitelist()
def get_top_salespersons():
	"""Top salespersons ranked by today's revenue."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Sales User", "Accounts Manager"]
	)
	return _get_top_salespersons(nowdate())


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _get_today_summary(today):
	"""Today's total sales, txn count, avg ticket, and YoY percentage."""
	si = frappe.qb.DocType("Sales Invoice")

	row = (
		frappe.qb.from_(si)
		.select(
			frappe.qb.fn.Coalesce(frappe.qb.fn.Sum(si.base_grand_total), 0).as_("total_sales"),
			frappe.qb.fn.Count(si.name).as_("txn_count"),
		)
		.where((si.docstatus == 1) & (si.is_pos == 1) & (si.posting_date == today))
	).run(as_dict=True)

	r = row[0] if row else {}
	total = flt(r.get("total_sales"))
	count = cint(r.get("txn_count"))
	avg_ticket = (total / count) if count else 0

	# YoY: same date last year
	last_year = add_days(today, -365)
	si2 = frappe.qb.DocType("Sales Invoice")
	ly_row = (
		frappe.qb.from_(si2)
		.select(frappe.qb.fn.Coalesce(frappe.qb.fn.Sum(si2.base_grand_total), 0).as_("total_sales"))
		.where((si2.docstatus == 1) & (si2.is_pos == 1) & (si2.posting_date == last_year))
	).run(as_dict=True)

	ly_total = flt(ly_row[0].total_sales) if ly_row else 0
	yoy_pct = ((total - ly_total) / ly_total * 100) if ly_total else 0

	return {
		"today_sales": total,
		"txn_count": count,
		"avg_ticket": flt(avg_ticket, 2),
		"yoy_pct": flt(yoy_pct, 1),
	}


def _get_hourly_distribution(today):
	"""Hourly sales from 9 AM to 8 PM for bar chart."""
	rows = frappe.db.sql(
		"""SELECT
			HOUR(posting_time) AS hour,
			COALESCE(SUM(base_grand_total), 0) AS total
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s
		AND posting_time IS NOT NULL
		GROUP BY hour
		ORDER BY hour""",
		(today,),
		as_dict=True,
	)

	hour_map = {r.hour: flt(r.total) for r in rows}
	result = []
	max_val = max(hour_map.values()) if hour_map else 1
	max_val = max_val or 1

	for h in range(9, 21):
		total = hour_map.get(h, 0)
		result.append({
			"hour": h,
			"label": _format_hour(h),
			"total": flt(total),
			"height": flt(total / max_val * 100, 1) if max_val else 0,
		})

	return result


def _get_category_breakdown(today):
	"""Revenue by item's custom_jewelry_type."""
	rows = frappe.db.sql(
		"""SELECT
			COALESCE(i.custom_jewelry_type, 'Other') AS category,
			SUM(sii.base_net_amount) AS total
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		JOIN `tabItem` i ON i.name = sii.item_code
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND si.posting_date = %s
		GROUP BY category
		ORDER BY total DESC""",
		(today,),
		as_dict=True,
	)

	grand = sum(flt(r.total) for r in rows) or 1
	for r in rows:
		r["pct"] = flt(flt(r.total) / grand * 100, 1)
		r["total"] = flt(r.total)

	return rows


def _get_top_salespersons(today):
	"""Top 5 salespersons by revenue via commission splits."""
	rows = frappe.db.sql(
		"""SELECT
			emp.employee_name AS name,
			emp.name AS employee_id,
			SUM(scs.commission_amount) AS commission,
			SUM(scs.allocated_amount) AS total
		FROM `tabSales Commission Split` scs
		JOIN `tabEmployee` emp ON scs.employee = emp.name
		JOIN `tabSales Invoice` si ON scs.sales_invoice = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND si.posting_date = %s
		GROUP BY scs.employee
		ORDER BY total DESC
		LIMIT 5""",
		(today,),
		as_dict=True,
	)

	for r in rows:
		r["total"] = flt(r.total)

	return rows


def _format_hour(h):
	"""Convert 24h to 12h label."""
	if h == 0:
		return "12a"
	if h < 12:
		return f"{h}"
	if h == 12:
		return "12p"
	return f"{h}"


def cint(v):
	try:
		return int(v or 0)
	except (ValueError, TypeError):
		return 0
