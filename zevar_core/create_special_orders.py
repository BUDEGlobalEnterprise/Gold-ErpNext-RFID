import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_doctypes():
	module = "Unified Retail Management System"

	print("Creating Zevar Special Order Stone...")
	if not frappe.db.exists("DocType", "Zevar Special Order Stone"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Zevar Special Order Stone",
			"module": module,
			"custom": 1,
			"istable": 1,
			"editable_grid": 1,
			"fields": [
				{
					"fieldname": "stone_item_code",
					"fieldtype": "Link",
					"options": "Item",
					"label": "Stone Item Code",
					"in_list_view": 1
				},
				{
					"fieldname": "shape",
					"fieldtype": "Data",
					"label": "Shape",
					"in_list_view": 1
				},
				{
					"fieldname": "carat_weight",
					"fieldtype": "Float",
					"label": "Carat Weight",
					"in_list_view": 1
				},
				{
					"fieldname": "clarity",
					"fieldtype": "Data",
					"label": "Clarity"
				},
				{
					"fieldname": "color",
					"fieldtype": "Data",
					"label": "Color"
				},
				{
					"fieldname": "sourcing_method",
					"fieldtype": "Select",
					"options": "In-Stock\nMemo Request\nCustomer Provided",
					"label": "Sourcing Method",
					"in_list_view": 1
				}
			]
		})
		doc.insert(ignore_permissions=True)

	print("Creating Zevar Special Order...")
	if not frappe.db.exists("DocType", "Zevar Special Order"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Zevar Special Order",
			"module": module,
			"custom": 1,
			"is_submittable": 1,
			"autoname": "ZSO-.YYYY.-.####",
			"fields": [
				{
					"fieldname": "customer",
					"fieldtype": "Link",
					"options": "Customer",
					"label": "Customer",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "ring_size",
					"fieldtype": "Data",
					"label": "Ring Size"
				},
				{
					"fieldname": "workflow_status",
					"fieldtype": "Select",
					"options": "Draft\nCAD Pending\nBench Work\nSetting\nPolishing\nQC\nReady",
					"label": "Workflow Status",
					"default": "Draft",
					"in_list_view": 1
				},
				{
					"fieldname": "metal_type",
					"fieldtype": "Select",
					"options": "Gold\nPlatinum\nSilver",
					"label": "Metal Type"
				},
				{
					"fieldname": "metal_purity",
					"fieldtype": "Select",
					"options": "14K\n18K\n22K\n24K",
					"label": "Metal Purity"
				},
				{
					"fieldname": "estimated_weight_grams",
					"fieldtype": "Float",
					"label": "Estimated Weight (Grams)"
				},
				{
					"fieldname": "estimated_total_price",
					"fieldtype": "Currency",
					"label": "Estimated Total Price"
				},
				{
					"fieldname": "stones",
					"fieldtype": "Table",
					"options": "Zevar Special Order Stone",
					"label": "Stones"
				}
			]
		})
		doc.insert(ignore_permissions=True)

	print("Creating Zevar Job Bag...")
	if not frappe.db.exists("DocType", "Zevar Job Bag"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Zevar Job Bag",
			"module": module,
			"custom": 1,
			"autoname": "JB-.YYYY.-.####",
			"fields": [
				{
					"fieldname": "special_order",
					"fieldtype": "Link",
					"options": "Zevar Special Order",
					"label": "Special Order",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "current_bench",
					"fieldtype": "Link",
					"options": "Workstation",
					"label": "Current Bench",
					"in_list_view": 1
				},
				{
					"fieldname": "barcode",
					"fieldtype": "Data",
					"label": "Barcode",
					"read_only": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "status",
					"fieldtype": "Select",
					"options": "Quoted\nApproved\nProcurement\nIn Production\nQC Check\nCompleted\nDelivered",
					"label": "Status",
					"default": "Quoted",
					"in_list_view": 1
				},
			]
		})
		doc.insert(ignore_permissions=True)

	# ── Custom fields on Zevar Special Order for Shop Floor display ──
	custom_fields = {
		"Zevar Special Order": [
			{"fieldname": "custom_item_description", "fieldtype": "Data", "label": "Item Description", "insert_after": "customer"},
			{"fieldname": "custom_priority", "fieldtype": "Select", "label": "Priority", "insert_after": "custom_item_description", "options": "Normal\nHigh\nUrgent", "default": "Normal"},
			{"fieldname": "custom_assigned_to", "fieldtype": "Link", "label": "Assigned To", "insert_after": "custom_priority", "options": "User"},
			{"fieldname": "custom_due_date", "fieldtype": "Date", "label": "Due Date", "insert_after": "custom_assigned_to"},
			{"fieldname": "custom_order_number", "fieldtype": "Data", "label": "Order Number", "insert_after": "custom_due_date", "read_only": 1},
		],
	}

	for doctype, fields in custom_fields.items():
		existing = frappe.db.get_all("Custom Field", filters={"dt": doctype}, pluck="name")
		existing_names = set(existing)
		for cf in fields:
			cf_name = f"{doctype}-{cf['fieldname']}"
			if cf_name not in existing_names:
				custom_doc = frappe.get_doc({
					"doctype": "Custom Field",
					"dt": doctype,
					**cf,
				})
				custom_doc.insert(ignore_permissions=True)
				print(f"  Custom field added: {cf_name}")

	frappe.db.commit()
	print("Special Order Doctypes Created Successfully!")

if __name__ == '__main__':
    create_doctypes()
