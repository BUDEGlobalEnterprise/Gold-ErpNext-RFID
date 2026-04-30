import frappe


def create_eod_calendar_page():
	page_name = "eod-calendar"
	if not frappe.db.exists("Page", page_name):
		doc = frappe.new_doc("Page")
		doc.page_name = page_name
		doc.title = "EOD Analytics Calendar"
		doc.module = "Unified Retail Management System"
		doc.standard = "Yes"
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Created page: {page_name}")


create_eod_calendar_page()
