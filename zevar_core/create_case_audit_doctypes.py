import frappe


def execute():
	# Create Case Audit Scan (Child Table)
	if not frappe.db.exists("DocType", "Case Audit Scan"):
		doc = frappe.get_doc(
			{
				"doctype": "DocType",
				"name": "Case Audit Scan",
				"module": "Unified Retail Management System",
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
						"label": "Barcode/EPC",
						"in_list_view": 1,
					},
					{"fieldname": "scanned_at", "fieldtype": "Datetime", "label": "Scanned At"},
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

	# Create Case Audit Session
	if not frappe.db.exists("DocType", "Case Audit Session"):
		doc = frappe.get_doc(
			{
				"doctype": "DocType",
				"name": "Case Audit Session",
				"module": "Unified Retail Management System",
				"custom": 0,
				"is_submittable": 1,
				"naming_rule": "Expression",
				"autoname": "CASE-AUDIT-.YYYY.-.#####",
				"fields": [
					{
						"fieldname": "store_location",
						"fieldtype": "Link",
						"options": "Warehouse",
						"label": "Store/Warehouse",
						"reqd": 1,
						"in_list_view": 1,
					},
					{
						"fieldname": "started_at",
						"fieldtype": "Datetime",
						"label": "Started At",
						"in_list_view": 1,
						"read_only": 1,
					},
					{
						"fieldname": "completed_at",
						"fieldtype": "Datetime",
						"label": "Completed At",
						"read_only": 1,
					},
					{
						"fieldname": "status",
						"fieldtype": "Select",
						"label": "Status",
						"options": "Draft\nIn Progress\nReconciled\nDiscrepancy",
						"default": "Draft",
						"in_list_view": 1,
						"read_only": 1,
					},
					{
						"fieldname": "expected_count",
						"fieldtype": "Int",
						"label": "Expected Count",
						"read_only": 1,
					},
					{
						"fieldname": "scanned_count",
						"fieldtype": "Int",
						"label": "Scanned Count",
						"read_only": 1,
					},
					{
						"fieldname": "scans",
						"fieldtype": "Table",
						"options": "Case Audit Scan",
						"label": "Scans",
					},
				],
				"permissions": [
					{"role": "Sales User", "read": 1, "write": 1, "create": 1, "submit": 1},
					{
						"role": "Sales Manager",
						"read": 1,
						"write": 1,
						"create": 1,
						"submit": 1,
						"cancel": 1,
						"amend": 1,
					},
					{
						"role": "System Manager",
						"read": 1,
						"write": 1,
						"create": 1,
						"submit": 1,
						"cancel": 1,
						"amend": 1,
					},
				],
			}
		)
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
