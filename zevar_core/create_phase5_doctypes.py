import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_doctypes():
	module = "Unified Retail Management System"

	print("Adding custom_rfid_epc to Item...")
	custom_fields = {
		"Item": [
			{
				"fieldname": "custom_rfid_epc",
				"fieldtype": "Data",
				"label": "RFID EPC",
				"unique": 1,
				"insert_after": "item_code",
			}
		]
	}
	create_custom_fields(custom_fields)

	print("Creating Display Case...")
	if not frappe.db.exists("DocType", "Display Case"):
		doc = frappe.get_doc(
			{
				"doctype": "DocType",
				"name": "Display Case",
				"module": module,
				"custom": 0,
				"istable": 0,
				"fields": [
					{
						"fieldname": "case_name",
						"fieldtype": "Data",
						"label": "Case Name",
						"reqd": 1,
					},
					{
						"fieldname": "warehouse",
						"fieldtype": "Link",
						"options": "Warehouse",
						"label": "Warehouse",
						"reqd": 1,
					},
				],
				"autoname": "field:case_name",
				"naming_rule": "By fieldname",
			}
		)
		doc.insert(ignore_permissions=True)

	print("Creating Case Audit Scan...")
	if not frappe.db.exists("DocType", "Case Audit Scan"):
		doc = frappe.get_doc(
			{
				"doctype": "DocType",
				"name": "Case Audit Scan",
				"module": module,
				"custom": 0,
				"istable": 1,
				"editable_grid": 1,
				"fields": [
					{
						"fieldname": "item_code",
						"fieldtype": "Link",
						"options": "Item",
						"label": "Item Code",
						"in_list_view": 1,
					},
					{
						"fieldname": "barcode_or_epc",
						"fieldtype": "Data",
						"label": "Barcode or EPC",
						"in_list_view": 1,
					},
					{
						"fieldname": "scanned_at",
						"fieldtype": "Datetime",
						"label": "Scanned At",
						"in_list_view": 1,
					},
					{
						"fieldname": "match_status",
						"fieldtype": "Select",
						"label": "Match Status",
						"options": "Matched\nUnexpected\nMissing",
						"in_list_view": 1,
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)

	print("Creating Case Audit Session...")
	if not frappe.db.exists("DocType", "Case Audit Session"):
		doc = frappe.get_doc(
			{
				"doctype": "DocType",
				"name": "Case Audit Session",
				"module": module,
				"custom": 0,
				"istable": 0,
				"is_submittable": 1,
				"fields": [
					{
						"fieldname": "store_location",
						"fieldtype": "Link",
						"options": "Warehouse",
						"label": "Store Location",
						"reqd": 1,
					},
					{
						"fieldname": "display_case",
						"fieldtype": "Link",
						"options": "Display Case",
						"label": "Display Case",
					},
					{
						"fieldname": "started_at",
						"fieldtype": "Datetime",
						"label": "Started At",
					},
					{
						"fieldname": "completed_at",
						"fieldtype": "Datetime",
						"label": "Completed At",
					},
					{
						"fieldname": "expected_count",
						"fieldtype": "Int",
						"label": "Expected Count",
					},
					{
						"fieldname": "scanned_count",
						"fieldtype": "Int",
						"label": "Scanned Count",
					},
					{
						"fieldname": "status",
						"fieldtype": "Select",
						"label": "Status",
						"options": "Draft\nIn Progress\nReconciled\nDiscrepancy",
						"default": "Draft",
					},
					{
						"fieldname": "scans",
						"fieldtype": "Table",
						"options": "Case Audit Scan",
						"label": "Scans",
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
	print("Phase 5 Doctypes Created Successfully!")
