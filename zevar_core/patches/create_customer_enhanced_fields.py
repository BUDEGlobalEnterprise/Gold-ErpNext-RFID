"""
Create customer custom fields for enhanced POS customer modal.

Adds fields for: extra details, sizes, shipping address preferences.

Run: bench --site <site> execute zevar_core.patches.create_customer_enhanced_fields.execute
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	customer_fields = {
		"Customer": [
			{
				"fieldname": "custom_extra_details_section",
				"label": "Extra Details",
				"fieldtype": "Section Break",
				"insert_after": "custom_anniversary",
				"collapsible": 1,
			},
			{
				"fieldname": "custom_gender",
				"label": "Gender",
				"fieldtype": "Select",
				"options": "\nMale\nFemale\nOther",
				"insert_after": "custom_extra_details_section",
			},
			{
				"fieldname": "custom_birth_date",
				"label": "Birth Date",
				"fieldtype": "Date",
				"insert_after": "custom_gender",
			},
			{
				"fieldname": "custom_profession",
				"label": "Profession",
				"fieldtype": "Data",
				"insert_after": "custom_birth_date",
			},
			{
				"fieldname": "custom_phone2",
				"label": "Phone 2",
				"fieldtype": "Data",
				"insert_after": "custom_profession",
			},
			{
				"fieldname": "custom_internal_notes",
				"label": "Internal Notes",
				"fieldtype": "Small Text",
				"insert_after": "custom_phone2",
			},
			{
				"fieldname": "custom_accepts_marketing",
				"label": "Accepts Email Marketing",
				"fieldtype": "Check",
				"insert_after": "custom_internal_notes",
			},
			{
				"fieldname": "cb_extra_details",
				"label": "",
				"fieldtype": "Column Break",
				"insert_after": "custom_accepts_marketing",
			},
			{
				"fieldname": "custom_partner_name",
				"label": "Partner Name",
				"fieldtype": "Data",
				"insert_after": "cb_extra_details",
			},
			{
				"fieldname": "custom_partner_phone",
				"label": "Partner Phone",
				"fieldtype": "Data",
				"insert_after": "custom_partner_name",
			},
			{
				"fieldname": "custom_partner_email",
				"label": "Partner Email",
				"fieldtype": "Data",
				"insert_after": "custom_partner_phone",
			},
			{
				"fieldname": "custom_marriage_date",
				"label": "Marriage Date",
				"fieldtype": "Date",
				"insert_after": "custom_partner_email",
			},
			{
				"fieldname": "custom_sizes_section",
				"label": "Body Sizes",
				"fieldtype": "Section Break",
				"insert_after": "custom_marriage_date",
				"collapsible": 1,
			},
			{
				"fieldname": "custom_ring_left_size",
				"label": "Ring Left Size",
				"fieldtype": "Data",
				"insert_after": "custom_sizes_section",
			},
			{
				"fieldname": "custom_ring_right_size",
				"label": "Ring Right Size",
				"fieldtype": "Data",
				"insert_after": "custom_ring_left_size",
			},
			{
				"fieldname": "custom_middle_left_size",
				"label": "Middle Left Size",
				"fieldtype": "Data",
				"insert_after": "custom_ring_right_size",
			},
			{
				"fieldname": "custom_middle_right_size",
				"label": "Middle Right Size",
				"fieldtype": "Data",
				"insert_after": "custom_middle_left_size",
			},
			{
				"fieldname": "custom_index_left_size",
				"label": "Index Left Size",
				"fieldtype": "Data",
				"insert_after": "custom_middle_right_size",
			},
			{
				"fieldname": "custom_index_right_size",
				"label": "Index Right Size",
				"fieldtype": "Data",
				"insert_after": "custom_index_left_size",
			},
			{
				"fieldname": "cb_sizes_2",
				"label": "",
				"fieldtype": "Column Break",
				"insert_after": "custom_index_right_size",
			},
			{
				"fieldname": "custom_pink_left_size",
				"label": "Pink Left Size",
				"fieldtype": "Data",
				"insert_after": "cb_sizes_2",
			},
			{
				"fieldname": "custom_pink_right_size",
				"label": "Pink Right Size",
				"fieldtype": "Data",
				"insert_after": "custom_pink_left_size",
			},
			{
				"fieldname": "custom_thumb_left_size",
				"label": "Thumb Left Size",
				"fieldtype": "Data",
				"insert_after": "custom_pink_right_size",
			},
			{
				"fieldname": "custom_thumb_right_size",
				"label": "Thumb Right Size",
				"fieldtype": "Data",
				"insert_after": "custom_thumb_left_size",
			},
			{
				"fieldname": "custom_wrist_size",
				"label": "Wrist Size",
				"fieldtype": "Data",
				"insert_after": "custom_thumb_right_size",
			},
			{
				"fieldname": "custom_neck_size",
				"label": "Neck Size",
				"fieldtype": "Data",
				"insert_after": "custom_wrist_size",
			},
		]
	}

	create_custom_fields(customer_fields, update=True)
	frappe.db.commit()
	print("Customer enhanced fields created successfully.")
