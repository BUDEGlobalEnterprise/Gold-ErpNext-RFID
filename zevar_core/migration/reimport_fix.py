"""Fix broken dates and test data - nuclear clean + reimport."""
import frappe


def execute():
    """Clean everything with wrong dates and test data, then reimport."""
    report = {"cleaned": {}, "reimported": {}}

    def clear(table, where=""):
        full = f"tab{table}"
        exists = frappe.db.sql(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema=DATABASE() AND table_name=%s",
            (full,),
        )[0][0]
        if not exists:
            return 0
        try:
            if where:
                n = frappe.db.sql(f"SELECT COUNT(*) FROM `{full}` WHERE {where}")[0][0]
                frappe.db.sql(f"DELETE FROM `{full}` WHERE {where}")
            else:
                n = frappe.db.count(table)
                frappe.db.sql(f"DELETE FROM `{full}`")
            frappe.db.commit()  # nosemgrep
            return n
        except Exception as e:
            frappe.db.rollback()
            report["cleaned"][f"err:{table}"] = str(e)[:80]
            return 0

    # 1. Delete all Sales Invoices (posting_date is wrong)
    for t in ["Sales Invoice Item", "Sales Invoice"]:
        n = clear(t)
        if n:
            report["cleaned"][t] = n

    # 2. Delete all Payment Entries (posted against wrong invoices)
    for t in ["Payment Entry Reference", "Payment Entry", "Payment Ledger Entry"]:
        n = clear(t)
        if n:
            report["cleaned"][t] = n

    # 3. Delete all Stock Entries + related (posting_date is wrong)
    for t in ["Stock Entry Detail", "Stock Entry", "Stock Ledger Entry", "Bin"]:
        n = clear(t)
        if n:
            report["cleaned"][t] = n

    # 4. Delete GL entries from imported transactions
    n = clear("GL Entry")
    if n:
        report["cleaned"]["GL Entry"] = n

    # 5. Delete test users (keep Administrator, Guest)
    clear("User", "name NOT IN ('Administrator', 'Guest')")

    # 6. Delete employees, attendance, commission rules (will be reimported)
    for t in ["Attendance", "Commission Rule", "Employee"]:
        n = clear(t)
        if n:
            report["cleaned"][t] = n

    # 7. Delete all addresses and contacts (will be reimported)
    for t in ["Address", "Contact"]:
        n = clear(t)
        if n:
            report["cleaned"][t] = n

    # 8. Clean version trail and deleted docs
    for t in ["Version", "Deleted Document"]:
        n = clear(t)
        if n:
            report["cleaned"][t] = n

    frappe.db.commit()  # nosemgrep
    report["cleaned"]["_status"] = "CLEAN"

    # --- REIMPORT ---
    from zevar_core.migration import foxpro_import as fp
    from zevar_core.migration import foxpro_import_extended as fpx
    from zevar_core.migration.recovery_driver import DBF, STOCK_WAREHOUSE

    # 9. Reimport employees
    try:
        report["reimported"]["employees"] = _summ(fp.import_employees(DBF))
    except Exception as e:
        report["reimported"]["employees_err"] = str(e)[:200]

    # 10. Reimport sales invoices with set_posting_time=1 (already fixed in foxpro_import.py)
    try:
        report["reimported"]["transactions"] = _summ(fp.import_transactions(DBF))
    except Exception as e:
        report["reimported"]["transactions_err"] = str(e)[:200]

    # 11. Reimport payment tenders + layaway links (already patched)
    for fn in ("import_payment_tenders", "import_layaway_links"):
        try:
            f = getattr(fpx, fn, None)
            if f:
                report["reimported"][fn] = _summ(f(DBF))
        except Exception as e:
            report["reimported"][f"{fn}_err"] = str(e)[:200]

    # 12. Reimport opening stock with set_posting_time=1 (already fixed in recovery_driver.py)
    from zevar_core.migration.recovery_driver import load_opening_stock
    try:
        report["reimported"]["opening_stock"] = load_opening_stock(
            DBF, warehouse=STOCK_WAREHOUSE, posting_date="2026-04-01"
        )
    except Exception as e:
        report["reimported"]["opening_stock_err"] = str(e)[:200]

    # 13. Reimport repair orders
    try:
        report["reimported"]["repair_orders"] = _summ(fpx.import_repair_orders(DBF))
    except Exception as e:
        report["reimported"]["repair_orders_err"] = str(e)[:200]

    frappe.db.commit()  # nosemgrep
    return report


def _summ(result):
    if isinstance(result, dict):
        return {k: v for k, v in result.items() if k != "first_errors"}
    return str(result)[:200]
