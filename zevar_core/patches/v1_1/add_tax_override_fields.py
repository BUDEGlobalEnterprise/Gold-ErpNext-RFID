import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Sales Invoice": [
			{
				"fieldname": "custom_tax_override_approved_by",
				"label": "Tax Override Approved By",
				"fieldtype": "Link",
				"options": "User",
				"insert_after": "custom_no_tax_override",
				"read_only": 1,
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_tax_override_reason",
				"label": "Tax Override Reason",
				"fieldtype": "Small Text",
				"insert_after": "custom_tax_override_approved_by",
				"read_only": 1,
				"allow_on_submit": 1,
			},
		],
	}

	create_custom_fields(custom_fields)
	frappe.db.commit()
