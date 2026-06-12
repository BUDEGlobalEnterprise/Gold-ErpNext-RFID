"""
Cleanup Test Data Patch

Remove all test/dummy data injected by Frappe/ERPNext test fixtures:
- _Test Customer*, Test Customer, Test POS Customer, etc.
- _Test Item*, Test Item records
- _Test Supplier* records

This preserves real business data (Walk-In Customer, real vendor memo customers, etc.)
"""

import frappe


def execute():
    """Remove test data entries from Customer, Item, and Supplier doctypes."""

    # ── 1. Identify test customers ──
    test_customer_patterns = [
        "_Test%",
        "VerifyTest-%",
        "Test Customer",
        "Test POS Customer",
        "Test Trade-In Customer",
        "Return Test Customer",
        "Integration Test Customer",
        "Zevar E2E Customer",
        "Zevar Reports Test Customer",
        "KYC Test Customer",
        "Form 8300 Test Customer",
        "Test Loyalty Customer",
        "Layaway Test Customer",
        "Layaway Test Cust",
        "Finance Test Cust",
        "Session Test Cust",
    ]

    test_customers = set()
    for pattern in test_customer_patterns:
        if "%" in pattern:
            names = frappe.db.sql(
                "SELECT name FROM tabCustomer WHERE name LIKE %s",
                pattern,
                as_dict=1,
            )
        else:
            names = frappe.db.sql(
                "SELECT name FROM tabCustomer WHERE name = %s",
                pattern,
                as_dict=1,
            )
        for n in names:
            test_customers.add(n["name"])

    # Preserve Walk-In Customer (needed for POS)
    test_customers.discard("Walk-In Customer")

    print(f"Found {len(test_customers)} test customers to remove")

    for cust_name in test_customers:
        try:
            # Check if linked to real invoices
            invoice_count = frappe.db.count(
                "Sales Invoice",
                filters={"customer": cust_name, "docstatus": 1},
            )
            if invoice_count > 0:
                frappe.db.set_value("Customer", cust_name, "disabled", 1)
                print(f"  Disabled customer: {cust_name} - has {invoice_count} submitted invoices")
                continue

            frappe.delete_doc(
                "Customer",
                cust_name,
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
            print(f"  Deleted customer: {cust_name}")
        except Exception as e:
            try:
                frappe.db.set_value("Customer", cust_name, "disabled", 1)
                print(f"  Disabled customer: {cust_name} - delete failed: {e}")
            except Exception:
                print(f"  WARN: Could not delete {cust_name}: {e}")

    # ── 2. Identify test items ──
    test_item_patterns = ["_Test%", "TEST-RES-%", "ZEVAR-REPORT-%", "ZEVAR-E2E-%", "ZEVAR-CART-DIS-%"]
    test_items = set()
    for pattern in test_item_patterns:
        names = frappe.db.sql(
            "SELECT name FROM tabItem WHERE name LIKE %s",
            pattern,
            as_dict=1,
        )
        for n in names:
            test_items.add(n["name"])

    print(f"Found {len(test_items)} test items to remove")

    for item_name in test_items:
        try:
            # Check if linked to real stock entries or invoices
            sle_count = frappe.db.count(
                "Stock Ledger Entry",
                filters={"item_code": item_name, "is_cancelled": 0},
            )
            si_count = frappe.db.count(
                "Sales Invoice Item",
                filters={"item_code": item_name, "docstatus": 1},
            )
            if sle_count > 0 or si_count > 0:
                frappe.db.set_value("Item", item_name, "disabled", 1)
                print(f"  Disabled item: {item_name} - has {sle_count} SLEs, {si_count} invoice items")
                continue

            frappe.delete_doc(
                "Item",
                item_name,
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
            print(f"  Deleted item: {item_name}")
        except Exception as e:
            try:
                frappe.db.set_value("Item", item_name, "disabled", 1)
                print(f"  Disabled item: {item_name} - delete failed: {e}")
            except Exception:
                print(f"  WARN: Could not delete {item_name}: {e}")

    # ── 3. Identify test suppliers ──
    test_supplier_names = frappe.db.sql(
        "SELECT name FROM tabSupplier WHERE name LIKE '_Test%%'",
        as_dict=1,
    )
    print(f"Found {len(test_supplier_names)} test suppliers to remove")

    for sup in test_supplier_names:
        try:
            frappe.delete_doc(
                "Supplier",
                sup["name"],
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
            print(f"  Deleted supplier: {sup['name']}")
        except Exception as e:
            print(f"  WARN: Could not delete {sup['name']}: {e}")

    # ── 4. Clean up test customer groups ──
    test_groups = frappe.db.sql(
        "SELECT name FROM `tabCustomer Group` WHERE name LIKE '_Test%%'",
        as_dict=1,
    )
    for grp in test_groups:
        try:
            frappe.delete_doc(
                "Customer Group",
                grp["name"],
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
            print(f"  Deleted customer group: {grp['name']}")
        except Exception:
            pass  # May have children, skip silently

    # ── 5. Clean up test territories ──
    test_territories = frappe.db.sql(
        "SELECT name FROM tabTerritory WHERE name LIKE '_Test%%'",
        as_dict=1,
    )
    for ter in test_territories:
        try:
            frappe.delete_doc(
                "Territory",
                ter["name"],
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
            print(f"  Deleted territory: {ter['name']}")
        except Exception:
            pass

    # ── 6. Clean invalid legacy/imported rate rows that break live-rate widgets ──
    invalid_rate_logs = frappe.db.sql(
        """
        SELECT name
        FROM `tabGold Rate Log`
        WHERE source = 'Legacy Import'
            AND (metal IS NULL OR purity IS NULL OR IFNULL(rate_per_gram, 0) <= 0)
        """,
        as_dict=1,
    )
    print(f"Found {len(invalid_rate_logs)} invalid legacy gold rate logs to remove")
    for row in invalid_rate_logs:
        try:
            frappe.delete_doc(
                "Gold Rate Log",
                row["name"],
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
            print(f"  Deleted invalid gold rate log: {row['name']}")
        except Exception as e:
            print(f"  WARN: Could not delete invalid gold rate log {row['name']}: {e}")

    frappe.db.commit()
    print("Test data cleanup complete.")
