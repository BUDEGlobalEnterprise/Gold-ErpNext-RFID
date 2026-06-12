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
		{"fieldname": "period", "label": frappe._("Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "invoices", "label": frappe._("Invoices"), "fieldtype": "Int", "width": 100},
		{
			"fieldname": "total_overhead",
			"label": frappe._("Total Overhead"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "overhead_per_invoice",
			"label": frappe._("Overhead per Invoice"),
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"fieldname": "rent_portion",
			"label": frappe._("Rent Portion"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "utilities_portion",
			"label": frappe._("Utilities Portion"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "marketing_portion",
			"label": frappe._("Marketing Portion"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "insurance_portion",
			"label": frappe._("Insurance Portion"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{"fieldname": "other", "label": frappe._("Other"), "fieldtype": "Currency", "width": 120},
	]


def get_allocation_ratios():
	"""Read Cost Center Allocation singleton for overhead category ratios."""
	if not frappe.db.exists("DocType", "Cost Center Allocation"):
		return {"rent": 0, "utilities": 0, "marketing": 0, "insurance": 0, "other": 0}

	alloc_name = frappe.db.get_value("Cost Center Allocation", {}, "name")
	if not alloc_name:
		return {"rent": 0, "utilities": 0, "marketing": 0, "insurance": 0, "other": 0}

	alloc = frappe.get_doc("Cost Center Allocation", alloc_name)
	ratios = {"rent": 0, "utilities": 0, "marketing": 0, "insurance": 0, "other": 0}

	total = (
		flt(alloc.get("rent_percentage", 0))
		+ flt(alloc.get("utilities_percentage", 0))
		+ flt(alloc.get("marketing_percentage", 0))
		+ flt(alloc.get("insurance_percentage", 0))
		+ flt(alloc.get("other_percentage", 0))
	)

	if total == 0:
		return ratios

	ratios["rent"] = flt(alloc.get("rent_percentage", 0)) / total
	ratios["utilities"] = flt(alloc.get("utilities_percentage", 0)) / total
	ratios["marketing"] = flt(alloc.get("marketing_percentage", 0)) / total
	ratios["insurance"] = flt(alloc.get("insurance_percentage", 0)) / total
	ratios["other"] = flt(alloc.get("other_percentage", 0)) / total

	return ratios


def get_data(filters):
	conditions = ""
	values = {}

	if filters and filters.get("from_date"):
		conditions += " AND posting_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]

	if filters and filters.get("to_date"):
		conditions += " AND posting_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			posting_date AS period,
			COUNT(*) AS invoices,
			SUM(overhead_per_invoice) AS total_overhead,
			AVG(overhead_per_invoice) AS overhead_per_invoice
		FROM `tabSale Cost Breakdown`
		WHERE docstatus = 1 {conditions}
		GROUP BY posting_date
		ORDER BY posting_date
		""",
		values=values,
		as_dict=True,
	)

	ratios = get_allocation_ratios()

	for row in rows:
		total_oh = flt(row.get("total_overhead", 0))
		row["rent_portion"] = flt(total_oh * ratios["rent"])
		row["utilities_portion"] = flt(total_oh * ratios["utilities"])
		row["marketing_portion"] = flt(total_oh * ratios["marketing"])
		row["insurance_portion"] = flt(total_oh * ratios["insurance"])
		row["other"] = flt(total_oh * ratios["other"])

	return rows
