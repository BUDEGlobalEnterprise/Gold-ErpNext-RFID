"""
Customer Dashboard API — LTV distribution, new vs returning analysis,
layaway cohort retention, and top customer rankings.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, add_months, add_days


@frappe.whitelist()
def get_dashboard_data():
	"""Single-call payload for the Customer Dashboard page."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]
	)
	today = nowdate()
	return {
		"kpi": _get_kpi_summary(today),
		"new_vs_returning": _get_new_vs_returning(today),
		"top_customers": _get_top_customers(today),
		"layaway_cohort": _get_layaway_cohort(today),
	}


@frappe.whitelist()
def get_kpi_summary():
	"""Total customers, new this month, avg LTV, active layaways."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]
	)
	return _get_kpi_summary(nowdate())


@frappe.whitelist()
def get_new_vs_returning():
	"""New vs returning customers for the last 6 months."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]
	)
	return _get_new_vs_returning(nowdate())


@frappe.whitelist()
def get_top_customers():
	"""Top 10 customers by revenue (last 12 months)."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]
	)
	return _get_top_customers(nowdate())


@frappe.whitelist()
def get_layaway_cohort():
	"""Layaway completion rate by month of origination (6 months)."""
	frappe.only_for(
		["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]
	)
	return _get_layaway_cohort(nowdate())


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _get_kpi_summary(today):
	"""Aggregate customer KPIs."""
	# Total active customers (not disabled)
	total_customers = frappe.db.count("Customer", filters={"disabled": 0})

	# New this month
	month_start = getdate(today).replace(day=1)
	new_customers = frappe.db.count(
		"Customer",
		filters=[["disabled", "=", 0], ["creation", ">=", month_start]],
	)

	# Average LTV: total POS revenue / total customers
	revenue_row = frappe.db.sql(
		"""SELECT COALESCE(SUM(base_grand_total), 0) AS total
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1""",
		as_dict=True,
	)
	total_revenue = flt(revenue_row[0].total) if revenue_row else 0
	avg_ltv = (total_revenue / total_customers) if total_customers else 0

	# Active layaways
	active_layaways = frappe.db.sql(
		"""SELECT COUNT(*) AS cnt
		FROM `tabSales Invoice`
		WHERE docstatus < 2
		AND custom_transaction_stream = 'Layaway Deposit'
		AND status NOT IN ('Paid', 'Cancelled', 'Return')""",
		as_dict=True,
	)
	layaway_count = active_layaways[0].cnt if active_layaways else 0

	# Returning customers (placed >1 order in last 12 months)
	returning = frappe.db.sql(
		"""SELECT COUNT(*) AS cnt FROM (
			SELECT si.customer
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1 AND si.is_pos = 1
			AND si.posting_date >= DATE_SUB(%s, INTERVAL 12 MONTH)
			GROUP BY si.customer
			HAVING COUNT(si.name) > 1
		) sub""",
		(today,),
		as_dict=True,
	)
	returning_count = returning[0].cnt if returning else 0

	return {
		"total_customers": total_customers,
		"new_customers": new_customers,
		"avg_ltv": flt(avg_ltv, 2),
		"active_layaways": layaway_count,
		"returning": returning_count,
	}


def _get_new_vs_returning(today):
	"""New vs returning breakdown for the current month."""
	month_start = getdate(today).replace(day=1)

	new = frappe.db.sql(
		"""SELECT COUNT(DISTINCT si.customer) AS cnt
		FROM `tabSales Invoice` si
		JOIN `tabCustomer` c ON c.name = si.customer
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date >= %s
		AND c.creation >= %s""",
		(month_start, month_start),
		as_dict=True,
	)

	returning = frappe.db.sql(
		"""SELECT COUNT(DISTINCT si.customer) AS cnt
		FROM `tabSales Invoice` si
		JOIN `tabCustomer` c ON c.name = si.customer
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date >= %s
		AND c.creation < %s""",
		(month_start, month_start),
		as_dict=True,
	)

	return {
		"new": new[0].cnt if new else 0,
		"returning": returning[0].cnt if returning else 0,
	}


def _get_top_customers(today):
	"""Top 10 customers by revenue in last 12 months."""
	rows = frappe.db.sql(
		"""SELECT
			c.customer_name AS name,
			c.name AS customer_id,
			SUM(si.base_grand_total) AS total,
			COUNT(si.name) AS order_count
		FROM `tabSales Invoice` si
		JOIN `tabCustomer` c ON c.name = si.customer
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date >= DATE_SUB(%s, INTERVAL 12 MONTH)
		GROUP BY si.customer
		ORDER BY total DESC
		LIMIT 10""",
		(today,),
		as_dict=True,
	)

	for r in rows:
		r["total"] = flt(r.total)

	return rows


def _get_layaway_cohort(today):
	"""Layaway completion rate by month of origination for last 6 months."""
	rows = frappe.db.sql(
		"""SELECT
			DATE_FORMAT(la.creation, '%%b') AS label,
			DATE_FORMAT(la.creation, '%%Y-%%m') AS sort_key,
			COUNT(*) AS total,
			SUM(CASE WHEN la.status IN ('Completed', 'Paid', 'Delivered') THEN 1 ELSE 0 END) AS completed
		FROM `tabLayaway` la
		WHERE la.creation >= DATE_SUB(%s, INTERVAL 6 MONTH)
		GROUP BY sort_key, label
		ORDER BY sort_key""",
		(today,),
		as_dict=True,
	)

	max_rate = 0
	for r in rows:
		total = r.total or 1
		rate = (r.completed or 0) / total * 100
		r["rate"] = flt(rate, 1)
		max_rate = max(max_rate, rate)

	for r in rows:
		r["height"] = flt(r.rate / max_rate * 100, 1) if max_rate else 0

	# Fill missing months
	month_labels = []
	for i in range(5, -1, -1):
		dt = add_months(getdate(today), -i)
		month_labels.append({"label": dt.strftime("%b"), "sort_key": dt.strftime("%Y-%m")})

	result_map = {r.sort_key: r for r in rows}
	result = []
	for m in month_labels:
		if m["sort_key"] in result_map:
			result.append(result_map[m["sort_key"]])
		else:
			result.append({"label": m["label"], "total": 0, "completed": 0, "rate": 0, "height": 0})

	return result
