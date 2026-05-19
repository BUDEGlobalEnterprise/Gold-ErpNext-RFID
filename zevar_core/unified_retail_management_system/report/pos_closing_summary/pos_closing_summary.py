import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "closing_entry",
			"label": _("Closing Entry"),
			"fieldtype": "Link",
			"options": "POS Closing Entry",
			"width": 180,
		},
		{
			"fieldname": "user",
			"label": _("User"),
			"fieldtype": "Link",
			"options": "User",
			"width": 150,
		},
		{
			"fieldname": "period_start_date",
			"label": _("Period Start"),
			"fieldtype": "Datetime",
			"width": 160,
		},
		{
			"fieldname": "period_end_date",
			"label": _("Period End"),
			"fieldtype": "Datetime",
			"width": 160,
		},
		{
			"fieldname": "grand_total",
			"label": _("Total Sales"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "net_total",
			"label": _("Net Sales"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "total_quantity",
			"label": _("Total Items Sold"),
			"fieldtype": "Float",
			"width": 130,
		},
	]


def get_data(filters):
	"""Pull POS Closing Entry rows, scoped by filters.

	Two corrections live here vs the previous version:

	1. Filter values are bound through %(name)s placeholders, never
	   interpolated. The old code did
	     conditions.append(f"pce.period_start >= '{filters.get('from_date')}'")
	   which was a textbook SQL-injection vector even with an
	   authenticated user.

	2. Column names match the actual `tabPOS Closing Entry` schema:
	   period_start_date / period_end_date (not period_start / period_end)
	   and total_quantity (there is no total_variance column on this
	   DocType — variance is recorded in the per-payment-mode child
	   table, which can be surfaced by a separate report).
	"""
	conditions = []
	values: dict = {}

	if filters.get("from_date"):
		conditions.append("pce.period_start_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("pce.period_end_date <= CONCAT(%(to_date)s, ' 23:59:59')")
		values["to_date"] = filters["to_date"]

	if filters.get("user"):
		conditions.append("pce.user = %(user)s")
		values["user"] = filters["user"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	# nosemgrep: only `where_clause` is interpolated and it is built
	# only from a fixed set of static fragments; every user-supplied
	# value travels through the `values` dict.
	return frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			pce.name AS closing_entry,
			pce.user,
			pce.period_start_date,
			pce.period_end_date,
			pce.grand_total,
			pce.net_total,
			pce.total_quantity
		FROM `tabPOS Closing Entry` pce
		WHERE pce.docstatus = 1
		  AND {where_clause}
		ORDER BY pce.period_end_date DESC
		""",
		values=values,
		as_dict=1,
	)
