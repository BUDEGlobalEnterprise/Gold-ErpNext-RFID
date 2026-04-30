# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0


import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	"""
	Execute the Payment Method Summary Report.

	Returns breakdown of payments by method for reconciliation.
	"""
	columns = [
		{
			"fieldname": "mode_of_payment",
			"label": _("Payment Method"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "transaction_count",
			"label": _("Transactions"),
			"fieldtype": "Int",
			"width": 120,
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "percentage",
			"label": _("% of Total"),
			"fieldtype": "Percent",
			"width": 100,
		},
		{
			"fieldname": "avg_transaction",
			"label": _("Avg Transaction"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "receivable_account",
			"label": _("Receivable Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 200,
		},
	]

	data = []

	filters = filters or {}

	# Date range filter
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	warehouse = filters.get("warehouse")

	if not from_date:
		from_date = frappe.utils.today()
	if not to_date:
		to_date = frappe.utils.today()

	# Build warehouse filter
	warehouse_filter = ""
	warehouse_params = {"from_date": from_date, "to_date": to_date}
	if warehouse:
		warehouse_filter = "AND EXISTS (SELECT 1 FROM `tabSales Invoice Item` sii WHERE sii.parent = si.name AND sii.warehouse = %(warehouse)s)"
		warehouse_params["warehouse"] = warehouse

	# Stream filter
	stream_filter = ""
	transaction_stream = filters.get("transaction_stream")
	if transaction_stream:
		if isinstance(transaction_stream, str):
			transaction_stream = [transaction_stream]

		if transaction_stream:
			stream_filter = "AND si.custom_transaction_stream IN %(transaction_stream)s"
			warehouse_params["transaction_stream"] = tuple(transaction_stream)

	# Get payment method breakdown
	payment_data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			sip.mode_of_payment,
			COUNT(*) as transaction_count,
			SUM(sip.amount) as total_amount,
			AVG(sip.amount) as avg_transaction
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.is_pos = 1
			AND si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
			{warehouse_filter}
			{stream_filter}
		GROUP BY sip.mode_of_payment
		ORDER BY total_amount DESC
	""",
		warehouse_params,
		as_dict=1,
	)

	# Calculate grand total
	grand_total = sum(flt(row.get("total_amount", 0)) for row in payment_data)

	financiers = ["AFF", "CIMA", "Synchrony", "Progressive", "Snap"]

	for row in payment_data:
		row["total_amount"] = flt(row.get("total_amount", 0))
		row["avg_transaction"] = flt(row.get("avg_transaction", 0))
		row["percentage"] = (row["total_amount"] / grand_total * 100) if grand_total > 0 else 0

		if row["mode_of_payment"] in financiers:
			row["receivable_account"] = f"Asset — A/R {row['mode_of_payment']} - ZJ"
		else:
			row["receivable_account"] = ""

		data.append(row)

	return columns, data


def get_chart_data(filters=None):
	"""Return chart data for visualization."""
	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	warehouse = filters.get("warehouse")

	if not from_date:
		from_date = frappe.utils.today()
	if not to_date:
		to_date = frappe.utils.today()

	warehouse_filter = ""
	warehouse_params = {"from_date": from_date, "to_date": to_date}
	if warehouse:
		warehouse_filter = "AND EXISTS (SELECT 1 FROM `tabSales Invoice Item` sii WHERE sii.parent = si.name AND sii.warehouse = %(warehouse)s)"
		warehouse_params["warehouse"] = warehouse

	stream_filter = ""
	transaction_stream = filters.get("transaction_stream")
	if transaction_stream:
		if isinstance(transaction_stream, str):
			transaction_stream = [transaction_stream]

		if transaction_stream:
			stream_filter = "AND si.custom_transaction_stream IN %(transaction_stream)s"
			warehouse_params["transaction_stream"] = tuple(transaction_stream)

	chart_data = frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			sip.mode_of_payment as name,
			SUM(sip.amount) as value
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.is_pos = 1
			AND si.docstatus = 1
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
			{warehouse_filter}
			{stream_filter}
		GROUP BY sip.mode_of_payment
		ORDER BY value DESC
	""",
		warehouse_params,
		as_dict=1,
	)

	return {
		"data": {
			"labels": [row.get("name", "Unknown") for row in chart_data],
			"datasets": [{"values": [flt(row.get("value", 0)) for row in chart_data]}],
		},
		"type": "donut",
	}
