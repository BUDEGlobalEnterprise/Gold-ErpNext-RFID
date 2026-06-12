# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import json

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
		{
			"fieldname": "employee_name",
			"label": frappe._("Employee Name"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "hours_allocated",
			"label": frappe._("Hours Allocated"),
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"fieldname": "labor_cost",
			"label": frappe._("Labor Cost ($)"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "sales_handled",
			"label": frappe._("Sales Handled"),
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"fieldname": "revenue_generated",
			"label": frappe._("Revenue Generated ($)"),
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"fieldname": "cost_per_sale",
			"label": frappe._("Cost per Sale ($)"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "profit_per_labor_dollar",
			"label": frappe._("Profit per Labor Dollar"),
			"fieldtype": "Float",
			"width": 180,
		},
	]


def get_data(filters):
	conditions, values = build_conditions(filters)

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	breakdowns = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			name,
			total_revenue,
			labor_allocation_detail
		FROM `tabSale Cost Breakdown`
		WHERE docstatus = 0 {conditions}
		ORDER BY posting_date DESC
		""",
		values=values,
		as_dict=True,
	)

	# Aggregate per employee from labor_allocation_detail JSON
	employee_data = {}

	for bd in breakdowns:
		if not bd.labor_allocation_detail:
			continue

		try:
			allocations = json.loads(bd.labor_allocation_detail)
		except (json.JSONDecodeError, TypeError):
			continue

		if not isinstance(allocations, list):
			continue

		revenue = flt(bd.total_revenue)

		for alloc in allocations:
			emp = alloc.get("employee")
			if not emp:
				# Skip entries without a specific employee (default pool allocation)
				continue

			# Apply employee filter if provided
			if filters and filters.get("employee") and emp != filters.get("employee"):
				continue

			if emp not in employee_data:
				employee_data[emp] = {
					"employee": emp,
					"employee_name": "",
					"hours_allocated": 0.0,
					"labor_cost": 0.0,
					"sales_handled": 0,
					"revenue_generated": 0.0,
				}

			allocated_minutes = flt(alloc.get("allocated_minutes", 0))
			cost = flt(alloc.get("cost", 0))
			split_pct = flt(alloc.get("split_percent", 100))

			employee_data[emp]["hours_allocated"] += allocated_minutes / 60.0
			employee_data[emp]["labor_cost"] += cost
			employee_data[emp]["sales_handled"] += 1
			# Revenue contribution proportional to split percentage
			employee_data[emp]["revenue_generated"] += revenue * (split_pct / 100.0)

	if not employee_data:
		return []

	# Fetch employee names
	emp_ids = list(employee_data.keys())
	employee_names = frappe.db.get_all(
		"Employee",
		filters={"name": ["in", emp_ids]},
		fields=["name", "employee_name"],
	)
	name_map = {e.name: e.employee_name for e in employee_names}

	# Build result rows
	result = []
	for emp_id, row in employee_data.items():
		row["employee_name"] = name_map.get(emp_id, "")
		row["hours_allocated"] = flt(row["hours_allocated"], 2)
		row["labor_cost"] = flt(row["labor_cost"], 2)
		row["revenue_generated"] = flt(row["revenue_generated"], 2)

		if flt(row["labor_cost"]) > 0:
			row["cost_per_sale"] = flt(row["labor_cost"] / row["sales_handled"], 2)
			row["profit_per_labor_dollar"] = flt(row["revenue_generated"] / row["labor_cost"], 2)
		else:
			row["cost_per_sale"] = 0.0
			row["profit_per_labor_dollar"] = 0.0

		result.append(row)

	result.sort(key=lambda x: x["profit_per_labor_dollar"], reverse=True)
	return result


def build_conditions(filters):
	conditions = ""
	values = {}

	if not filters:
		return conditions, values

	if filters.get("from_date"):
		conditions += " AND posting_date >= %(from_date)s"
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions += " AND posting_date <= %(to_date)s"
		values["to_date"] = filters["to_date"]

	# Note: employee filter is applied at the JSON parsing level,
	# not as a SQL condition, because employee lives inside
	# the labor_allocation_detail JSON field.

	return conditions, values
