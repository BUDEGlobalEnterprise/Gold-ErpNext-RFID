# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0


import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""
	Execute the Gold Rate History Report.

	Returns gold rate history with trends and analysis.
	"""
	columns = [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "time",
			"label": _("Time"),
			"fieldtype": "Time",
			"width": 80,
		},
		{
			"fieldname": "metal",
			"label": _("Metal"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "purity",
			"label": _("Purity"),
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"fieldname": "rate_per_gram",
			"label": _("Rate/g"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "rate_change",
			"label": _("Change"),
			"fieldtype": "Currency",
			"width": 80,
		},
		{
			"fieldname": "change_percent",
			"label": _("Change %"),
			"fieldtype": "Percent",
			"width": 80,
		},
		{
			"fieldname": "trend",
			"label": _("Trend"),
			"fieldtype": "Data",
			"width": 60,
		},
		{
			"fieldname": "source",
			"label": _("Source"),
			"fieldtype": "Data",
			"width": 100,
		},
	]

	data = []

	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	metal = filters.get("metal")
	purity = filters.get("purity")

	if not from_date:
		from_date = frappe.utils.add_days(frappe.utils.today(), -30)
	if not to_date:
		to_date = frappe.utils.today()

	# Build filters
	query_filters = {"date": ["between", [from_date, to_date]]}
	if metal:
		query_filters["metal"] = metal
	if purity:
		query_filters["purity"] = purity

	# Get gold rate history
	rates = frappe.get_all(
		"Gold Rate Log",
		filters=query_filters,
		fields=["date", "time", "metal", "purity", "rate_per_gram", "source"],
		order_by="date desc, time desc",
	)

	# Track previous rate for change calculation
	prev_rates = {}

	for rate in rates:
		key = f"{rate.metal}_{rate.purity}"
		rate_per_gram = flt(rate.get("rate_per_gram", 0))
		prev_rate = prev_rates.get(key)

		if prev_rate:
			change = rate_per_gram - prev_rate
			change_percent = (change / prev_rate * 100) if prev_rate > 0 else 0
			trend = "▲" if change > 0 else ("▼" if change < 0 else "→")
		else:
			change = 0
			change_percent = 0
			trend = "-"

		rate["rate_per_gram"] = rate_per_gram
		rate["rate_change"] = flt(change)
		rate["change_percent"] = flt(change_percent)
		rate["trend"] = trend
		data.append(rate)

		prev_rates[key] = rate_per_gram

	return columns, data


def get_chart_data(filters=None):
	"""Return chart data for gold rate trends."""
	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = frappe.utils.add_days(frappe.utils.today(), -30)
	if not to_date:
		to_date = frappe.utils.today()

	chart_data = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			date,
			metal,
			purity,
			rate_per_gram
		FROM `tabGold Rate Log`
		WHERE date BETWEEN %(from_date)s AND %(to_date)s
		ORDER BY date
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	# Group by metal+purity
	grouped = {}
	for row in chart_data:
		key = f"{row.get('metal', 'Gold')} {row.get('purity', '24K')}"
		if key not in grouped:
			grouped[key] = {"dates": [], "rates": []}
		grouped[key]["dates"].append(str(row.get("date")))
		grouped[key]["rates"].append(flt(row.get("rate_per_gram", 0)))

	datasets = []
	for key, values in grouped.items():
		datasets.append({"name": key, "values": values["rates"]})

	return {
		"data": {"labels": next(iter(grouped.values()))["dates"] if grouped else [], "datasets": datasets},
		"type": "line",
	}
