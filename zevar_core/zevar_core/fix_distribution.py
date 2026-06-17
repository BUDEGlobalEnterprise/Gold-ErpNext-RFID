import frappe

COMPANY = "Zevar Fine Jewelers"
ABBR = "ZFJ"

STORES = [
    {"code": "MHT", "name": "Manhattan Store", "warehouse": "Manhattan Store - ZFJ"},
    {"code": "BKN", "name": "Brooklyn Store", "warehouse": "Brooklyn Store - ZFJ"},
    {"code": "QNS", "name": "Queens Store", "warehouse": "Queens Store - ZFJ"},
    {"code": "MDT", "name": "Midtown Store", "warehouse": "Midtown Store - ZFJ"},
    {"code": "SOH", "name": "SoHo Store", "warehouse": "SoHo Store - ZFJ"},
]

def main():
    frappe.init(site="zevar.localhost", sites_path="sites")
    frappe.connect()

    try:
        # 1. Create missing POS Profiles
        print("--- Fixing POS Profiles ---")
        payment_modes = ["Cash", "Credit Card", "Debit Card", "Check", "Wire Transfer", "Zelle"]
        for store in STORES:
            profile_name = f"{store['name']} POS"
            if not frappe.db.exists("POS Profile", profile_name):
                pos = frappe.new_doc("POS Profile")
                pos.name = profile_name
                pos.pos_profile_name = profile_name
                pos.company = COMPANY
                pos.warehouse = store["warehouse"]

                # Account fallbacks
                pos.write_off_account = frappe.db.get_value("Account", {"company": COMPANY, "account_name": "Write Off"}, "name")
                if not pos.write_off_account:
                    pos.write_off_account = frappe.db.sql("SELECT name FROM tabAccount WHERE company=%s AND root_type='Expense' AND is_group=0 LIMIT 1", COMPANY)[0][0]
                
                pos.write_off_cost_center = frappe.db.sql("SELECT name FROM `tabCost Center` WHERE company=%s AND is_group=0 LIMIT 1", COMPANY)[0][0]
                pos.currency = frappe.db.get_value("Company", COMPANY, "default_currency") or "USD"
                pos.selling_price_list = frappe.db.get_value("Price List", {"selling": 1}, "name") or "Standard Selling"

                for mode in payment_modes:
                    if frappe.db.exists("Mode of Payment", mode):
                        pos.append("payments", {"mode_of_payment": mode, "default": 1 if mode == "Cash" else 0})

                try:
                    pos.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
                    print(f"Created POS Profile: {profile_name}")
                except Exception as e:
                    print(f"Skipping POS Profile {profile_name} due to error: {e}")
            
            # Link POS profile to Store Location
            if frappe.db.exists("Store Location", {"store_code": store["code"]}):
                frappe.db.set_value("Store Location", {"store_code": store["code"]}, "pos_profile", profile_name)

        # 2. Distribute Inventory
        print("--- Distributing Inventory ---")
        source_wh = f"Manhattan Store - {ABBR}"

        # Get all bins currently in Manhattan
        bins = frappe.db.sql("""
            SELECT item_code, actual_qty, valuation_rate, stock_value
            FROM `tabBin`
            WHERE warehouse = %s AND actual_qty > 0
            ORDER BY item_code
        """, source_wh, as_dict=True)

        total_items = len(bins)
        if total_items > 0:
            chunk_size = total_items // 5
            remainder = total_items % 5
            idx = 0

            # Direct SQL distribution
            for i, store in enumerate(STORES):
                size = chunk_size + (1 if i < remainder else 0)
                items = bins[idx:idx + size]
                idx += size

                if store["code"] == "MHT":
                    continue # Manhattan keeps its slice

                for item in items:
                    ic = item["item_code"]
                    qty = item["actual_qty"]
                    rate = item.get("valuation_rate") or 1
                    val = item.get("stock_value") or (qty * rate)

                    # Insert or update bin for target store
                    if not frappe.db.exists("Bin", {"item_code": ic, "warehouse": store["warehouse"]}):
                        frappe.db.sql("""
                            INSERT INTO `tabBin` (name, creation, modified, item_code, warehouse, actual_qty, valuation_rate, stock_value)
                            VALUES (%s, NOW(), NOW(), %s, %s, %s, %s, %s)
                        """, (frappe.generate_hash(length=10), ic, store["warehouse"], qty, rate, val))
                    else:
                        frappe.db.sql("UPDATE `tabBin` SET actual_qty=%s, valuation_rate=%s, stock_value=%s WHERE item_code=%s AND warehouse=%s",
                                      (qty, rate, val, ic, store["warehouse"]))

                    # Zero out in Manhattan
                    frappe.db.sql("UPDATE `tabBin` SET actual_qty=0, stock_value=0 WHERE item_code=%s AND warehouse=%s", (ic, source_wh))

                    # Update Item Default
                    existing_def = frappe.db.get_value("Item Default", {"parent": ic, "company": COMPANY}, "name")
                    if existing_def:
                        frappe.db.set_value("Item Default", existing_def, "default_warehouse", store["warehouse"])
                    else:
                        frappe.db.sql("""
                            INSERT INTO `tabItem Default` (name, parent, parenttype, parentfield, company, default_warehouse)
                            VALUES (%s, %s, 'Item', 'item_defaults', %s, %s)
                        """, (frappe.generate_hash(length=10), ic, COMPANY, store["warehouse"]))

                print(f"Assigned {len(items)} items to {store['name']}")

        frappe.db.commit()

        # Print final distribution
        print("--- Final Distribution ---")
        for store in STORES:
            res = frappe.db.sql("SELECT COUNT(*) as cnt, COALESCE(SUM(actual_qty), 0) as qty FROM tabBin WHERE warehouse=%s AND actual_qty>0", store["warehouse"], as_dict=True)
            print(f"{store['name']}: {res[0]['cnt']} items, {res[0]['qty']} qty")
            
        print("Done.")

    finally:
        frappe.destroy()

if __name__ == "__main__":
    main()
