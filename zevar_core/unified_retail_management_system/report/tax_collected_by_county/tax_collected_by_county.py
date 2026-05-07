import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"fieldname": "county",
			"label": _("County"),
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "store_name",
			"label": _("Store"),
			"fieldtype": "Link",
			"options": "Store Location",
			"width": 150,
		},
		{
			"fieldname": "net_total",
			"label": _("Net Total"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "tax_amount",
			"label": _("Tax Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "grand_total",
			"label": _("Grand Total"),
			"fieldtype": "Currency",
			"width": 120,
		},
	]


def get_data(filters):
	conditions = []
	if filters.get("from_date"):
		conditions.append(f"si.posting_date >= '{filters.get('from_date')}'")
	if filters.get("to_date"):
		conditions.append(f"si.posting_date <= '{filters.get('to_date')}'")
	if filters.get("store"):
		conditions.append(f"sl.name = '{filters.get('store')}'")

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	query = f"""
        SELECT
            sl.county,
            sl.store_name,
            SUM(si.net_total) as net_total,
            SUM(si.total_taxes_and_charges) as tax_amount,
            SUM(si.grand_total) as grand_total
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabStore Location` sl ON sl.default_warehouse = sii.warehouse
        WHERE si.docstatus = 1
          AND si.is_pos = 1
          AND {where_clause}
        GROUP BY sl.county, sl.store_name
        ORDER BY sl.county ASC
    """

	return frappe.db.sql(query, as_dict=1)


def get_chart(data):
	if not data:
		return None

	labels = [row.get("county") for row in data]
	values = [flt(row.get("tax_amount")) for row in data]

	return {
		"data": {"labels": labels, "datasets": [{"values": values}]},
		"type": "bar",
		"colors": ["#D4AF37"],
	}
