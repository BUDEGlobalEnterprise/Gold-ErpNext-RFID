import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"POS Settings": [
			{
				"fieldname": "custom_max_salesperson_splits",
				"label": "Max Salesperson Splits",
				"fieldtype": "Int",
				"default": 4,
				"insert_after": "pos_profile",
				"description": "Maximum number of salespeople that can be assigned to a single sale for commission splitting.",
			},
		],
	}

	create_custom_fields(custom_fields)
	frappe.db.commit()
