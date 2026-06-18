import frappe

def execute():
    mops = frappe.get_all("Mode of Payment", fields=["name"])
    print("=== Mode of Payments ===")
    for m in mops:
        doc = frappe.get_doc("Mode of Payment", m.name)
        print(f"\n{m.name}:")
        for a in doc.accounts:
            print(f"  account={a.default_account} company={a.company}")
