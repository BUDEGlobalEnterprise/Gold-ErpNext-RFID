import frappe

def execute():
    stale = frappe.get_all("POS Opening Entry", filters={"docstatus": 1, "status": "Open"}, fields=["name"])
    for entry in stale:
        doc = frappe.get_doc("POS Opening Entry", entry.name)
        if doc.docstatus == 1:
            doc.cancel()
        frappe.delete_doc("POS Opening Entry", entry.name, ignore_permissions=True)
        print(f"Deleted: {entry.name}")

    frappe.db.commit()
    print("Done!")
