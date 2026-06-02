"""Backfill pricing_method on all Items from the deprecated custom_is_bulk_sku flag.

Adds custom_pricing_method field if missing, then sets:
  - has_serial_no=1 → 'Fine'
  - custom_is_bulk_sku=1 → 'Bulk UPC'
  - everything else → 'Fine'

Idempotent.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "Item"):
		return

	_add_pricing_method_field()
	_backfill_values()


def _add_pricing_method_field():
	if frappe.db.exists("Custom Field", "Item-custom_pricing_method"):
		return

	frappe.get_doc({
		"doctype": "Custom Field",
		"dt": "Item",
		"fieldname": "custom_pricing_method",
		"fieldtype": "Select",
		"options": "Fine
Bulk UPC
Bulk IUOM
Bulk UOM
Bulk Mixed",
		"label": "Pricing Method",
		"default": "Fine",
		"insert_after": "has_serial_no",
	}).insert(ignore_permissions=True)


def _backfill_values():
	table = "`tabItem`"

	frappe.db.sql(f"""
		UPDATE {table}
		SET custom_pricing_method = 'Fine'
		WHERE (custom_pricing_method IS NULL OR custom_pricing_method = '')
		AND has_serial_no = 1
	""")

	frappe.db.sql(f"""
		UPDATE {table}
		SET custom_pricing_method = 'Bulk UPC'
		WHERE (custom_pricing_method IS NULL OR custom_pricing_method = '')
		AND (custom_is_bulk_sdk = 1 OR custom_is_bulk_sku = 1)
	""")

	frappe.db.sql(f"""
		UPDATE {table}
		SET custom_pricing_method = 'Fine'
		WHERE (custom_pricing_method IS NULL OR custom_pricing_method = '')
	""")

	frappe.db.commit()
