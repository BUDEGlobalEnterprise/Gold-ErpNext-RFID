import frappe


def execute():
	exists = frappe.db.exists("DocType", "POS Manager Override")
	print(f"POS Manager Override exists: {exists}")
