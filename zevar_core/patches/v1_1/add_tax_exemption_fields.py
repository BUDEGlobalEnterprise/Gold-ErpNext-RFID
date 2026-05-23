import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Sales Invoice": [
			{
				"fieldname": "custom_tax_exemption_status",
				"label": "Tax Exemption Status",
				"fieldtype": "Select",
				"options": "\nPending\nApproved\nRejected",
				"insert_after": "custom_tax_override_reason",
				"read_only": 1,
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_tax_exemption_log",
				"label": "Tax Exemption Log",
				"fieldtype": "Link",
				"options": "POS Tax Exemption Log",
				"insert_after": "custom_tax_exemption_status",
				"read_only": 1,
				"allow_on_submit": 1,
			},
		],
		"POS Profile": [
			{
				"fieldname": "custom_is_activated",
				"label": "Is Activated",
				"fieldtype": "Check",
				"default": 0,
				"insert_after": "disabled",
			},
			{
				"fieldname": "custom_activated_by",
				"label": "Activated By",
				"fieldtype": "Link",
				"options": "User",
				"insert_after": "custom_is_activated",
				"read_only": 1,
			},
			{
				"fieldname": "custom_activated_at",
				"label": "Activated At",
				"fieldtype": "Datetime",
				"insert_after": "custom_activated_by",
				"read_only": 1,
			},
			{
				"fieldname": "custom_auto_deactivate_time",
				"label": "Auto Deactivate Time",
				"fieldtype": "Time",
				"insert_after": "custom_activated_at",
				"description": "Time of day to auto-deactivate this POS profile (e.g. 22:00 for 10 PM close). Leave empty for no auto-deactivation.",
			},
		],
	}

	create_custom_fields(custom_fields)
	frappe.db.commit()
