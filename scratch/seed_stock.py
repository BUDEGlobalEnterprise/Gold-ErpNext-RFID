"""Bulk-add 15 of every stock item to the POS warehouse (Stores - ZFJ) for testing."""
import frappe
from frappe.utils import today


def main():
    company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
    WH = "Stores - ZFJ"
    items = frappe.get_all("Item", filters={"is_stock_item": 1, "disabled": 0}, pluck="name")
    CHUNK = 250
    done = 0
    for i in range(0, len(items), CHUNK):
        batch = items[i:i + CHUNK]
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.purpose = "Material Receipt"
        se.company = company
        se.set_posting_time = 1
        se.posting_date = today()
        for code in batch:
            se.append("items", {
                "item_code": code, "t_warehouse": WH, "qty": 15,
                "basic_rate": frappe.db.get_value("Item", code, "valuation_rate") or frappe.db.get_value("Item", code, "standard_rate") or 100.0,
                "conversion_factor": 1.0, "stock_uom": "Nos", "uom": "Nos",
            })
        se.insert(ignore_permissions=True)
        se.submit()
        frappe.db.commit()
        done += len(batch)
        print(f"STOCKPROGRESS {done}/{len(items)}", flush=True)
    print(f"STOCKDONE {done} items x 15 into {WH}", flush=True)
    return {"done": done, "warehouse": WH}
