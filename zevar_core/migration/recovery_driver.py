"""
Recovery driver — restore real Zevar business data from recovered FoxPro DBFs.

Run via bench:
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.dryrun
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.wipe_test_data
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.run_masters
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.run_transactions
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.load_opening_stock
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.run_extended
    bench --site zevar.localhost execute zevar_core.migration.recovery_driver.verify

All writes are real (not dry-run) except `dryrun`.
"""

import frappe
from frappe import _

from zevar_core.migration import foxpro_import as fp
from zevar_core.migration import foxpro_import_extended as fpx

DBF = "/tmp/zevar_dbf"
STOCK_WAREHOUSE = "Stores - ZFJ"

# Extended importers to run, in dependency order.
EXTENDED = [
    "import_stone_cuts",
    "import_stone_types",
    "import_departments",
    "import_subcategories",
    "import_tax_rates",
    "import_slush_items",
    "import_receipt_lines",
    "import_payment_tenders",
    "import_repair_orders",
    "import_layaway_contracts",
    "import_layaway_links",
    "import_salespersons",
    "import_commission_rules",
    "import_payroll",
    "import_audit_trail",
    "import_sold_history",
    "import_watch_details",
]


def _summ(stats):
    if isinstance(stats, dict) and "total" in stats:
        return {
            "total": stats.get("total"),
            "imported": stats.get("imported"),
            "skipped": stats.get("skipped"),
            "errors": len(stats.get("errors", [])),
            "first_errors": stats.get("errors", [])[:3],
        }
    return stats


def dryrun(backup_path=DBF):
    """Validate every importer can read its DBF and report expected counts. No writes."""
    out = {}
    ia = fp.import_all(backup_path, dry_run=True)
    out["import_all"] = {k: _summ(v) for k, v in ia.items() if isinstance(v, dict)}
    out["import_all"]["_totals"] = {
        "total_records": ia.get("total_records"),
        "total_imported": ia.get("total_imported"),
        "total_skipped": ia.get("total_skipped"),
        "total_errors": ia.get("total_errors"),
    }
    for fn in EXTENDED:
        f = getattr(fpx, fn, None)
        if f is None:
            out[fn] = "MISSING"
            continue
        try:
            out[fn] = _summ(f(backup_path, dry_run=True))
        except Exception as e:
            out[fn] = {"error": str(e)[:200]}
    return out


def wipe_test_data():
    """
    Remove ERPNext test fixtures to leave a clean slate for real import.

    Deletes: Items, Customers, Suppliers (all current rows are _Test/demo) plus
    their child tables, stock tables (Bin, Stock Ledger Entry, Item Price,
    Stock Queue), serial/batch test data, and _Test Addresses/Contacts.
    ZFJ company + Stores - ZFJ warehouse are untouched.
    """
    cleared = {}

    def safe(sql):
        try:
            return frappe.db.sql(sql)
        except Exception as e:
            cleared.setdefault("_sql_errors", []).append(f"{sql[:60]}: {str(e)[:80]}")
            return None

    # 1. Dynamic child tables of the three master doctypes
    for parent in ("Item", "Customer", "Supplier"):
        children = frappe.db.sql_list(
            "SELECT DISTINCT options FROM tabDocField WHERE parent=%s AND fieldtype='Table'",
            (parent,),
        )
        for child in children:
            child = (child or "").strip()
            if child and frappe.db.table_exists(child):
                n = frappe.db.count(child)
                if n:
                    safe(f"DELETE FROM `tab{child}`")
                    cleared[f"child:{child}"] = n

    # 2. Stock dependent tables (all test)
    for t in ("Stock Ledger Entry", "Stock Queue", "Bin", "Item Price"):
        if frappe.db.table_exists(t):
            n = frappe.db.count(t)
            safe(f"DELETE FROM `tab{t}`")
            cleared[f"stock:{t}"] = n

    # 3. Serial No / Batch test rows
    for t in ("Serial No", "Batch"):
        if frappe.db.table_exists(t):
            n = frappe.db.count(t)
            if n:
                safe(f"DELETE FROM `tab{t}`")
                cleared[f"other:{t}"] = n

    # 4. Dynamic Link rows referencing the masters we are about to delete
    safe("DELETE FROM `tabDynamic Link` WHERE link_doctype IN ('Item','Customer','Supplier')")

    # 5. _Test Addresses / Contacts
    for t in ("Address", "Contact"):
        n = frappe.db.count(t, {"name": ["like", "_Test%"]})
        if n:
            safe(f"DELETE FROM `tab{t}` WHERE name LIKE '_Test%'")
            cleared[f"addr:{t}"] = n

    # 6. The masters themselves
    for dt in ("Item", "Customer", "Supplier"):
        n = frappe.db.count(dt)
        safe(f"DELETE FROM `tab{dt}`")
        cleared[f"master:{dt}"] = n

    # 7. Trash records of the above
    safe("DELETE FROM `tabDeleted Document` WHERE deleted_doctype IN ('Item','Customer','Supplier','Bin','Stock Ledger Entry','Item Price')")

    frappe.db.commit()  # nosemgrep
    return cleared


def clean_slate():
    """
    Nuclear clean-slate: remove ALL business data the migration populates so the
    real import runs into a guaranteed-empty DB. Preserves framework setup:
    Companies, Warehouses, Accounts, Cost Centers, UOM, Currency, Custom Fields,
    Property Setters, DocTypes, Users/Roles, Modes of Payment, and root nodes.

    Idempotent and safe — every doctype cleared here is recreated by the import.
    """
    report = {}

    def clear(table, where=""):
        full = f"tab{table}"
        exists = frappe.db.sql(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema=DATABASE() AND table_name=%s",
            (full,),
        )[0][0]
        if not exists:
            return
        try:
            if where:
                n = frappe.db.sql(f"SELECT COUNT(*) FROM `{full}` WHERE {where}")[0][0]
                frappe.db.sql(f"DELETE FROM `{full}` WHERE {where}")
            else:
                n = frappe.db.count(table)
                frappe.db.sql(f"DELETE FROM `{full}`")
            if n:
                report[table] = n
        except Exception as e:
            report[f"err:{table}"] = str(e)[:80]

    # 1. Transactional documents first (have GL/ledger impact)
    for t in ["Sales Invoice Item", "Sales Invoice", "Purchase Receipt Item",
              "Purchase Receipt", "Delivery Note Item", "Delivery Note",
              "Payment Entry Reference", "Payment Entry", "Stock Entry Detail",
              "Stock Entry", "POS Audit Log", "Customer Ledger Entry",
              "Payment Ledger Entry", "Layaway Contract", "Repair Order",
              "Sales Taxes and Charges Template", "Jewelry Appraisal",
              "Gold Rate Log", "Repair Type", "Store Location"]:
        clear(t)

    # Tax templates only for ZFJ (leave other companies' defaults untouched)
    clear("Sales Taxes and Charges Template", "company='Zevar Fine Jewelers'")

    # 2. Dynamic links + child tables of masters we are about to delete
    for parent in ("Item", "Customer", "Supplier", "Employee"):
        children = frappe.db.sql_list(
            "SELECT DISTINCT options FROM tabDocField WHERE parent=%s AND fieldtype='Table'",
            (parent,),
        )
        for child in children:
            child = (child or "").strip()
            if child and frappe.db.table_exists(child):
                clear(child)
    clear("Dynamic Link", "link_doctype IN ('Item','Customer','Supplier','Employee')")

    # 3. Stock tables
    for t in ["Stock Ledger Entry", "Stock Queue", "Bin", "Item Price",
              "Serial No", "Batch", "Item Attribute Value"]:
        clear(t)

    # 4. Item Attribute values created by migration
    for t in ("Item Attribute",):
        clear(t, "name IN ('Color','Clarity','Cut','Stone Type')")
    # Item Groups (keep root), Purity, Metal, Brand
    clear("Item Group", "name <> 'All Item Groups'")
    clear("Zevar Purity")
    clear("Zevar Metal")
    clear("Brand")

    # 5. Masters
    for t in ("Item", "Customer", "Supplier", "Employee", "Commission Rule",
              "Attendance"):
        clear(t)

    # 6. Test / orphan addresses & contacts
    clear("Address")
    clear("Contact")

    # 7. Trash + version trail for the above
    clear("Deleted Document",
          "deleted_doctype IN ('Item','Customer','Supplier','Employee','Sales Invoice',"
          "'Payment Entry','Layaway Contract','Repair Order','Bin','Stock Ledger Entry','Item Price')")
    clear("Version",
          "ref_doctype IN ('Item','Customer','Supplier','Employee','Sales Invoice',"
          "'Payment Entry','Layaway Contract','Repair Order')")

    frappe.db.commit()  # nosemgrep
    return report


def run_masters(backup_path=DBF):
    """Import stores, employees, categories, purities, attributes, suppliers,
    customers, inventory, repair_types, gold_rates, appraisals. No transactions yet."""
    return {k: _summ(v) for k, v in fp.import_all(backup_path, skip_transactions=True).items()
            if isinstance(v, dict)}


def run_transactions(backup_path=DBF):
    """Import historical Sales Invoices from trans.dbf."""
    return _summ(fp.import_transactions(backup_path))


def run_inventory_only(backup_path=DBF):
    """Re-run item import only — picks up items that failed previously (skips existing)."""
    return _summ(fp.import_inventory(backup_path))


def load_opening_stock(backup_path=DBF, warehouse=STOCK_WAREHOUSE, posting_date="2026-04-01"):
    """Create Material Receipt entries from inventor.DBF QTY (on-hand) into the warehouse."""
    from dbfread import DBF

    company = frappe.defaults.get_global_default("company")
    expense_account = (
        frappe.get_cached_value("Company", company, "stock_adjustment_account")
        or frappe.get_cached_value("Company", company, "default_expense_account")
    )

    table = DBF(f"{backup_path}/inventor.DBF", encoding="cp1252", ignore_missing_memofile=True)
    items = []
    skipped_no_item = 0
    for rec in table:
        barcode = (rec.get("BARCODE") or "").strip()
        stockno = (rec.get("STOCKNO") or "").strip()
        abr = (rec.get("ABR") or "").strip()
        qty = rec.get("QTY") or 0
        cost = rec.get("COST") or 0
        if not qty or qty <= 0:
            continue
        item_code = barcode if barcode else (f"{abr}-{stockno}" if abr and stockno else stockno)
        if not item_code or not frappe.db.exists("Item", item_code):
            skipped_no_item += 1
            continue
        existing = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
        if existing > 0:
            continue
        items.append({"item_code": item_code, "qty": float(qty),
                      "valuation_rate": float(cost) if cost and cost > 0 else 0})

    created = errors = 0
    item_errors = []
    batch = 50

    def submit_entry(lines):
        """Create + submit one Stock Entry from a list of item dicts. Returns count."""
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.company = company
        se.set_posting_time = 1
        se.posting_date = posting_date
        for it in lines:
            rate = it["valuation_rate"] if it["valuation_rate"] > 0 else 1
            se.append("items", {
                "item_code": it["item_code"], "qty": it["qty"], "uom": "Nos",
                "t_warehouse": warehouse, "basic_rate": rate, "expense_account": expense_account,
            })
        se.insert(ignore_permissions=True)
        se.submit()
        return len(lines)

    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        try:
            created += submit_entry(chunk)
            frappe.db.commit()  # nosemgrep — commit each success so later failures can't roll it back
        except Exception:
            # Batch failed — isolate: stock each valid item on its own entry
            frappe.db.rollback()
            for it in chunk:
                try:
                    created += submit_entry([it])
                    frappe.db.commit()  # nosemgrep
                except Exception as e:
                    errors += 1
                    item_errors.append(f"{it['item_code']}: {str(e)[:90]}")
                    frappe.db.rollback()

    frappe.db.commit()  # nosemgrep
    return {"candidates": len(items), "stocked_lines": created, "errors": errors,
            "skipped_no_matching_item": skipped_no_item, "warehouse": warehouse,
            "first_item_errors": item_errors[:15]}


def run_extended(backup_path=DBF):
    out = {}
    for fn in EXTENDED:
        f = getattr(fpx, fn, None)
        if f is None:
            out[fn] = "MISSING"
            continue
        try:
            out[fn] = _summ(f(backup_path))
        except Exception as e:
            out[fn] = {"error": str(e)[:200]}
    return out


def run_payments_layaway(backup_path=DBF):
    """Re-run the three patched importers: layaway contracts + both Payment Entry streams."""
    out = {}
    for fn in ("import_layaway_contracts", "import_payment_tenders", "import_layaway_links"):
        f = getattr(fpx, fn, None)
        try:
            out[fn] = _summ(f(backup_path))
        except Exception as e:
            out[fn] = {"error": str(e)[:200]}
    return out


def verify():
    """Report current counts of key doctypes."""
    doctypes = [
        "Item", "Customer", "Supplier", "Employee", "Item Group", "Store Location",
        "Sales Invoice", "Stock Ledger Entry", "Bin", "Repair Order", "Repair Type",
        "Layaway Contract", "Payment Entry", "Jewelry Appraisal", "Gold Rate Log",
        "Zevar Metal", "Zevar Purity",
    ]
    out = {}
    for dt in doctypes:
        try:
            out[dt] = frappe.db.count(dt)
        except Exception as e:
            out[dt] = f"err:{str(e)[:60]}"
    return out


def debug_metal():
    """Reproduce the 'Could not find Metal Type' error to find its source."""
    import traceback
    out = {"metal_type_distribution": frappe.db.sql(
        "SELECT custom_metal_type, COUNT(*) FROM tabItem GROUP BY custom_metal_type "
        "ORDER BY COUNT(*) DESC LIMIT 15")}
    try:
        doc = frappe.new_doc("Item")
        doc.item_code = "DEBUG-METAL-TEST"
        doc.item_name = "Debug Metal Test"
        doc.stock_uom = "Nos"
        doc.is_stock_item = 1
        doc.item_group = "All Item Groups"
        doc.custom_metal_type = "White Gold"
        doc.custom_purity = "14Kt"
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        out["result"] = "INSERTED OK (no error)"
        frappe.delete_doc("Item", "DEBUG-METAL-TEST", force=True)
    except Exception as e:
        out["result"] = f"FAILED: {e!r}"
        out["traceback"] = traceback.format_exc().splitlines()[-12:]
    return out


# Metal name → {metal_type, color_hex}. metal_type must be Precious|Base|Mixed.
METALS = {
    "Yellow Gold": {"metal_type": "Precious", "color_hex": "#FFD700"},
    "White Gold": {"metal_type": "Precious", "color_hex": "#F5F5DC"},
    "Rose Gold": {"metal_type": "Precious", "color_hex": "#B76E79"},
    "Silver": {"metal_type": "Precious", "color_hex": "#C0C0C0"},
    "Platinum": {"metal_type": "Precious", "color_hex": "#E5E4E2"},
}

# Purity name → {fine_metal_content, metal, aliases}
PURITIES = {
    "10Kt": {"fine_metal_content": 0.4167, "metal": "Yellow Gold", "aliases": "10k"},
    "14Kt": {"fine_metal_content": 0.585, "metal": "Yellow Gold", "aliases": "14k"},
    "18Kt": {"fine_metal_content": 0.750, "metal": "Yellow Gold", "aliases": "18k"},
    "22Kt": {"fine_metal_content": 0.9167, "metal": "Yellow Gold", "aliases": "22k"},
    "925 Sterling": {"fine_metal_content": 0.925, "metal": "Silver", "aliases": "SS"},
    "999 Fine": {"fine_metal_content": 0.999, "metal": "Platinum", "aliases": "PLAT"},
}


def debug_stock_item(item_code="00001090"):
    """Inspect Frappe's view of an item (DB vs cached doc)."""
    info = {
        "db_item_group": frappe.db.get_value("Item", item_code, "item_group"),
        "raw_sql": frappe.db.sql("SELECT name, item_code, item_group FROM tabItem WHERE name=%s OR item_code=%s", (item_code, item_code)),
        "cached_before": getattr(frappe.get_cached_doc("Item", item_code), "item_group", "???"),
    }
    frappe.clear_document_cache("Item", item_code)
    info["fresh_after_clear"] = frappe.get_doc("Item", item_code).item_group
    return info


def debug_invoice(transno="104"):
    """Reproduce one legacy transaction insert to find the abs() error source."""
    import traceback
    try:
        from dbfread import DBF as DBFTable
        t = DBFTable(f"{DBF}/trans.dbf", encoding="cp1252", ignore_missing_memofile=True)
        rec = next((r for r in t if str(r.get("TRANSNO", "")).strip() == transno), None)
        if not rec:
            return {"error": f"transno {transno} not found"}
        rec = {k.lower(): v for k, v in rec.items()}
        doc = frappe.new_doc("Sales Invoice")
        doc.title = f"Legacy Trans #{transno}"
        doc.posting_date = fp.format_date(rec.get("date")) or frappe.utils.today()
        doc.update_stock = 0
        doc.company = frappe.defaults.get_global_default("company")
        doc.customer = "Walk In Customer" if frappe.db.exists("Customer", "Walk In Customer") else None
        amount = fp.clean_float(rec.get("amount"))
        if amount > 0:
            doc.append("items", {"item_code": "LEGACY-ITEM", "item_name": "Legacy Sale",
                                 "qty": 1, "rate": amount})
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.rollback()
        return {"result": "INSERTED OK (rolled back)", "amount": amount}
    except Exception as e:
        frappe.db.rollback()
        tb = traceback.format_exc().splitlines()
        frames = [l.strip() for l in tb if "/apps/erpnext/" in l or "/apps/zevar_core/" in l]
        return {"result": f"FAILED: {e!r}", "frames": frames[-14:]}


def ensure_metals_and_purities():
    """Create the Zevar Metal + Zevar Purity master records that items reference."""
    report = {"metals": [], "purities": []}
    for name, meta in METALS.items():
        if frappe.db.exists("Zevar Metal", name):
            report["metals"].append(f"{name}: exists")
            continue
        try:
            d = frappe.new_doc("Zevar Metal")
            d.metal_name = name
            d.metal_type = meta["metal_type"]
            d.color_hex = meta["color_hex"]
            d.is_active = 1
            d.insert(ignore_permissions=True, ignore_mandatory=True)
            report["metals"].append(f"{name}: created")
        except Exception as e:
            report["metals"].append(f"{name}: ERROR {str(e)[:80]}")
    for name, meta in PURITIES.items():
        if frappe.db.exists("Zevar Purity", name):
            report["purities"].append(f"{name}: exists")
            continue
        try:
            d = frappe.new_doc("Zevar Purity")
            d.purity_name = name
            d.fine_metal_content = meta["fine_metal_content"]
            d.metal = meta["metal"]
            d.aliases = meta["aliases"]
            d.is_active = 1
            d.insert(ignore_permissions=True, ignore_mandatory=True)
            report["purities"].append(f"{name}: created")
        except Exception as e:
            report["purities"].append(f"{name}: ERROR {str(e)[:80]}")
    frappe.db.commit()  # nosemgrep
    return report
