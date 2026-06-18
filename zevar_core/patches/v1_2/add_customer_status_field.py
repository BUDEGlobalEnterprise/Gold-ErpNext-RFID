"""Add customer status (tier) custom field for CRM clienteling.

Creates a Select field on Customer to track VIP/Platinum/Gold/Silver/etc. status.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Customer": [
			{
				"fieldname": "custom_customer_status",
				"label": "Customer Status",
				"fieldtype": "Select",
				"options": "\nRegular\nSilver\nGold\nPlatinum\nVIP\nDiamond",
				"default": "",
				"insert_after": "customer_group",
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "Customer tier based on purchase history and relationship",
			},
		],
	}

	create_custom_fields(custom_fields, ignore_validate=True)
