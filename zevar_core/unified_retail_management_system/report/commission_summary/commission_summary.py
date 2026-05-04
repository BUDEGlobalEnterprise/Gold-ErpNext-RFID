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
			"fieldname": "employee",
			"label": frappe._("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 180,
		},
		{"fieldname": "employee_name", "label": frappe._("Employee Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "total_sales", "label": frappe._("Total Sales"), "fieldtype": "Currency", "width": 140},
		{
			"fieldname": "total_commission",
			"label": frappe._("Total Commission"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{"fieldname": "avg_rate", "label": frappe._("Avg Rate %"), "fieldtype": "Percent", "width": 100},
		{"fieldname": "split_count", "label": frappe._("# Invoices"), "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	conditions = ""
	values = {}

	if filters and filters.get("from_date"):
		conditions += " AND scs.posting_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]

	if filters and filters.get("to_date"):
		conditions += " AND scs.posting_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	if filters and filters.get("employee"):
		conditions += " AND scs.employee = %(employee)s"
		values["employee"] = filters["employee"]

	if filters and filters.get("status"):
		conditions += " AND scs.status = %(status)s"
		values["status"] = filters["status"]

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			scs.employee,
			e.employee_name,
			SUM(scs.sale_amount) AS total_sales,
			SUM(scs.commission_amount) AS total_commission,
			AVG(scs.commission_rate) AS avg_rate,
			COUNT(*) AS split_count
		FROM `tabSales Commission Split` scs
		LEFT JOIN `tabEmployee` e ON e.name = scs.employee
		WHERE 1=1 {conditions}
		GROUP BY scs.employee
		ORDER BY total_commission DESC
		""",
		values=values,
		as_dict=True,
	)

	return data
