import frappe


def execute():
	financiers = {
		"Synchrony": "Asset — A/R Synchrony - ZJ",
		"AFF": "Asset — A/R AFF - ZJ",
		"CIMA": "Asset — A/R CIMA - ZJ",
		"Progressive": "Asset — A/R Progressive - ZJ",
		"Snap": "Asset — A/R Snap - ZJ",
	}
	company = "Zevar Jewelers"

	for mode, account in financiers.items():
		if not frappe.db.exists("Mode of Payment", mode):
			continue

		doc = frappe.get_doc("Mode of Payment", mode)
		doc.type = "General"

		# Check if an account for this company is already set
		account_exists = False
		for acc in doc.accounts:
			if acc.company == company:
				acc.default_account = account
				account_exists = True
				break

		if not account_exists:
			doc.append("accounts", {"company": company, "default_account": account})

		doc.save(ignore_permissions=True)
