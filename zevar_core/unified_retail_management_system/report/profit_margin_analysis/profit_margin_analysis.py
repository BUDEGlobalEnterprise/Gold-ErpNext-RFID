# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "posting_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "sales_invoice",
			"label": _("Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 140,
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
			"fieldname": "total_revenue",
			"label": _("Revenue"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "total_metal_cogs",
			"label": _("Metal COGS"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "total_gemstone_cogs",
			"label": _("Gemstone COGS"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "total_labor_cost",
			"label": _("Labor"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "total_commission",
			"label": _("Commission"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "total_payment_cost",
			"label": _("Payment Cost"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "overhead_per_invoice",
			"label": _("Overhead"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "total_cost",
			"label": _("Total Cost"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "gross_profit",
			"label": _("Gross Profit"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "gross_margin_pct",
			"label": _("Margin %"),
			"fieldtype": "Percent",
			"width": 100,
		},
	]


def get_data(filters):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	values = {
		"from_date": from_date,
		"to_date": to_date,
	}

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	query = """
		SELECT
			scb.posting_date,
			scb.sales_invoice,
			scb.customer,
			si.customer_name,
			scb.total_revenue,
			scb.total_metal_cogs,
			scb.total_gemstone_cogs,
			scb.total_labor_cost,
			scb.total_commission,
			scb.total_payment_cost,
			scb.overhead_per_invoice,
			scb.total_cost,
			scb.gross_profit,
			scb.gross_margin_pct
		FROM `tabSale Cost Breakdown` scb
		LEFT JOIN `tabSales Invoice` si ON scb.sales_invoice = si.name
		WHERE scb.docstatus = 1
			AND scb.posting_date >= %(from_date)s
			AND scb.posting_date <= %(to_date)s
		ORDER BY scb.posting_date DESC, scb.name DESC
	"""

	data = frappe.db.sql(query, values=values, as_dict=True)  # nosemgrep

	# Format Currency and Percent fields for display
	for row in data:
		row["total_revenue"] = flt(row.get("total_revenue"), 2)
		row["total_metal_cogs"] = flt(row.get("total_metal_cogs"), 2)
		row["total_gemstone_cogs"] = flt(row.get("total_gemstone_cogs"), 2)
		row["total_labor_cost"] = flt(row.get("total_labor_cost"), 2)
		row["total_commission"] = flt(row.get("total_commission"), 2)
		row["total_payment_cost"] = flt(row.get("total_payment_cost"), 2)
		row["overhead_per_invoice"] = flt(row.get("overhead_per_invoice"), 2)
		row["total_cost"] = flt(row.get("total_cost"), 2)
		row["gross_profit"] = flt(row.get("gross_profit"), 2)
		row["gross_margin_pct"] = flt(row.get("gross_margin_pct"), 1)

	return data
