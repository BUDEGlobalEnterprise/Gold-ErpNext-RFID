# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff, flt, today


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": frappe._("Contract"),
			"fieldtype": "Link",
			"options": "Layaway Contract",
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
		{"fieldname": "contract_date", "label": frappe._("Start Date"), "fieldtype": "Date", "width": 110},
		{
			"fieldname": "target_completion_date",
			"label": frappe._("Due Date"),
			"fieldtype": "Date",
			"width": 110,
		},
		{"fieldname": "days_remaining", "label": frappe._("Days Left"), "fieldtype": "Int", "width": 90},
		{"fieldname": "total_amount", "label": frappe._("Total"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "deposit_amount", "label": frappe._("Paid"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "balance_amount", "label": frappe._("Balance"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "pct_paid", "label": frappe._("% Paid"), "fieldtype": "Percent", "width": 90},
	]


def get_data(filters):
	conditions = "WHERE lc.docstatus = 1"
	values = {}

	if filters and filters.get("status"):
		conditions += " AND lc.status = %(status)s"
		values["status"] = filters["status"]

	if filters and filters.get("customer"):
		conditions += " AND lc.customer = %(customer)s"
		values["customer"] = filters["customer"]

	if filters and filters.get("overdue_only"):
		conditions += " AND lc.target_completion_date < %(today)s AND lc.status = 'Active'"
		values["today"] = today()

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			lc.name, lc.customer, lc.status,
			lc.contract_date, lc.target_completion_date,
			lc.total_amount, lc.deposit_amount, lc.balance_amount
		FROM `tabLayaway Contract` lc
		{conditions}
		ORDER BY lc.target_completion_date ASC
		""",
		values=values,
		as_dict=True,
	)

	for row in rows:
		row["days_remaining"] = date_diff(row["target_completion_date"], today())
		total = flt(row["total_amount"])
		row["pct_paid"] = (flt(row["deposit_amount"]) / total * 100) if total else 0

	return rows
