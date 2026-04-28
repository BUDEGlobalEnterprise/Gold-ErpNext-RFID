import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Item": [
			{
				"fieldname": "custom_rfid_epc",
				"label": "RFID EPC",
				"fieldtype": "Data",
				"insert_after": "item_code",
				"unique": 1,
				"description": "Unique Electronic Product Code for RFID tracking",
			}
		]
	}

	create_custom_fields(custom_fields)
	frappe.db.commit()
