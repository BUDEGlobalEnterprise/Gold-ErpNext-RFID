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
        }
    ]

def get_data(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"si.posting_date >= '{filters.get('from_date')}'")
    if filters.get("to_date"):
        conditions.append(f"si.posting_date <= '{filters.get('to_date')}'")
    if filters.get("warehouse"):
        conditions.append(f"sii.warehouse = '{filters.get('warehouse')}'")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT 
            sii.item_code,
            sii.item_name,
            SUM(sii.qty) as total_qty,
            SUM(sii.base_amount) as total_amount,
            AVG(sii.base_rate) as avg_rate
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.docstatus = 1 
          AND si.is_pos = 1
          AND {where_clause}
        GROUP BY sii.item_code, sii.item_name
        ORDER BY total_amount DESC
        LIMIT {filters.get("limit") or 20}
    """
    
    return frappe.db.sql(query, as_dict=1)

def get_chart(data):
    if not data:
        return None
        
    # Take top 10 for the chart
    top_data = data[:10]
    labels = [row.get("item_name")[:15] for row in top_data]
    values = [flt(row.get("total_amount")) for row in top_data]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [{"values": values}]
        },
        "type": "donut",
        "colors": ["#D4AF37", "#b5952f", "#967b27", "#77611f"]
    }
