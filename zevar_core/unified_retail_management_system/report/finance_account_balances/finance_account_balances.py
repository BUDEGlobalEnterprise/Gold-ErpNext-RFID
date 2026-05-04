# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": frappe._("Account"),
			"fieldtype": "Link",
			"options": "In-House Finance Account",
			"width": 160,
		},
		{
			"fieldname": "customer",
			"label": frappe._("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{"fieldname": "status", "label": frappe._("Status"), "fieldtype": "Data", "width": 100},
		{
			"fieldname": "credit_limit",
			"label": frappe._("Credit Limit"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{"fieldname": "current_balance", "label": frappe._("Balance"), "fieldtype": "Currency", "width": 130},
		{
			"fieldname": "available_credit",
			"label": frappe._("Available"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{"fieldname": "utilization", "label": frappe._("% Used"), "fieldtype": "Percent", "width": 90},
		{"fieldname": "interest_rate", "label": frappe._("APR %"), "fieldtype": "Percent", "width": 80},
	]


def get_data(filters):
	conditions = "WHERE 1=1"
	values = {}

	if filters and filters.get("status"):
		conditions += " AND fa.status = %(status)s"
		values["status"] = filters["status"]

	if filters and filters.get("customer"):
		conditions += " AND fa.customer = %(customer)s"
		values["customer"] = filters["customer"]

	if filters and filters.get("has_balance"):
		conditions += " AND fa.current_balance > 0"

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			fa.name, fa.customer, fa.status,
			fa.credit_limit, fa.current_balance,
			fa.available_credit, fa.interest_rate
		FROM `tabIn-House Finance Account` fa
		{conditions}
		ORDER BY fa.current_balance DESC
		""",
		values=values,
		as_dict=True,
	)

	for row in rows:
		limit = flt(row["credit_limit"])
		row["utilization"] = (flt(row["current_balance"]) / limit * 100) if limit else 0

	return rows
