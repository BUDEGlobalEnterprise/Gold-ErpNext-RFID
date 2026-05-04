# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""
	Execute the Sales by Salesperson Report.

	Returns sales breakdown by salesperson with totals and commission data.
	"""
	columns = [
		{
			"fieldname": "salesperson",
			"label": _("Salesperson"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "employee_name",
			"label": _("Name"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "total_sales",
			"label": _("Total Sales"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "transaction_count",
			"label": _("Transactions"),
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"fieldname": "total_commission",
			"label": _("Commission"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "avg_sale",
			"label": _("Avg Sale"),
			"fieldtype": "Currency",
			"width": 100,
		},
	]

	data = []

	filters = filters or {}

	# Date range filter
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	if not from_date:
		from_date = frappe.utils.add_months(frappe.utils.today(), -1)
	if not to_date:
		to_date = frappe.utils.today()

	# Get sales by salesperson
	sales_data = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			COALESCE(si.custom_salesperson_1, 'Unassigned') as salesperson,
			emp.employee_name as employee_name,
			COUNT(*) as transaction_count,
			SUM(si.grand_total) as total_sales,
			SUM(COALESCE(sc.total_commission, 0)) as total_commission,
			AVG(si.grand_total) as avg_sale
		FROM `tabSales Invoice` si
		LEFT JOIN `tabEmployee` emp ON emp.name = si.custom_salesperson_1
		WHERE si.is_pos = 1
			AND si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY si.custom_salesperson_1, emp.employee_name
		ORDER BY total_sales DESC
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	for row in sales_data:
		row["total_sales"] = flt(row.get("total_sales", 0))
		row["total_commission"] = flt(row.get("total_commission", 0))
		row["avg_sale"] = flt(row.get("avg_sale", 0))
		data.append(row)

	return columns, data


def get_chart_data(filters=None):
	"""Return chart data for visualization."""
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
			COALESCE(si.custom_salesperson_1, 'Unassigned') as name,
			SUM(si.grand_total) as value
		FROM `tabSales Invoice` si
		WHERE si.is_pos = 1
			AND si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		GROUP BY si.custom_salesperson_1
		ORDER BY value DESC
		LIMIT 10
	""",
		{"from_date": from_date, "to_date": to_date},
		as_dict=1,
	)

	return {
		"labels": [row.get("name") for row in chart_data],
		"datasets": [{"values": [flt(row.get("value", 0)) for row in chart_data]}],
	}
