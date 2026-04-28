import frappe


def execute():
	frappe.db.set_value("Account", "Liability — Layaway Deposits Held - ZJ", "account_type", "Receivable")
	frappe.db.commit()
