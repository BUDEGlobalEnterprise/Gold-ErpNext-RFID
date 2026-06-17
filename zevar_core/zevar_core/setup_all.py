"""
All-in-one cleanup and store setup script.
Uses direct SQL with FK checks disabled for speed.
"""
import frappe
from frappe.utils.nestedset import rebuild_tree


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
    # =============================================
    # PHASE 1: Delete orphan warehouses
    # =============================================
    print("=" * 60)
    print("PHASE 1: Delete Orphaned Warehouses")
    print("=" * 60)

    orphans = [
        "QW RT Warehouse - ZFJ", "QW BF Warehouse - ZFJ", "QW5 Warehouse - ZFJ",
        "QW7 Store WH - ZFJ", "QW7B Store WH - ZFJ", "M0 RT WH - ZFJ",
        "SCB SC WH - ZFJ", "WIF WH - ZFJ", "ROLL WH - ZFJ",
    ]

    frappe.db.sql("SET FOREIGN_KEY_CHECKS=0")

    # Clean SLEs and Bins for warehouses with entries
    for wh in orphans:
        frappe.db.sql("DELETE FROM `tabStock Ledger Entry` WHERE warehouse = %s", wh)
        frappe.db.sql("DELETE FROM `tabBin` WHERE warehouse = %s", wh)
        frappe.db.sql("DELETE FROM `tabWarehouse` WHERE name = %s", wh)
        print(f"  ✓ Deleted: {wh}")

    frappe.db.sql("SET FOREIGN_KEY_CHECKS=1")
    frappe.db.commit()
    print("Phase 1 complete.\n")

    # =============================================
    # PHASE 2: Delete all test companies
    # =============================================
    print("=" * 60)
    print("PHASE 2: Delete All Test/Junk Companies")
    print("=" * 60)

    test_companies = frappe.db.sql(
        "SELECT name FROM `tabCompany` WHERE name != %s", COMPANY, as_dict=True
    )
    print(f"  Found {len(test_companies)} junk companies to delete.")

    frappe.db.sql("SET FOREIGN_KEY_CHECKS=0")

    # Get all DocTypes that have a 'company' field
    company_linked_tables = frappe.db.sql("""
        SELECT DISTINCT parent
        FROM `tabDocField`
        WHERE fieldname = 'company' AND fieldtype = 'Link'
        AND parent IN (SELECT name FROM `tabDocType` WHERE istable = 0)
    """, as_dict=True)

    for tc in test_companies:
        cn = tc["name"]

        # Delete from all tables that have a company field
        for dt in company_linked_tables:
            table_name = f"tab{dt['parent']}"
            try:
                frappe.db.sql(f"DELETE FROM `{table_name}` WHERE company = %s", cn)
            except Exception:
                pass

        # Also clean child tables that reference these companies
        # Warehouses
        frappe.db.sql("DELETE FROM `tabWarehouse` WHERE company = %s", cn)
        # Accounts
        frappe.db.sql("DELETE FROM `tabAccount` WHERE company = %s", cn)
        # Cost Centers
        frappe.db.sql("DELETE FROM `tabCost Center` WHERE company = %s", cn)
        # Departments
        try:
            frappe.db.sql("DELETE FROM `tabDepartment` WHERE company = %s", cn)
        except Exception:
            pass
        # Company itself
        frappe.db.sql("DELETE FROM `tabCompany` WHERE name = %s", cn)
        print(f"  ✓ Purged: {cn}")

    frappe.db.sql("SET FOREIGN_KEY_CHECKS=1")
    frappe.db.commit()

    remaining = frappe.db.sql("SELECT name FROM `tabCompany`", as_dict=True)
    print(f"\n  Remaining companies: {[c['name'] for c in remaining]}")
    print("Phase 2 complete.\n")

    # =============================================
    # PHASE 3: Create warehouse hierarchy
    # =============================================
    print("=" * 60)
    print("PHASE 3: Create 5-Store Warehouse Hierarchy")
    print("=" * 60)

    parent_group = f"All Warehouses - {ABBR}"

    # Create Store Warehouses group
    group_name = f"Store Warehouses - {ABBR}"
    if not frappe.db.exists("Warehouse", group_name):
        grp = frappe.new_doc("Warehouse")
        grp.warehouse_name = "Store Warehouses"
        grp.is_group = 1
        grp.parent_warehouse = parent_group
        grp.company = COMPANY
        grp.insert(ignore_permissions=True)
        print(f"  ✓ Created group: {grp.name}")
    else:
        print(f"  - Already exists: {group_name}")

    # Rename "Stores - ZFJ" → "Manhattan Store - ZFJ"
    old_name = "Stores - ZFJ"
    new_name = f"Manhattan Store - {ABBR}"
    if frappe.db.exists("Warehouse", old_name):
        frappe.db.set_value("Warehouse", old_name, {
            "warehouse_name": "Manhattan Store",
            "parent_warehouse": group_name,
        })
        frappe.rename_doc("Warehouse", old_name, new_name, force=True)
        print(f"  ✓ Renamed: {old_name} → {new_name}")
    elif frappe.db.exists("Warehouse", new_name):
        frappe.db.set_value("Warehouse", new_name, "parent_warehouse", group_name)
        print(f"  - Already renamed: {new_name}")

    # Create the other 4 stores
    for store in STORES[1:]:
        wh_name = store["warehouse"]
        if not frappe.db.exists("Warehouse", wh_name):
            wh = frappe.new_doc("Warehouse")
            wh.warehouse_name = store["name"]
            wh.parent_warehouse = group_name
            wh.company = COMPANY
            wh.insert(ignore_permissions=True)
            print(f"  ✓ Created: {wh.name}")
        else:
            print(f"  - Already exists: {wh_name}")

    rebuild_tree("Warehouse", "parent_warehouse")
    frappe.db.commit()
    print("Phase 3 complete.\n")

    # =============================================
    # PHASE 4: Create POS Profiles
    # =============================================
    print("=" * 60)
    print("PHASE 4: Create POS Profiles Per Store")
    print("=" * 60)

    payment_modes = ["Cash", "Credit Card", "Debit Card", "Check", "Wire Transfer", "Zelle"]

    # Delete old Default POS
    if frappe.db.exists("POS Profile", "Default POS"):
        frappe.delete_doc("POS Profile", "Default POS", force=True, ignore_permissions=True)
        print("  ✓ Deleted old 'Default POS'")

    for store in STORES:
        profile_name = f"{store['name']} POS"
        if frappe.db.exists("POS Profile", profile_name):
            print(f"  - Already exists: {profile_name}")
            continue

        pos = frappe.new_doc("POS Profile")
        pos.pos_profile_name = profile_name
        pos.company = COMPANY
        pos.warehouse = store["warehouse"]

        # Find required accounts
        pos.write_off_account = frappe.db.get_value(
            "Account", {"company": COMPANY, "account_name": "Write Off"}, "name"
        ) or frappe.db.get_value(
            "Account", {"company": COMPANY, "root_type": "Expense", "is_group": 0}, "name"
        ) or ""

        pos.write_off_cost_center = frappe.db.get_value(
            "Cost Center", {"company": COMPANY, "is_group": 0}, "name"
        ) or ""

        pos.currency = frappe.db.get_value("Company", COMPANY, "default_currency") or "USD"
        pos.selling_price_list = frappe.db.get_value(
            "Price List", {"selling": 1}, "name"
        ) or "Standard Selling"

        for mode in payment_modes:
            if frappe.db.exists("Mode of Payment", mode):
                pos.append("payments", {
                    "mode_of_payment": mode,
                    "default": 1 if mode == "Cash" else 0,
                })

        try:
            pos.insert(ignore_permissions=True, ignore_mandatory=True)
            print(f"  ✓ Created: {profile_name} → {store['warehouse']}")
        except Exception as e:
            print(f"  ✗ Failed: {profile_name}: {e}")

    frappe.db.commit()
    print("Phase 4 complete.\n")

    # =============================================
    # PHASE 5: Replace Store Location records
    # =============================================
    print("=" * 60)
    print("PHASE 5: Replace Store Location Records")
    print("=" * 60)

    # Delete all old store locations (display cases)
    old_count = frappe.db.count("Store Location")
    if old_count:
        frappe.db.sql("DELETE FROM `tabStore Location`")
        # Also clean child tables
        for child in ["Store Location Workshop", "Store Location Bench Vendor"]:
            if frappe.db.exists("DocType", child):
                try:
                    frappe.db.sql(f"DELETE FROM `tab{child}`")
                except Exception:
                    pass
        print(f"  ✓ Deleted {old_count} old display-case locations")

    addresses = [
        "47 W 47th St, New York, NY 10036",
        "216 Atlantic Ave, Brooklyn, NY 11201",
        "37-01 Main St, Flushing, NY 11354",
        "580 5th Ave, New York, NY 10036",
        "95 Grand St, New York, NY 10013",
    ]

    for i, store in enumerate(STORES):
        pos_name = f"{store['name']} POS"
        sl = frappe.new_doc("Store Location")
        sl.store_code = store["code"]
        sl.store_name = store["name"]
        sl.is_active = 1
        sl.default_warehouse = store["warehouse"]
        sl.store_address = addresses[i]
        if frappe.db.exists("POS Profile", pos_name):
            sl.pos_profile = pos_name
        try:
            sl.insert(ignore_permissions=True)
            print(f"  ✓ Created: {store['code']} - {store['name']}")
        except Exception as e:
            print(f"  ✗ Failed: {store['code']}: {e}")

    frappe.db.commit()
    print("Phase 5 complete.\n")

    # =============================================
    # PHASE 6: Distribute inventory evenly
    # =============================================
    print("=" * 60)
    print("PHASE 6: Distribute Inventory Across 5 Stores")
    print("=" * 60)

    source_wh = f"Manhattan Store - {ABBR}"

    # Get all items with stock
    bins = frappe.db.sql("""
        SELECT item_code, actual_qty, valuation_rate, stock_value
        FROM `tabBin`
        WHERE warehouse = %s AND actual_qty > 0
        ORDER BY item_code
    """, source_wh, as_dict=True)

    total_items = len(bins)
    total_qty = sum(b["actual_qty"] for b in bins)
    print(f"  Items with stock in {source_wh}: {total_items}")
    print(f"  Total quantity: {total_qty}")

    if total_items == 0:
        print("  No items to distribute. Skipping.")
        frappe.db.commit()
        _print_final_verification()
        return

    # Split into 5 groups
    chunk_size = total_items // 5
    remainder = total_items % 5
    assignments = []
    idx = 0
    for i, store in enumerate(STORES):
        size = chunk_size + (1 if i < remainder else 0)
        items = bins[idx:idx + size]
        assignments.append((store, items))
        idx += size
        print(f"  {store['name']}: assigned {len(items)} items")

    # Use direct Bin manipulation (dev environment, fastest approach)
    print("\n  Distributing via direct Bin updates...")

    for store, items in assignments:
        if store["code"] == "MHT":
            # Manhattan keeps its items — no change needed
            continue

        for item in items:
            ic = item["item_code"]
            qty = item["actual_qty"]
            rate = item.get("valuation_rate") or 1
            val = item.get("stock_value") or (qty * rate)

            # Create Bin in new warehouse
            existing_bin = frappe.db.exists("Bin", {"item_code": ic, "warehouse": store["warehouse"]})
            if not existing_bin:
                new_bin = frappe.new_doc("Bin")
                new_bin.item_code = ic
                new_bin.warehouse = store["warehouse"]
                new_bin.actual_qty = qty
                new_bin.valuation_rate = rate
                new_bin.stock_value = val
                new_bin.db_insert()
            else:
                frappe.db.sql("""
                    UPDATE `tabBin` SET actual_qty = %s, valuation_rate = %s, stock_value = %s
                    WHERE item_code = %s AND warehouse = %s
                """, (qty, rate, val, ic, store["warehouse"]))

            # Zero out in Manhattan
            frappe.db.sql("""
                UPDATE `tabBin` SET actual_qty = 0, stock_value = 0
                WHERE item_code = %s AND warehouse = %s
            """, (ic, source_wh))

    # Update Item Defaults
    print("  Updating Item Default warehouses...")
    for store, items in assignments:
        for item in items:
            existing_default = frappe.db.get_value(
                "Item Default",
                {"parent": item["item_code"], "company": COMPANY},
                "name",
            )
            if existing_default:
                frappe.db.set_value(
                    "Item Default", existing_default, "default_warehouse", store["warehouse"]
                )
            else:
                frappe.db.sql("""
                    INSERT INTO `tabItem Default` (name, parent, parenttype, parentfield, company, default_warehouse)
                    VALUES (%s, %s, 'Item', 'item_defaults', %s, %s)
                """, (frappe.generate_hash(length=10), item["item_code"], COMPANY, store["warehouse"]))

    frappe.db.commit()
    print("Phase 6 complete.\n")

    _print_final_verification()


def _print_final_verification():
    print("=" * 60)
    print("FINAL VERIFICATION")
    print("=" * 60)

    # Companies
    companies = frappe.db.sql("SELECT name FROM `tabCompany`", as_dict=True)
    print(f"\n  Companies: {[c['name'] for c in companies]}")

    # Warehouses
    print("\n  Warehouse Tree:")
    whs = frappe.get_all("Warehouse", filters={"company": COMPANY},
                         fields=["name", "parent_warehouse", "is_group"], order_by="lft asc")
    for w in whs:
        indent = "    " if w.get("parent_warehouse") else "  "
        if w.get("parent_warehouse") and w["parent_warehouse"] != f"All Warehouses - {ABBR}":
            indent = "      "
        g = " [GROUP]" if w.get("is_group") else ""
        print(f"{indent}{w['name']}{g}")

    # Stock per warehouse
    print("\n  Stock Distribution:")
    for store in STORES:
        result = frappe.db.sql("""
            SELECT COUNT(*) as cnt, COALESCE(SUM(actual_qty), 0) as qty
            FROM `tabBin`
            WHERE warehouse = %s AND actual_qty > 0
        """, store["warehouse"], as_dict=True)
        r = result[0] if result else {"cnt": 0, "qty": 0}
        print(f"    {store['name']}: {int(r['cnt'])} items, {int(r['qty'])} qty")

    # Total
    total = frappe.db.sql("""
        SELECT COUNT(*) as cnt, COALESCE(SUM(actual_qty), 0) as qty
        FROM `tabBin`
        WHERE warehouse LIKE %s AND actual_qty > 0
    """, f"% - {ABBR}", as_dict=True)
    t = total[0] if total else {"cnt": 0, "qty": 0}
    print(f"    TOTAL: {int(t['cnt'])} items, {int(t['qty'])} qty")

    # Store Locations
    print("\n  Store Locations:")
    sls = frappe.get_all("Store Location",
                         fields=["store_code", "store_name", "default_warehouse", "pos_profile"])
    for sl in sls:
        print(f"    {sl['store_code']}: {sl['store_name']} → {sl.get('default_warehouse')} | POS: {sl.get('pos_profile')}")

    # POS Profiles
    print("\n  POS Profiles:")
    pps = frappe.get_all("POS Profile", filters={"company": COMPANY},
                         fields=["name", "warehouse"])
    for pp in pps:
        print(f"    {pp['name']} → {pp['warehouse']}")

    print("\n✅ All phases complete!")
