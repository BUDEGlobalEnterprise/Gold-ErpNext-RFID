# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0


import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""
	Execute the Trade-In Summary Report.

	Returns summary of trade-in transactions with 2x rule compliance.
	"""
	columns = [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "invoice",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 120,
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "trade_in_value",
			"label": _("Trade-In Value"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "new_item_value",
			"label": _("New Item Value"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "ratio",
			"label": _("Ratio"),
			"fieldtype": "Percent",
			"width": 80,
		},
		{
			"fieldname": "compliance",
			"label": _("2x Rule"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "manager_override",
			"label": _("Manager Override"),
			"fieldtype": "Check",
			"width": 100,
		},
		{
			"fieldname": "salesperson",
			"label": _("Salesperson"),
			"fieldtype": "Data",
			"width": 120,
		},
	]

	data = []

	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = frappe.utils.add_months(frappe.utils.today(), -1)
	if not to_date:
		to_date = frappe.utils.today()

	# Get trade-in records from Sales Invoice custom fields
	trade_ins = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			si.posting_date as date,
			si.name as invoice,
			si.customer,
			si.customer_name,
			ti.trade_in_value,
			ti.new_item_value,
			ti.manager_override,
			ti.override_reason,
			si.custom_salesperson_1 as salesperson
		FROM `tabSales Invoice` si
		JOIN `tabSales Invoice Custom Trade Ins` ti ON ti.parent = si.name
		WHERE si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		ORDER BY si.posting_date DESC
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	for row in trade_ins:
		trade_in_value = flt(row.get("trade_in_value", 0))
		new_item_value = flt(row.get("new_item_value", 0))

		# Calculate ratio
		ratio = (trade_in_value / new_item_value * 100) if new_item_value > 0 else 0

		# Check 2x rule compliance
		compliance = "✓ Compliant" if new_item_value >= (trade_in_value * 2) else "⚠ Violation"

		row["trade_in_value"] = trade_in_value
		row["new_item_value"] = new_item_value
		row["ratio"] = ratio
		row["compliance"] = compliance
		data.append(row)

	return columns, data


def get_chart_data(filters=None):
	"""Return chart data for trade-in trends."""
	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = frappe.utils.add_months(frappe.utils.today(), -1)
	if not to_date:
		to_date = frappe.utils.today()

	chart_data = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			si.posting_date as date,
			SUM(ti.trade_in_value) as trade_in_value,
			COUNT(*) as count
		FROM `tabSales Invoice` si
		JOIN `tabSales Invoice Custom Trade Ins` ti ON ti.parent = si.name
		WHERE si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY si.posting_date
		ORDER BY si.posting_date
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	return {
		"data": {
			"labels": [str(row.get("date")) for row in chart_data],
			"datasets": [
				{
					"name": "Trade-In Value",
					"values": [flt(row.get("trade_in_value", 0)) for row in chart_data],
				}
			],
		},
		"type": "line",
	}
