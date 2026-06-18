import frappe

def execute():
    # Find bins where actual_qty > 0 but no SLEs exist
    bins = frappe.db.sql("""
        SELECT b.name, b.item_code, b.warehouse, b.actual_qty, b.projected_qty
        FROM `tabBin` b
        WHERE b.warehouse LIKE '%- ZFJ'
        AND b.actual_qty > 0
    """, as_dict=True)
    
    corrupted = []
    for b in bins:
        sle_count = frappe.db.count("Stock Ledger Entry", {
            "item_code": b.item_code,
            "warehouse": b.warehouse,
        })
        if sle_count == 0:
            corrupted.append(b)
    
    if corrupted:
        print(f"=== Found {len(corrupted)} corrupted bins ===")
        for b in corrupted:
            print(f"  {b.item_code} @ {b.warehouse}: actual={b.actual_qty}, projected={b.projected_qty}")
            # Delete stale bins
            frappe.delete_doc("Bin", b.name, ignore_permissions=True)
            print(f"    Deleted: {b.name}")
    else:
        print("No corrupted bins found.")
    
    frappe.db.commit()
    
    # Verify remaining ZFJ bins
    remaining = frappe.db.sql("""
        SELECT b.item_code, b.warehouse, b.actual_qty, b.projected_qty
        FROM `tabBin` b
        WHERE b.warehouse LIKE '%- ZFJ'
        AND b.actual_qty > 0
        ORDER BY b.warehouse, b.item_code
    """, as_dict=True)
    print(f"\n=== Remaining ZFJ bins with stock ({len(remaining)}) ===")
    for r in remaining:
        print(f"  {r.item_code} @ {r.warehouse}: actual={r.actual_qty} projected={r.projected_qty}")
