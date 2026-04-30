import frappe


def create_audit_page():
	if not frappe.db.exists("Page", "case-audit-page"):
		doc = frappe.get_doc(
			{
				"doctype": "Page",
				"page_name": "case-audit-page",
				"module": "Unified Retail Management System",
				"title": "Case Audit",
				"standard": "Yes",
			}
		)
		doc.insert(ignore_permissions=True)

		# Add roles
		for role in ["System Manager", "Sales Manager", "Cashier", "Owner"]:
			if frappe.db.exists("Role", role):
				doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)

		frappe.db.commit()
		print("Page created successfully.")
	else:
		print("Page already exists.")
