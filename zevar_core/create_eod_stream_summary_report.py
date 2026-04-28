import frappe


def execute():
	report_name = "EOD Stream Summary"
	if frappe.db.exists("Report", report_name):
		return

	doc = frappe.new_doc("Report")
	doc.report_name = report_name
	doc.ref_doctype = "Sales Invoice"
	doc.report_type = "Script Report"
	doc.is_standard = "Yes"
	doc.module = "Unified Retail Management System"
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
