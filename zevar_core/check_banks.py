import frappe

def execute():
    banks = frappe.get_all("Account", filters={"account_type": "Bank", "company": "Zevar Fine Jewelers"}, fields=["name"])
    print("=== Bank Accounts for ZFJ ===")
    for b in banks:
        print(f"  {b.name}")
    if not banks:
        print("  (none found)")
