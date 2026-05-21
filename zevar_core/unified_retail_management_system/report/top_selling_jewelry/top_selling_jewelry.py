import frappe
from frappe import _
from frappe.utils import cint, flt

# Hard cap so a malicious / malformed `limit` filter cannot make the report
# return arbitrary amounts of data or generate a runaway query.
_MAX_LIMIT = 200
_DEFAULT_LIMIT = 20


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "metal",
			"label": _("Metal"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "purity",
			"label": _("Purity"),
			"fieldtype": "Data",
			"width": 90,
		},
		{
			"fieldname": "jewelry_type",
			"label": _("Jewelry Type"),
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"fieldname": "total_qty",
			"label": _("Total Qty"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "avg_rate",
			"label": _("Avg Rate"),
			"fieldtype": "Currency",
			"width": 120,
		},
	]


def get_data(filters):
	"""Top-selling jewelry items by total revenue.

	Pulls from `tabSales Invoice Item` joined with the parent invoice (POS
	only, submitted) and the Item master (for metal / purity / jewelry
	type). All filter values are bound through parameter placeholders so
	this report is safe against SQL injection.
	"""
	conditions = []
	values: dict = {}

	if filters.get("from_date"):
		conditions.append("si.posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("si.posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	if filters.get("warehouse"):
		conditions.append("sii.warehouse = %(warehouse)s")
		values["warehouse"] = filters["warehouse"]

	if filters.get("jewelry_type"):
		conditions.append("i.custom_jewelry_type = %(jewelry_type)s")
		values["jewelry_type"] = filters["jewelry_type"]

	if filters.get("metal"):
		conditions.append("i.custom_metal_type = %(metal)s")
		values["metal"] = filters["metal"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	# Validate `limit` strictly: cint handles non-numeric input by
	# returning 0; we then clamp into [1, _MAX_LIMIT].
	limit = cint(filters.get("limit") or _DEFAULT_LIMIT)
	if limit <= 0:
		limit = _DEFAULT_LIMIT
	limit = min(limit, _MAX_LIMIT)
	values["limit_value"] = limit

	# nosemgrep: only `where_clause` is interpolated and it is built only
	# from a fixed set of static fragments. The LIMIT placeholder uses a
	# bound parameter, and `limit_value` is hard-clamped above.
	return frappe.db.sql(  # nosemgrep
		f"""
		SELECT
			sii.item_code,
			sii.item_name,
			i.custom_metal_type AS metal,
			i.custom_purity AS purity,
			i.custom_jewelry_type AS jewelry_type,
			SUM(sii.qty) AS total_qty,
			SUM(sii.base_amount) AS total_amount,
			AVG(sii.base_rate) AS avg_rate
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		LEFT JOIN `tabItem` i ON sii.item_code = i.name
		WHERE si.docstatus = 1
		  AND si.is_pos = 1
		  AND {where_clause}
		GROUP BY sii.item_code, sii.item_name, i.custom_metal_type,
		         i.custom_purity, i.custom_jewelry_type
		ORDER BY total_amount DESC
		LIMIT %(limit_value)s
		""",
		values=values,
		as_dict=1,
	)


def get_chart(data):
	if not data:
		return None

	# Take top 10 for the chart
	top_data = data[:10]
	labels = [(row.get("item_name") or "")[:15] for row in top_data]
	values = [flt(row.get("total_amount")) for row in top_data]

	return {
		"data": {"labels": labels, "datasets": [{"values": values}]},
		"type": "donut",
		"colors": ["#D4AF37", "#b5952f", "#967b27", "#77611f"],
	}
