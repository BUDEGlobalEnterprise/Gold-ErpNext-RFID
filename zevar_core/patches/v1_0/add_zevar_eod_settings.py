import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"POS Settings": [
			{
				"fieldname": "zevar_eod_section",
				"fieldtype": "Section Break",
				"label": "Zevar EOD",
			},
			{
				"fieldname": "custom_yoy_compare_mode",
				"fieldtype": "Select",
				"label": "YoY Compare Mode",
				"options": "Exact Date\nISO Weekday Matched",
				"default": "Exact Date",
				"insert_after": "zevar_eod_section",
			},
			{
				"fieldname": "enable_fixed_float",
				"fieldtype": "Check",
				"label": "Enable Fixed Float",
				"default": "1",
				"insert_after": "custom_yoy_compare_mode",
			},
			{
				"fieldname": "enable_stream_segregation",
				"fieldtype": "Check",
				"label": "Enable Stream Segregation",
				"default": "1",
				"insert_after": "enable_fixed_float",
			},
			{
				"fieldname": "enable_rfid_audit",
				"fieldtype": "Check",
				"label": "Enable RFID Audit",
				"default": "1",
				"insert_after": "enable_stream_segregation",
			},
			{
				"fieldname": "enable_eod_calendar",
				"fieldtype": "Check",
				"label": "Enable EOD Calendar",
				"default": "1",
				"insert_after": "enable_rfid_audit",
			},
		]
	}
	create_custom_fields(custom_fields, update=True)
