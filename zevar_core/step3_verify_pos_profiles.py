import frappe

def execute():
    profiles = frappe.get_all("POS Profile", fields=["name", "warehouse"])
    for p in profiles:
        print(f"  {p.name} -> {p.warehouse}")
