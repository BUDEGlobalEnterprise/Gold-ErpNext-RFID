"""
Gold Purchase API — scrap gold buying operations
"""

import frappe
from frappe import _


@frappe.whitelist()
def calculate_scrap_value(metal_type: str, purity: str, gross_weight_g: float, stone_weight_g: float = 0) -> dict:
    """Calculate the value of a scrap gold item based on live rates.

    Called in real-time as the cashier weighs items at the counter.
    """
    from zevar_core.api.pricing import _get_gold_rate
    from zevar_core.constants import PURITY_VALUES

    net_weight = (float(gross_weight_g) - float(stone_weight_g or 0))
    if net_weight <= 0:
        return {"net_weight": 0, "rate_per_gram": 0, "calculated_value": 0, "purity_percentage": 0}

    purity_pct = PURITY_VALUES.get(purity, 0)
    metal = metal_type
    if metal in ("White Gold", "Rose Gold"):
        metal = "Yellow Gold"

    rate = _get_gold_rate(metal, purity)
    calculated = round(net_weight * rate, 2)

    return {
        "net_weight": round(net_weight, 3),
        "rate_per_gram": rate,
        "calculated_value": calculated,
        "purity_percentage": purity_pct * 100,
    }


@frappe.whitelist()
def create_gold_purchase(data: dict) -> dict:
    """Create a new Gold Purchase from POS.

    Args:
        data: Dict with customer, store_location, items list, payment_method, etc.
    """
    if isinstance(data, str):
        import json
        data = json.loads(data)

    frappe.has_permission("Gold Purchase", "create", throw=True)

    doc = frappe.get_doc({"doctype": "Gold Purchase", **data})
    doc.insert(ignore_permissions=True)

    return {
        "success": True,
        "name": doc.name,
        "total_calculated_value": doc.total_calculated_value,
        "total_agreed_value": doc.total_agreed_value,
    }


@frappe.whitelist()
def submit_gold_purchase(name: str) -> dict:
    """Submit (finalize) a Gold Purchase, triggering payment and stock entries."""
    frappe.has_permission("Gold Purchase", "submit", throw=True)

    doc = frappe.get_doc("Gold Purchase", name)
    doc.submit()

    return {
        "success": True,
        "name": doc.name,
        "payment_entry": doc.payment_entry,
        "stock_entry": doc.stock_entry,
        "payment_status": doc.payment_status,
    }


@frappe.whitelist()
def get_gold_purchase(name: str) -> dict:
    """Get Gold Purchase details with items."""
    doc = frappe.get_doc("Gold Purchase", name)

    return {
        "name": doc.name,
        "purchase_date": doc.purchase_date,
        "customer": doc.customer,
        "customer_name": doc.customer_name,
        "store_location": doc.store_location,
        "status": doc.status,
        "payment_status": doc.payment_status,
        "total_gross_weight": doc.total_gross_weight,
        "total_net_weight": doc.total_net_weight,
        "total_calculated_value": doc.total_calculated_value,
        "total_agreed_value": doc.total_agreed_value,
        "payment_method": doc.payment_method,
        "payment_entry": doc.payment_entry,
        "stock_entry": doc.stock_entry,
        "items": [
            {
                "metal_type": i.metal_type,
                "purity": i.purity,
                "purity_percentage": i.purity_percentage,
                "gross_weight_g": i.gross_weight_g,
                "stone_weight_g": i.stone_weight_g,
                "net_weight_g": i.net_weight_g,
                "rate_per_gram": i.rate_per_gram,
                "calculated_value": i.calculated_value,
                "agreed_value": i.agreed_value,
                "test_method": i.test_method,
                "test_result": i.test_result,
                "description": i.description,
            }
            for i in doc.items
        ],
    }


@frappe.whitelist()
def get_gold_purchases_list(filters: dict | None = None, limit: int = 20) -> list:
    """Get list of Gold Purchases with basic info."""
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    return frappe.get_all(
        "Gold Purchase",
        fields=["name", "purchase_date", "customer_name", "total_agreed_value", "status", "payment_status", "payment_method"],
        filters=filters or {},
        order_by="purchase_date desc",
        limit_page_length=int(limit),
    )
