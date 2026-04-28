import frappe
from frappe.utils import flt


def execute():
	company = "Zevar Jewelers"
	if not frappe.db.exists("Company", company):
		return

	accounts = [
		{
			"account_name": "Income — Repair Services",
			"parent_account": f"Direct Income - ZJ",
			"account_type": "Income Account",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Liability — Layaway Deposits Held",
			"parent_account": f"Current Liabilities - ZJ",
			"account_type": "",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Asset — A/R Synchrony",
			"parent_account": f"Accounts Receivable - ZJ",
			"account_type": "Receivable",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Asset — A/R AFF",
			"parent_account": f"Accounts Receivable - ZJ",
			"account_type": "Receivable",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Asset — A/R CIMA",
			"parent_account": f"Accounts Receivable - ZJ",
			"account_type": "Receivable",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Asset — A/R Progressive",
			"parent_account": f"Accounts Receivable - ZJ",
			"account_type": "Receivable",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Asset — A/R Snap",
			"parent_account": f"Accounts Receivable - ZJ",
			"account_type": "Receivable",
			"company": company,
			"is_group": 0,
		},
		{
			"account_name": "Asset — Cash Drawer Float",
			"parent_account": f"Cash In Hand - ZJ",
			"account_type": "Cash",
			"company": company,
			"is_group": 0,
		},
	]

	for acc in accounts:
		account_id = f"{acc['account_name']} - ZJ"
		if not frappe.db.exists("Account", account_id):
			doc = frappe.new_doc("Account")
			doc.update(acc)
			doc.insert(ignore_permissions=True)

	# Seed an opening JV of $300 per POS Profile
	setup_register_floats(company)


def setup_register_floats(company):
	"""Seed an opening JV of $300 per POS Profile for Cash Drawer Float"""
	pos_profiles = frappe.get_all("POS Profile", filters={"company": company}, fields=["name"])

	if not pos_profiles:
		return

	cash_float_account = f"Asset — Cash Drawer Float - ZJ"
	# Need a generic temporary account for opening entry, like "Temporary Opening - ZJ"
	temp_account = f"Temporary Opening - ZJ"

	if not frappe.db.exists("Account", cash_float_account) or not frappe.db.exists("Account", temp_account):
		return

	for profile in pos_profiles:
		# Check if JV already exists for this POS profile
		existing_jv = frappe.db.exists(
			"Journal Entry",
			{
				"voucher_type": "Opening Entry",
				"user_remark": f"Opening float for POS Register {profile.name}",
			},
		)

		if not existing_jv:
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Opening Entry"
			je.company = company
			je.posting_date = frappe.utils.today()
			je.user_remark = f"Opening float for POS Register {profile.name}"

			je.append(
				"accounts",
				{
					"account": cash_float_account,
					"debit_in_account_currency": 300.0,
					"credit_in_account_currency": 0.0,
				},
			)

			je.append(
				"accounts",
				{
					"account": temp_account,
					"debit_in_account_currency": 0.0,
					"credit_in_account_currency": 300.0,
				},
			)

			je.save(ignore_permissions=True)
			je.submit()
