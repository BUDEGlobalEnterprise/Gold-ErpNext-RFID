import frappe

def execute():
    item = "00001510"
    
    # All SLEs for this item
    sle = frappe.db.sql("""
        SELECT name, warehouse, posting_date, voucher_type, voucher_no,
               actual_qty, qty_after_transaction
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s
        ORDER BY posting_date DESC, posting_time DESC
        LIMIT 20
    """, (item,), as_dict=True)
    
    print(f"=== All SLEs for {item} ({len(sle)}) ===")
    for s in sle:
        print(f"  {s.warehouse} | {s.posting_date} | {s.voucher_type} {s.voucher_no} | qty={s.actual_qty} | after={s.qty_after_transaction}")
    
    # Bin data
    bins = frappe.db.sql("""
        SELECT warehouse, actual_qty, projected_qty, reserved_qty, reserved_qty_for_production
        FROM `tabBin`
        WHERE item_code = %s
    """, (item,), as_dict=True)
    
    print(f"\n=== Bin data for {item} ===")
    for b in bins:
        print(f"  {b.warehouse}: actual={b.actual_qty} projected={b.projected_qty} reserved={b.reserved_qty} reserved_prod={b.reserved_qty_for_production}")

    # Rebuild bin
    print("\n=== Rebuilding bin... ===")
    from erpnext.stock.utils import update_bin
    for wh in ["Brooklyn Store - ZFJ", "Manhattan Store - ZFJ"]:
        try:
            update_bin({
                "item_code": item,
                "warehouse": wh,
                "doctype": "Bin",
            }, allow_negative_stock=True)
            print(f"  Rebuilt bin for {wh}")
        except Exception as e:
            print(f"  Error rebuilding {wh}: {e}")
    
    # Check after rebuild
    bins2 = frappe.db.sql("""
        SELECT warehouse, actual_qty, projected_qty
        FROM `tabBin`
        WHERE item_code = %s
    """, (item,), as_dict=True)
    
    print(f"\n=== After rebuild ===")
    for b in bins2:
        print(f"  {b.warehouse}: actual={b.actual_qty} projected={b.projected_qty}")
    
    frappe.db.commit()
