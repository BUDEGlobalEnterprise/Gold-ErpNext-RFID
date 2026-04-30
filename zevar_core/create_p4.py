import frappe


def create_number_cards():
	cards = ["Synchrony", "AFF", "CIMA", "Progressive", "Snap"]
	for financier in cards:
		name = f"AR - {financier} (Today)"
		label = f"A/R — {financier} (Today)"
		if not frappe.db.exists("Number Card", name):
			doc = frappe.new_doc("Number Card")
			doc.name = name
			doc.label = label
			doc.document_type = "GL Entry"
			doc.function = "Sum"
			doc.aggregate_function_based_on = "debit"
			doc.filters_json = f'[("GL Entry", "account", "=", "Asset — A/R {financier} - ZJ", False), ("GL Entry", "posting_date", "=", "Today", False)]'
			doc.is_standard = 0
			doc.module = "Unified Retail Management System"
			doc.insert(ignore_permissions=True)
			print(f"Created number card: {name}")
	frappe.db.commit()
