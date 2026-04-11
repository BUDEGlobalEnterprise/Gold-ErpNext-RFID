# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

from datetime import timedelta

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "repair_order",
			"label": _("Repair Order"),
			"fieldtype": "Link",
			"options": "Repair Order",
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
			"fieldname": "customer_phone",
			"label": _("Phone"),
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"fieldname": "received_date",
			"label": _("Received Date"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "promised_date",
			"label": _("Promised Date"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "days_overdue",
			"label": _("Days Overdue"),
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"fieldname": "overdue_category",
			"label": _("Category"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "repair_type",
			"label": _("Repair Type"),
			"fieldtype": "Link",
			"options": "Repair Type",
			"width": 150,
		},
		{
			"fieldname": "total_cost",
			"label": _("Total Cost"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "deposit_amount",
			"label": _("Deposit"),
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"fieldname": "balance_due",
			"label": _("Balance Due"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "assigned_to",
			"label": _("Technician"),
			"fieldtype": "Link",
			"options": "User",
			"width": 140,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "warehouse",
			"label": _("Store"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 130,
		},
		{
			"fieldname": "priority",
			"label": _("Priority"),
			"fieldtype": "Data",
			"width": 100,
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)
	values = get_values(filters)

	today_date = today()

	# nosemgrep: frappe-semgrep-rules.rules.security.frappe-sql-format-injection
	rows = frappe.db.sql(
		f"""
		SELECT
			ro.name as repair_order,
			ro.customer,
			ro.customer_phone,
			DATE(ro.received_date) as received_date,
			ro.promised_date,
			ro.repair_type,
			ro.total_cost,
			ro.deposit_amount,
			ro.balance_due,
			ro.assigned_to,
			ro.status,
			ro.warehouse,
			ro.priority
		FROM `tabRepair Order` ro
		WHERE ro.docstatus = 1
			AND ro.promised_date IS NOT NULL
			AND ro.promised_date < %(today)s
			AND ro.status NOT IN ('Delivered', 'Cancelled')
			{conditions}
		ORDER BY ro.promised_date ASC
		""",
		values={**values, "today": today_date},
		as_dict=True,
	)

	data = []
	for row in rows:
		promised_date = getdate(row.promised_date)
		days_overdue = (today_date - promised_date).days
		row.days_overdue = days_overdue

		# Categorize overdue
		if days_overdue <= 3:
			row.overdue_category = '<span class="text-warning">1-3 days</span>'
		elif days_overdue <= 7:
			row.overdue_category = '<span class="text-orange">4-7 days</span>'
		elif days_overdue <= 14:
			row.overdue_category = '<span class="text-danger">8-14 days</span>'
		else:
			row.overdue_category = '<span class="text-danger" style="font-weight:bold">15+ days</span>'

		data.append(row)

	return data


def get_conditions(filters):
	conditions = ""

	if filters.get("warehouse"):
		conditions += " AND ro.warehouse = %(warehouse)s"

	if filters.get("repair_type"):
		conditions += " AND ro.repair_type = %(repair_type)s"

	if filters.get("assigned_to"):
		conditions += " AND ro.assigned_to = %(assigned_to)s"

	if filters.get("status"):
		conditions += " AND ro.status = %(status)s"

	if filters.get("customer"):
		conditions += " AND ro.customer = %(customer)s"

	if filters.get("priority"):
		conditions += " AND ro.priority = %(priority)s"

	# Minimum days overdue filter
	if filters.get("min_days_overdue"):
		min_days = filters.get("min_days_overdue")
		conditions += f" AND DATEDIFF(%(today)s, ro.promised_date) >= {min_days}"

	return conditions


def get_values(filters):
	values = {}
	if filters.get("warehouse"):
		values["warehouse"] = filters["warehouse"]
	if filters.get("repair_type"):
		values["repair_type"] = filters["repair_type"]
	if filters.get("assigned_to"):
		values["assigned_to"] = filters["assigned_to"]
	if filters.get("status"):
		values["status"] = filters["status"]
	if filters.get("customer"):
		values["customer"] = filters["customer"]
	if filters.get("priority"):
		values["priority"] = filters["priority"]
	return values
