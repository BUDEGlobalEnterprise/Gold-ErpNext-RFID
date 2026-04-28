import frappe


def execute():
	accounts = frappe.get_all(
		"Account",
		filters={"parent_account": "Temporary Accounts - ZJ", "is_group": 0},
		fields=["name", "account_type"],
	)
	print(f"TEMP NON-GROUP: {accounts}")
