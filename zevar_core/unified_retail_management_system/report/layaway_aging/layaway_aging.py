# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0


import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate


def execute(filters=None):
	"""
	Execute the Layaway Aging Report.

	Returns layaway contracts grouped by aging buckets.
	"""
	columns = [
		{
			"fieldname": "contract",
			"label": _("Contract"),
			"fieldtype": "Link",
			"options": "Layaway Contract",
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
			"fieldname": "contract_date",
			"label": _("Contract Date"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "paid_amount",
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "balance_amount",
			"label": _("Balance"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "days_outstanding",
			"label": _("Days Outstanding"),
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"fieldname": "aging_bucket",
			"label": _("Aging Bucket"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "next_payment_due",
			"label": _("Next Payment Due"),
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100,
		},
	]

	data = []

	filters = filters or {}
	status_filter = filters.get("status")

	# Get active layaway contracts
	query_filters = {"docstatus": ["<", 2]}
	if status_filter:
		query_filters["status"] = status_filter

	contracts = frappe.get_all(
		"Layaway Contract",
		filters=query_filters,
		fields=[
			"name as contract",
			"customer",
			"customer_name",
			"contract_date",
			"total_amount",
			"paid_amount",
			"balance_amount",
			"status",
		],
		order_by="contract_date",
	)

	today = getdate()

	for contract in contracts:
		contract_date = getdate(contract.get("contract_date"))
		days_outstanding = date_diff(today, contract_date)

		# Determine aging bucket
		if days_outstanding <= 30:
			aging_bucket = "0-30 days"
		elif days_outstanding <= 60:
			aging_bucket = "31-60 days"
		elif days_outstanding <= 90:
			aging_bucket = "61-90 days"
		else:
			aging_bucket = "90+ days"

		# Get next payment due date
		next_payment = frappe.db.get_value(
			"Layaway Payment Schedule",
			{"parent": contract.contract, "status": "Pending"},
			"due_date",
			order_by="due_date asc",
		)

		contract["days_outstanding"] = days_outstanding
		contract["aging_bucket"] = aging_bucket
		contract["next_payment_due"] = next_payment
		contract["total_amount"] = flt(contract.get("total_amount", 0))
		contract["paid_amount"] = flt(contract.get("paid_amount", 0))
		contract["balance_amount"] = flt(contract.get("balance_amount", 0))

		data.append(contract)

	return columns, data


def get_chart_data(filters=None):
	"""Return chart data for aging visualization."""
	filters = filters or {}

	chart_data = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			CASE
				WHEN DATEDIFF(CURDATE(), contract_date) <= 30 THEN '0-30 days'
				WHEN DATEDIFF(CURDATE(), contract_date) <= 60 THEN '31-60 days'
				WHEN DATEDIFF(CURDATE(), contract_date) <= 90 THEN '61-90 days'
				ELSE '90+ days'
			END as aging_bucket,
			COUNT(*) as count,
			SUM(balance_amount) as total_balance
		FROM `tabLayaway Contract`
		WHERE docstatus < 2
			AND status != 'Completed'
		GROUP BY aging_bucket
		ORDER BY FIELD(aging_bucket, '0-30 days', '31-60 days', '61-90 days', '90+ days')
	""",
		as_dict=1,
	)

	return {
		"data": {
			"labels": [row.get("aging_bucket", "Unknown") for row in chart_data],
			"datasets": [
				{"name": "Balance", "values": [flt(row.get("total_balance", 0)) for row in chart_data]}
			],
		},
		"type": "bar",
	}
