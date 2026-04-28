import frappe


def execute():
	"""Add enhanced fields to Case Audit Session and Case Audit Scan DocTypes."""

	# --- Case Audit Session: new fields ---
	if frappe.db.exists("DocType", "Case Audit Session"):
		session_doc = frappe.get_doc("DocType", "Case Audit Session")

		new_session_fields = [
			{
				"fieldname": "auditor",
				"fieldtype": "Link",
				"options": "User",
				"label": "Auditor",
				"in_list_view": 1,
				"insert_after": "store_location",
			},
			{
				"fieldname": "audit_type",
				"fieldtype": "Select",
				"options": "Barcode\nRFID\nMixed",
				"label": "Audit Type",
				"default": "Barcode",
				"insert_after": "auditor",
			},
			{
				"fieldname": "cancelled_at",
				"fieldtype": "Datetime",
				"label": "Cancelled At",
				"read_only": 1,
				"insert_after": "completed_at",
			},
			{
				"fieldname": "section_break_values",
				"fieldtype": "Section Break",
				"label": "Value Tracking",
				"insert_after": "scanned_count",
			},
			{
				"fieldname": "total_value_expected",
				"fieldtype": "Currency",
				"label": "Total Value Expected",
				"read_only": 1,
				"insert_after": "section_break_values",
			},
			{
				"fieldname": "total_value_scanned",
				"fieldtype": "Currency",
				"label": "Total Value Scanned",
				"read_only": 1,
				"insert_after": "total_value_expected",
			},
			{
				"fieldname": "total_value_discrepancy",
				"fieldtype": "Currency",
				"label": "Total Value Discrepancy",
				"read_only": 1,
				"insert_after": "total_value_scanned",
			},
			{
				"fieldname": "notes",
				"fieldtype": "Small Text",
				"label": "Notes",
				"insert_after": "total_value_discrepancy",
			},
		]

		existing_fieldnames = {f.fieldname for f in session_doc.fields}
		for field_def in new_session_fields:
			if field_def["fieldname"] not in existing_fieldnames:
				session_doc.append("fields", field_def)

		# Update status options to include Cancelled
		for f in session_doc.fields:
			if f.fieldname == "status":
				if "Cancelled" not in (f.options or ""):
					f.options = (f.options or "") + "\nCancelled"
				break

		session_doc.save(ignore_permissions=True)

	# --- Case Audit Scan: new fields ---
	if frappe.db.exists("DocType", "Case Audit Scan"):
		scan_doc = frappe.get_doc("DocType", "Case Audit Scan")

		new_scan_fields = [
			{
				"fieldname": "item_name",
				"fieldtype": "Data",
				"label": "Item Name",
				"read_only": 1,
				"in_list_view": 1,
				"insert_after": "item_code",
			},
			{
				"fieldname": "is_duplicate",
				"fieldtype": "Check",
				"label": "Is Duplicate",
				"default": "0",
				"insert_after": "match_status",
			},
			{
				"fieldname": "item_image",
				"fieldtype": "Data",
				"label": "Item Image",
				"read_only": 1,
				"insert_after": "is_duplicate",
			},
			{
				"fieldname": "valuation_rate",
				"fieldtype": "Currency",
				"label": "Valuation Rate",
				"read_only": 1,
				"insert_after": "item_image",
			},
		]

		existing_fieldnames = {f.fieldname for f in scan_doc.fields}
		for field_def in new_scan_fields:
			if field_def["fieldname"] not in existing_fieldnames:
				scan_doc.append("fields", field_def)

		scan_doc.save(ignore_permissions=True)

	frappe.db.commit()
