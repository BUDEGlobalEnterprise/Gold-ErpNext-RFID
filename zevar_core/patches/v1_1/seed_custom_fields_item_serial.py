import frappe


def execute():
	_create_item_fields()
	_create_serial_no_fields()


def _create_item_fields():
	fields = [
		{
			"fieldname": "custom_is_bulk_sku",
			"fieldtype": "Check",
			"label": "Is Bulk SKU",
			"description": "Non-serialized items (chains/studs) use quantity-based stock",
			"insert_after": "has_serial_no",
		},
		{
			"fieldname": "custom_default_showcase",
			"fieldtype": "Link",
			"label": "Default Showcase",
			"options": "Display Case",
			"insert_after": "custom_is_bulk_sku",
		},
		{
			"fieldname": "custom_is_customer_owned",
			"fieldtype": "Check",
			"label": "Is Customer Owned",
			"description": "For repair drop-offs; excluded from value KPIs",
			"insert_after": "custom_default_showcase",
		},
		{
			"fieldname": "custom_theft_risk_class",
			"fieldtype": "Select",
			"label": "Theft Risk Class",
			"options": "\nLow\nMedium\nHigh",
			"default": "Medium",
			"insert_after": "custom_is_customer_owned",
		},
		{
			"fieldname": "custom_piece_barcode",
			"fieldtype": "Data",
			"label": "Piece Barcode",
			"unique": 1,
			"insert_after": "custom_theft_risk_class",
		},
	]

	_insert_custom_fields("Item", fields)


def _create_serial_no_fields():
	fields = [
		{
			"fieldname": "custom_reserved_for_customer",
			"fieldtype": "Link",
			"label": "Reserved For Customer",
			"options": "Customer",
			"insert_after": "warehouse",
		},
		{
			"fieldname": "custom_reserved_until",
			"fieldtype": "Datetime",
			"label": "Reserved Until",
			"insert_after": "custom_reserved_for_customer",
		},
		{
			"fieldname": "custom_current_zone",
			"fieldtype": "Data",
			"label": "Current Zone",
			"read_only": 1,
			"insert_after": "custom_reserved_until",
		},
		{
			"fieldname": "custom_last_seen_at",
			"fieldtype": "Datetime",
			"label": "Last Seen At",
			"read_only": 1,
			"insert_after": "custom_current_zone",
		},
		{
			"fieldname": "custom_last_seen_by",
			"fieldtype": "Link",
			"label": "Last Seen By",
			"options": "User",
			"read_only": 1,
			"insert_after": "custom_last_seen_at",
		},
		{
			"fieldname": "custom_lifecycle_log_html",
			"fieldtype": "Text Editor",
			"label": "Lifecycle Log",
			"read_only": 1,
			"insert_after": "custom_last_seen_by",
		},
	]

	_insert_custom_fields("Serial No", fields)


def _insert_custom_fields(doctype, fields):
	for field in fields:
		exists = frappe.db.exists(
			"Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}
		)
		if not exists:
			cf = frappe.get_doc(
				{
					"doctype": "Custom Field",
					"dt": doctype,
					"module": "Unified Retail Management System",
					**field,
				}
			)
			cf.insert(ignore_permissions=True)
