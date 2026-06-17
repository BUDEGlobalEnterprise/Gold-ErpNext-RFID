"""Add custom fields for CRM <-> POS integration.

Creates link fields between Customer, Sales Invoice, CRM Lead, and CRM Deal
to enable full-funnel traceability from lead capture through purchase.
Also adds CRM POS Settings to FCRM Settings for configuration.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if "crm" not in frappe.get_installed_apps():
		return
	_create_crm_link_fields()
	_create_crm_pos_settings()


def _create_crm_link_fields():
	custom_fields = {
		"Customer": [
			{
				"fieldname": "custom_crm_lead",
				"label": "CRM Lead",
				"fieldtype": "Link",
				"options": "CRM Lead",
				"insert_after": "crm_deal",
				"read_only": 1,
				"description": "Auto-linked CRM Lead created when this customer was first captured",
			},
			{
				"fieldname": "custom_crm_deal",
				"label": "CRM Deal",
				"fieldtype": "Link",
				"options": "CRM Deal",
				"insert_after": "custom_crm_lead",
				"read_only": 1,
				"description": "Active CRM Deal associated with this customer",
			},
		],
		"Sales Invoice": [
			{
				"fieldname": "custom_crm_deal",
				"label": "CRM Deal",
				"fieldtype": "Link",
				"options": "CRM Deal",
				"insert_after": "custom_transaction_stream",
				"read_only": 1,
				"allow_on_submit": 1,
				"description": "CRM Deal linked for revenue attribution",
			},
		],
		"CRM Lead": [
			{
				"fieldname": "custom_pos_customer",
				"label": "POS Customer",
				"fieldtype": "Link",
				"options": "Customer",
				"insert_after": "territory",
				"read_only": 1,
				"description": "Linked ERPNext Customer record",
			},
			{
				"fieldname": "custom_lead_origin",
				"label": "Lead Origin",
				"fieldtype": "Select",
				"options": "\nPOS Walk-in\nFacebook\nManual\nPOS Referral",
				"insert_after": "source",
				"description": "Where this lead was originally captured",
			},
		],
		"CRM Deal": [
			{
				"fieldname": "custom_pos_customer",
				"label": "POS Customer",
				"fieldtype": "Link",
				"options": "Customer",
				"insert_after": "territory",
				"read_only": 1,
				"description": "Linked ERPNext Customer record",
			},
			{
				"fieldname": "custom_originating_invoice",
				"label": "Originating Invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"insert_after": "custom_pos_customer",
				"read_only": 1,
				"description": "The POS invoice that triggered this deal creation",
			},
		],
	}

	create_custom_fields(custom_fields, ignore_validate=True)


def _create_crm_pos_settings():
	"""Add CRM POS integration settings to FCRM Settings as custom fields."""
	settings_fields = {
		"FCRM Settings": [
			{
				"fieldname": "custom_pos_integration_section",
				"label": "POS Integration Settings",
				"fieldtype": "Section Break",
				"insert_after": "",
			},
			{
				"fieldname": "custom_auto_create_lead_on_new_customer",
				"label": "Auto-create Lead on New Customer",
				"fieldtype": "Check",
				"default": 1,
				"insert_after": "custom_pos_integration_section",
				"description": "Automatically create a CRM Lead when a new customer is created in POS",
			},
			{
				"fieldname": "custom_auto_create_deal_on_high_value",
				"label": "Auto-create Deal on High-Value Sale",
				"fieldtype": "Check",
				"default": 1,
				"insert_after": "custom_auto_create_lead_on_new_customer",
				"description": "Automatically create a CRM Deal when a POS sale exceeds the threshold",
			},
			{
				"fieldname": "custom_high_value_threshold",
				"label": "High-Value Sale Threshold",
				"fieldtype": "Currency",
				"default": 5000,
				"insert_after": "custom_auto_create_deal_on_high_value",
				"description": "Minimum sale amount to trigger automatic deal creation",
			},
			{
				"fieldname": "custom_occasion_reminder_days_before",
				"label": "Occasion Reminder Days Before",
				"fieldtype": "Int",
				"default": 14,
				"insert_after": "custom_high_value_threshold",
				"description": "How many days before a birthday/anniversary to create a reminder task",
			},
		],
	}

	create_custom_fields(settings_fields, ignore_validate=True)
