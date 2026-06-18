import frappe

def execute():
    # Check for float-related accounts
    accounts = frappe.get_all("Account", filters={"company": "Zevar Fine Jewelers"}, fields=["name", "account_type", "is_group"], order_by="name")
    print("=== All Accounts for Zevar Fine Jewelers ===")
    for a in accounts:
        print(f"  {a.name} | type={a.account_type} | group={a.is_group}")
