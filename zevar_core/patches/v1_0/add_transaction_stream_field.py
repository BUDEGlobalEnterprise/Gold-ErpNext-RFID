import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Sales Invoice": [
			{
				"fieldname": "custom_transaction_stream",
				"label": "Transaction Stream",
				"fieldtype": "Select",
				"options": "Jewelry Sale\nRepair\nLayaway Deposit\nLayaway Final",
				"default": "Jewelry Sale",
				"insert_after": "customer",
				"reqd": 1,
				"read_only_depends_on": "eval:doc.docstatus==1",
				"allow_on_submit": 0,
			}
		],
		"POS Profile": [
			{
				"fieldname": "custom_fixed_opening_float",
				"label": "Fixed Opening Float",
				"fieldtype": "Currency",
				"default": "300.00",
				"insert_after": "company",
				"reqd": 1,
			},
			{
				"fieldname": "custom_enforce_fixed_float",
				"label": "Enforce Fixed Float",
				"fieldtype": "Check",
				"default": "1",
				"insert_after": "custom_fixed_opening_float",
			},
			{
				"fieldname": "custom_float_gl_account",
				"label": "Float GL Account",
				"fieldtype": "Link",
				"options": "Account",
				"default": "Asset — Cash Drawer Float - ZJ",
				"insert_after": "custom_enforce_fixed_float",
			},
			{
				"fieldname": "custom_variance_alert_threshold",
				"label": "Variance Alert Threshold",
				"fieldtype": "Currency",
				"default": "5.00",
				"insert_after": "custom_float_gl_account",
			},
		],
	}

	create_custom_fields(custom_fields)
	frappe.db.commit()
