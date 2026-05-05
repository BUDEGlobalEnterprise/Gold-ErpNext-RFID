"""
Bootstrap all missing Mode of Payment records, account mappings, custom fields.

Fixes:
- Missing Mode of Payment records (Apple Pay, Google Pay, Venmo, etc.)
- Missing account mappings for Zevar Jewelers company
- Missing Liability — Layaway Deposits Held account
- Missing financier A/R accounts
- Missing POS custom fields on Sales Invoice
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		frappe.logger().warning("bootstrap_payment_modes: No default company found, skipping.")
		return

	abbr = frappe.get_cached_value("Company", company, "abbr")

	_ensure_pos_custom_fields()
	_ensure_layaway_liability_account(company, abbr)
	_ensure_financier_accounts(company, abbr)
	_ensure_all_modes_of_payment(company, abbr)


def _ensure_pos_custom_fields():
	pos_custom_fields = {
		"Sales Invoice": [
			{
				"fieldname": "custom_transaction_stream",
				"label": "Transaction Stream",
				"fieldtype": "Select",
				"options": "Jewelry Sale\nRepair\nLayaway Deposit\nLayaway Final",
				"default": "Jewelry Sale",
				"insert_after": "customer",
				"allow_on_submit": 0,
			},
			{
				"fieldname": "custom_no_tax_override",
				"label": "No Tax Override",
				"fieldtype": "Check",
				"insert_after": "custom_transaction_stream",
			},
			{
				"fieldname": "custom_layaway_reference",
				"label": "Layaway Reference",
				"fieldtype": "Link",
				"options": "Layaway Contract",
				"insert_after": "custom_no_tax_override",
			},
			{
				"fieldname": "custom_salesperson_1",
				"label": "Salesperson 1",
				"fieldtype": "Link",
				"options": "Employee",
				"insert_after": "custom_layaway_reference",
			},
			{
				"fieldname": "custom_salesperson_1_split",
				"label": "Salesperson 1 Split %",
				"fieldtype": "Percent",
				"insert_after": "custom_salesperson_1",
			},
			{
				"fieldname": "custom_salesperson_2",
				"label": "Salesperson 2",
				"fieldtype": "Link",
				"options": "Employee",
				"insert_after": "custom_salesperson_1_split",
			},
			{
				"fieldname": "custom_salesperson_2_split",
				"label": "Salesperson 2 Split %",
				"fieldtype": "Percent",
				"insert_after": "custom_salesperson_2",
			},
			{
				"fieldname": "custom_salesperson_3",
				"label": "Salesperson 3",
				"fieldtype": "Link",
				"options": "Employee",
				"insert_after": "custom_salesperson_2_split",
			},
			{
				"fieldname": "custom_salesperson_3_split",
				"label": "Salesperson 3 Split %",
				"fieldtype": "Percent",
				"insert_after": "custom_salesperson_3",
			},
			{
				"fieldname": "custom_salesperson_4",
				"label": "Salesperson 4",
				"fieldtype": "Link",
				"options": "Employee",
				"insert_after": "custom_salesperson_3_split",
			},
			{
				"fieldname": "custom_salesperson_4_split",
				"label": "Salesperson 4 Split %",
				"fieldtype": "Percent",
				"insert_after": "custom_salesperson_4",
			},
		],
	}

	child_table_fields = {
		"Sales Invoice": [
			{
				"fieldname": "custom_salesperson_splits",
				"label": "Salesperson Splits",
				"fieldtype": "Table",
				"options": "Sales Commission Split",
				"insert_after": "custom_salesperson_4_split",
			},
			{
				"fieldname": "custom_trade_ins",
				"label": "Trade-Ins",
				"fieldtype": "Table",
				"options": "Trade In Record",
				"insert_after": "custom_salesperson_splits",
			},
		],
	}

	all_fields = {}
	for dt, fields in pos_custom_fields.items():
		existing = all_fields.setdefault(dt, [])
		existing.extend(fields)
	for dt, fields in child_table_fields.items():
		existing = all_fields.setdefault(dt, [])
		existing.extend(fields)

	try:
		create_custom_fields(all_fields)
		frappe.db.commit()
	except Exception:
		frappe.log_error("bootstrap: Failed to create POS custom fields")


def _ensure_layaway_liability_account(company, abbr):
	account_name = f"Liability — Layaway Deposits Held - {abbr}"
	if frappe.db.exists("Account", account_name):
		return

	root_liability = frappe.db.get_value(
		"Account",
		{"root_type": "Liability", "is_group": 1, "company": company},
		"name",
		order_by="lft asc",
	)
	if not root_liability:
		frappe.logger().warning(
			f"bootstrap_payment_modes: No root liability account found for {company}"
		)
		return

	parent = root_liability
	parent_is_group = frappe.db.get_value("Account", root_liability, "is_group")
	if not parent_is_group:
		return

	try:
		acc = frappe.new_doc("Account")
		acc.account_name = "Liability — Layaway Deposits Held"
		acc.company = company
		acc.parent_account = parent
		acc.account_type = ""
		acc.is_group = 0
		acc.insert(ignore_permissions=True)
		frappe.logger().info(f"bootstrap_payment_modes: Created {acc.name}")
	except Exception:
		frappe.log_error("bootstrap_payment_modes: Failed to create Layaway Liability Account")


def _ensure_financier_accounts(company, abbr):
	financier_accounts = {
		"Synchrony": "Asset — A/R Synchrony",
		"AFF": "Asset — A/R AFF",
		"CIMA": "Asset — A/R CIMA",
		"Progressive": "Asset — A/R Progressive",
		"Snap": "Asset — A/R Snap",
	}

	root_asset = frappe.db.get_value(
		"Account",
		{"root_type": "Asset", "is_group": 1, "company": company},
		"name",
		order_by="lft asc",
	)
	if not root_asset:
		return

	for _mode, account_name in financier_accounts.items():
		full_name = f"{account_name} - {abbr}"
		if frappe.db.exists("Account", full_name):
			continue

		try:
			acc = frappe.new_doc("Account")
			acc.account_name = account_name
			acc.company = company
			acc.parent_account = root_asset
			acc.account_type = "Receivable"
			acc.is_group = 0
			acc.insert(ignore_permissions=True)
			frappe.logger().info(f"bootstrap_payment_modes: Created {acc.name}")
		except Exception:
			frappe.log_error(
				f"bootstrap_payment_modes: Failed to create {full_name}",
			)


def _ensure_all_modes_of_payment(company, abbr):
	cash_account = frappe.db.get_value(
		"Account", {"account_type": "Cash", "company": company}, "name"
	)
	if not cash_account:
		cash_account = frappe.db.get_value(
			"Account",
			{"account_name": "Cash", "company": company},
			"name",
		)

	bank_accounts = frappe.get_all(
		"Account",
		filters={"account_type": "Bank", "company": company, "is_group": 0},
		pluck="name",
		limit=1,
	)
	bank_account = bank_accounts[0] if bank_accounts else cash_account

	financier_account_map = {
		"Synchrony": f"Asset — A/R Synchrony - {abbr}",
		"AFF": f"Asset — A/R AFF - {abbr}",
		"CIMA": f"Asset — A/R CIMA - {abbr}",
		"Progressive": f"Asset — A/R Progressive - {abbr}",
		"Snap": f"Asset — A/R Snap - {abbr}",
	}

	modes = [
		{"mode_of_payment": "Cash", "type": "Cash", "account": cash_account},
		{"mode_of_payment": "Credit Card", "type": "Bank", "account": bank_account},
		{"mode_of_payment": "Debit Card", "type": "Bank", "account": bank_account},
		{"mode_of_payment": "Check", "type": "Bank", "account": bank_account},
		{"mode_of_payment": "Wire Transfer", "type": "Bank", "account": bank_account},
		{"mode_of_payment": "Zelle", "type": "General", "account": cash_account},
		{"mode_of_payment": "Gift Card", "type": "General", "account": cash_account},
		{"mode_of_payment": "Trade-In", "type": "General", "account": cash_account},
		{"mode_of_payment": "Apple Pay", "type": "Bank", "account": bank_account},
		{"mode_of_payment": "Google Pay", "type": "Bank", "account": bank_account},
		{"mode_of_payment": "Venmo", "type": "General", "account": cash_account},
		{"mode_of_payment": "Cash App", "type": "General", "account": cash_account},
		{"mode_of_payment": "Synchrony", "type": "General", "account": financier_account_map.get("Synchrony")},
		{"mode_of_payment": "AFF", "type": "General", "account": financier_account_map.get("AFF")},
		{"mode_of_payment": "CIMA", "type": "General", "account": financier_account_map.get("CIMA")},
		{"mode_of_payment": "Progressive", "type": "General", "account": financier_account_map.get("Progressive")},
		{"mode_of_payment": "Snap", "type": "General", "account": financier_account_map.get("Snap")},
		{"mode_of_payment": "In-House Finance", "type": "General", "account": cash_account},
	]

	for mode_def in modes:
		mode_name = mode_def["mode_of_payment"]
		target_account = mode_def["account"]

		if frappe.db.exists("Mode of Payment", mode_name):
			doc = frappe.get_doc("Mode of Payment", mode_name)
		else:
			doc = frappe.new_doc("Mode of Payment")
			doc.mode_of_payment = mode_name
			doc.type = mode_def["type"]
			doc.enabled = 1

		doc.type = mode_def["type"]

		account_exists = False
		for acc in doc.accounts:
			if acc.company == company:
				if target_account and frappe.db.exists("Account", target_account):
					acc.default_account = target_account
				account_exists = True
				break

		if not account_exists and target_account:
			if frappe.db.exists("Account", target_account):
				doc.append("accounts", {"company": company, "default_account": target_account})

		try:
			doc.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(
				f"bootstrap_payment_modes: Failed to save Mode of Payment '{mode_name}'"
			)

	frappe.db.commit()
