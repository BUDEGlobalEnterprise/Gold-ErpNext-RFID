import frappe


def execute():
	if not frappe.db.exists("Page", "case-audit"):
		doc = frappe.get_doc(
			{
				"doctype": "Page",
				"page_name": "case-audit",
				"title": "Case Audit",
				"module": "Unified Retail Management System",
				"standard": "Yes",
				"roles": [{"role": "Sales User"}, {"role": "Sales Manager"}, {"role": "System Manager"}],
			}
		)
		doc.insert(ignore_permissions=True)
	frappe.db.commit()
