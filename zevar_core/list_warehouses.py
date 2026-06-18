import frappe

def execute():
    groups = frappe.get_all("Warehouse", filters={"is_group": 1}, fields=["name"], order_by="name")
    print("=== Group (parent) Warehouses ===")
    for g in groups:
        children = frappe.get_all("Warehouse", filters={"parent_warehouse": g.name, "is_group": 0}, fields=["name"])
        print(f"\n{g.name} ({len(children)} children):")
        for c in children:
            print(f"  {c.name}")
