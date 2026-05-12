# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

import frappe
from frappe import _
from frappe.utils import add_days, flt, today


def execute(filters=None):
	"""
	Execute the COGS Trend Report.

	Returns Cost of Goods Sold trend grouped by period with metal/gemstone
	breakdown and average gold rate per period.

	Joins Sale Cost Breakdown with Gold Rate Log to derive average gold rate.
	"""
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "period",
			"label": _("Period"),
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"fieldname": "metal_cogs",
			"label": _("Metal COGS"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "gemstone_cogs",
			"label": _("Gemstone COGS"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "total_cogs",
			"label": _("Total COGS"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "avg_gold_rate",
			"label": _("Avg Gold Rate"),
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"fieldname": "invoice_count",
			"label": _("Invoice Count"),
			"fieldtype": "Int",
			"width": 110,
		},
	]


def get_date_format(granularity):
	"""Return MySQL DATE_FORMAT string for the given granularity."""
	if granularity == "Daily":
		return "%Y-%m-%d"
	elif granularity == "Weekly":
		return "%Y-W%u"
	# Default: Monthly
	return "%Y-%m"


def get_data(filters):
	filters = filters or {}

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	granularity = filters.get("granularity") or "Monthly"

	if not from_date:
		from_date = add_days(today(), -90)
	if not to_date:
		to_date = today()

	date_format = get_date_format(granularity)

	# Build COGS data grouped by period from Sale Cost Breakdown
	# Join with Gold Rate Log to get average gold rate per period
	data = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			DATE_FORMAT(scb.posting_date, %(date_format)s) AS period,
			SUM(COALESCE(scb.total_metal_cogs, 0)) AS metal_cogs,
			SUM(COALESCE(scb.total_gemstone_cogs, 0)) AS gemstone_cogs,
			SUM(
				COALESCE(scb.total_metal_cogs, 0)
				+ COALESCE(scb.total_gemstone_cogs, 0)
			) AS total_cogs,
			COALESCE(gr.avg_rate, 0) AS avg_gold_rate,
			COUNT(scb.name) AS invoice_count
		FROM `tabSale Cost Breakdown` scb
		LEFT JOIN (
			SELECT
				DATE_FORMAT(DATE(grl.timestamp), %(date_format)s) AS rate_period,
				AVG(grl.rate_per_gram) AS avg_rate
			FROM `tabGold Rate Log` grl
			WHERE DATE(grl.timestamp) BETWEEN %(from_date)s AND %(to_date)s
				AND grl.metal = 'Gold'
			GROUP BY rate_period
		) gr ON gr.rate_period = DATE_FORMAT(scb.posting_date, %(date_format)s)
		WHERE scb.posting_date BETWEEN %(from_date)s AND %(to_date)s
			AND scb.docstatus = 1
		GROUP BY period
		ORDER BY period ASC
		""",
		{
			"date_format": date_format,
			"from_date": from_date,
			"to_date": to_date,
		},
		as_dict=1,
	)

	for row in data:
		row["metal_cogs"] = flt(row.get("metal_cogs", 0))
		row["gemstone_cogs"] = flt(row.get("gemstone_cogs", 0))
		row["total_cogs"] = flt(row.get("total_cogs", 0))
		row["avg_gold_rate"] = flt(row.get("avg_gold_rate", 0))

	return data
