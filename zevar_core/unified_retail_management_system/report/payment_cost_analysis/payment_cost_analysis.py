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
			"fieldname": "payment_mode",
			"label": frappe._("Payment Mode"),
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"fieldname": "transaction_count",
			"label": frappe._("Transaction Count"),
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"fieldname": "total_volume",
			"label": frappe._("Total Volume ($)"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "processing_rate",
			"label": frappe._("Processing Rate (%)"),
			"fieldtype": "Percent",
			"width": 150,
		},
		{
			"fieldname": "total_processing_cost",
			"label": frappe._("Total Processing Cost ($)"),
			"fieldtype": "Currency",
			"width": 180,
		},
		{
			"fieldname": "effective_rate",
			"label": frappe._("Effective Rate (%)"),
			"fieldtype": "Percent",
			"width": 150,
		},
	]


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
		SELECT payment_cost_detail
		FROM `tabSale Cost Breakdown`
		WHERE docstatus = 1 {conditions}
		""",
		values=values,
		as_dict=True,
	)

	aggregated = {}

	for row in rows:
		detail_str = row.get("payment_cost_detail")
		if not detail_str:
			continue

		try:
			details = json.loads(detail_str)
		except (json.JSONDecodeError, TypeError):
			continue

		if not isinstance(details, list):
			continue

		for entry in details:
			mode = entry.get("payment_mode", "Unknown")
			volume = flt(entry.get("amount", 0))
			cost = flt(entry.get("processing_cost", 0))
			rate = flt(entry.get("processing_rate", 0))

			if mode not in aggregated:
				aggregated[mode] = {
					"payment_mode": mode,
					"transaction_count": 0,
					"total_volume": 0,
					"total_processing_cost": 0,
					"rate_weighted_sum": 0,
				}

			aggregated[mode]["transaction_count"] += 1
			aggregated[mode]["total_volume"] += volume
			aggregated[mode]["total_processing_cost"] += cost
			aggregated[mode]["rate_weighted_sum"] += rate

	data = []
	for mode, agg in aggregated.items():
		total_volume = flt(agg["total_volume"])
		total_cost = flt(agg["total_processing_cost"])
		count = agg["transaction_count"]

		processing_rate = flt(agg["rate_weighted_sum"] / count) if count > 0 else 0
		effective_rate = flt((total_cost / total_volume) * 100) if total_volume > 0 else 0

		data.append(
			{
				"payment_mode": mode,
				"transaction_count": count,
				"total_volume": total_volume,
				"processing_rate": processing_rate,
				"total_processing_cost": total_cost,
				"effective_rate": effective_rate,
			}
		)

	data.sort(key=lambda x: x["total_processing_cost"], reverse=True)
	return data
