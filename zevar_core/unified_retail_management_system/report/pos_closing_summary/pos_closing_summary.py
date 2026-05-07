import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
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
            "fieldname": "period_start",
            "label": _("Period Start"),
            "fieldtype": "Datetime",
            "width": 160,
        },
        {
            "fieldname": "period_end",
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
            "fieldname": "total_variance",
            "label": _("Total Variance"),
            "fieldtype": "Currency",
            "width": 120,
        }
    ]

def get_data(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"pce.period_start >= '{filters.get('from_date')}'")
    if filters.get("to_date"):
        conditions.append(f"pce.period_end <= '{filters.get('to_date')} 23:59:59'")
    if filters.get("user"):
        conditions.append(f"pce.user = '{filters.get('user')}'")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT 
            pce.name as closing_entry,
            pce.user,
            pce.period_start,
            pce.period_end,
            pce.grand_total,
            pce.net_total,
            pce.total_variance
        FROM `tabPOS Closing Entry` pce
        WHERE pce.docstatus = 1 
          AND {where_clause}
        ORDER BY pce.period_end DESC
    """
    
    return frappe.db.sql(query, as_dict=1)
