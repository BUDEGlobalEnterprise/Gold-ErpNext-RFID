"""
Memo Contract API — consignment/memo lifecycle management
"""

import frappe
from frappe import _
from frappe.utils import getdate, add_days, date_diff


@frappe.whitelist()
def create_memo(data: dict) -> dict:
    """Create a new memo contract with items from a vendor."""
    if isinstance(data, str):
        import json
        data = json.loads(data)

    frappe.has_permission("Memo Contract", "create", throw=True)

    doc = frappe.get_doc({"doctype": "Memo Contract", **data})
    doc.insert(ignore_permissions=True)

    return {
        "success": True,
        "name": doc.name,
        "total_memo_value": doc.total_memo_value,
        "item_count": doc.item_count,
    }


@frappe.whitelist()
def submit_memo(name: str) -> dict:
    """Activate a memo contract, moving items to consignment warehouse."""
    frappe.has_permission("Memo Contract", "submit", throw=True)

    doc = frappe.get_doc("Memo Contract", name)
    doc.submit()

    return {"success": True, "name": doc.name, "status": "Active"}


@frappe.whitelist()
def mark_item_sold(memo_name: str, item_idx: int, sales_invoice: str | None = None) -> dict:
    """Mark a specific memo item as sold."""
    frappe.has_permission("Memo Contract", "write", throw=True)

    doc = frappe.get_doc("Memo Contract", memo_name)
    doc.mark_item_sold(item_idx, sales_invoice)

    return {
        "success": True,
        "item_status": doc.items[item_idx].status,
        "total_sold_value": doc.total_sold_value,
        "balance_due": doc.balance_due,
    }


@frappe.whitelist()
def mark_item_returned(memo_name: str, item_idx: int) -> dict:
    """Mark a specific memo item as returned to vendor."""
    frappe.has_permission("Memo Contract", "write", throw=True)

    doc = frappe.get_doc("Memo Contract", memo_name)
    doc.mark_item_returned(item_idx)

    return {
        "success": True,
        "item_status": doc.items[item_idx].status,
        "total_returned_value": doc.total_returned_value,
    }


@frappe.whitelist()
def record_memo_payment(memo_name: str, amount: float, payment_type: str = "Settlement", reference: str | None = None) -> dict:
    """Record a payment to the vendor for sold memo items."""
    frappe.has_permission("Memo Contract", "write", throw=True)

    doc = frappe.get_doc("Memo Contract", memo_name)
    doc.record_payment(float(amount), payment_type, reference)

    return {
        "success": True,
        "total_paid": doc.total_paid,
        "balance_due": doc.balance_due,
        "status": doc.status,
    }


@frappe.whitelist()
def get_memo_contracts(filters: dict | None = None, limit: int = 20) -> list:
    """Get list of memo contracts with summary info."""
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    return frappe.get_all(
        "Memo Contract",
        fields=[
            "name",
            "supplier",
            "supplier_name",
            "contract_date",
            "due_date",
            "status",
            "total_memo_value",
            "total_sold_value",
            "balance_due",
            "item_count",
            "items_sold",
            "items_returned",
            "aging_days",
            "aging_category",
        ],
        filters=filters or {},
        order_by="contract_date desc",
        limit_page_length=int(limit),
    )


@frappe.whitelist()
def get_memo_aging_summary() -> list:
    """Get aging summary across all active memo contracts."""
    memos = frappe.get_all(
        "Memo Contract",
        fields=["name", "supplier_name", "total_memo_value", "balance_due", "aging_days", "aging_category", "due_date"],
        filters={"status": ["in", ["Active", "Overdue", "Partial Settlement"]]},
        order_by="aging_days desc",
    )

    summary = {"Current": [], "1-30 Days": [], "31-60 Days": [], "61-90 Days": [], "90+ Days": []}
    totals = {k: {"count": 0, "value": 0} for k in summary}

    for m in memos:
        cat = m.aging_category or "Current"
        if cat not in summary:
            cat = "Current"
        summary[cat].append(m)
        totals[cat]["count"] += 1
        totals[cat]["value"] += m.balance_due or 0

    return {"detail": summary, "totals": totals}


@frappe.whitelist()
def check_overdue_memos():
    """Scheduled task: update aging on overdue memo contracts."""
    memos = frappe.get_all(
        "Memo Contract",
        filters={"status": ["in", ["Active", "Partial Settlement"]], "docstatus": 1},
    )

    updated = 0
    for m in memos:
        doc = frappe.get_doc("Memo Contract", m.name)
        doc._calculate_aging()
        doc._calculate_totals()

        if doc.aging_days > 0 and doc.status != "Overdue":
            doc.db_set("status", "Overdue")
            updated += 1
        elif doc.aging_days <= 0 and doc.status == "Overdue":
            doc.db_set("status", "Active")
            updated += 1

        if doc.aging_days > (doc.auto_return_days or 90):
            for item in doc.items:
                if item.status == "On Memo":
                    item.status = "Returned"
                    item.date_returned = getdate()
            doc._calculate_totals()
            doc.db_set("status", "Returned")
            updated += 1

    return {"checked": len(memos), "updated": updated}
