"""
Patch: Setup Repair System

This patch ensures all repair system components are properly set up in Frappe.
Run this via: bench execute zevar_core.patches.setup_repair_system.execute
"""

import os

import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
	"""Setup the complete repair system in Frappe"""

	print("=" * 60)
	print("Setting Up Repair System for Zevar Jewelers")
	print("=" * 60)

	# 1. Create Desktop Icons
	create_repair_desktop_icons()

	# 2. Create Workspace
	create_repairs_workspace()

	# 3. Create Workflow
	create_repair_workflow()

	# 4. Create Required Roles
	create_technician_role()

	# 5. Create Repair Settings single records
	create_repair_settings()

	# 6. Clear caches
	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")
	frappe.cache.delete_key("workspace_links")
	frappe.clear_cache()

	print("\n" + "=" * 60)
	print("Repair System Setup Complete!")
	print("=" * 60)
	print("\nNext Steps:")
	print("1. Go to Desk and look for 'Repairs' workspace")
	print("2. Open 'Repair Order' DocType")
	print("3. Configure 'Repair Commission Settings'")
	print("4. Configure 'Repair Accounting Settings'")


def create_repair_desktop_icons():
	"""Create desktop icons for repair-related DocTypes"""
	print("\n1. Creating Desktop Icons...")

	icons_to_create = [
		{
			"name": "Repair Orders",
			"label": "Repair Orders",
			"link_to": "Repair Order",
			"link_type": "DocType",
			"icon": "tools",
			"color": "#f59e0b",
			"description": "Jewelry repair tracking and management",
			"seq": 40,
		},
		{
			"name": "Repair Types",
			"label": "Repair Types",
			"link_to": "Repair Type",
			"link_type": "DocType",
			"icon": "wrench",
			"color": "#8b5cf6",
			"description": "Repair types with pricing and time estimates",
			"seq": 41,
		},
	]

	for icon_data in icons_to_create:
		if not frappe.db.exists("Desktop Icon", icon_data["name"]):
			try:
				doc = frappe.new_doc("Desktop Icon")
				doc.update(icon_data)
				doc.insert(ignore_permissions=True)
				print(f"   ✓ Created: {icon_data['name']}")
			except Exception as e:
				print(f"   ✗ Failed to create {icon_data['name']}: {e}")
		else:
			print(f"   - Already exists: {icon_data['name']}")


def create_repairs_workspace():
	"""Create the Repairs workspace"""
	print("\n2. Creating Repairs Workspace...")

	workspace_name = "Repairs"

	if frappe.db.exists("Workspace", workspace_name):
		print(f"   - Workspace already exists: {workspace_name}")
		return

	try:
		doc = frappe.new_doc("Workspace")
		doc.name = workspace_name
		doc.label = "Repairs"
		doc.module = "Unified Retail Management System"
		doc.category = "Domains"
		doc.icon = "tools"
		doc.is_standard = 1
		doc.public = 1
		doc.description = "Repair management workspace"

		# Add links
		links_data = [
			{"link_to": "Repair Order", "link_type": "DocType", "label": "Repair Orders"},
			{"link_to": "Repair Type", "link_type": "DocType", "label": "Repair Types"},
			{"link_to": "Repair", "link_type": "Page", "label": "Repair Terminal"},
			{"link_to": "Repair Turnaround", "link_type": "Report", "label": "Repair Turnaround"},
			{"link_to": "Repair Revenue", "link_type": "Report", "label": "Repair Revenue"},
			{"link_to": "Overdue Repairs", "link_type": "Report", "label": "Overdue Repairs"},
			{"link_to": "Repair Type Popularity", "link_type": "Report", "label": "Repair Type Popularity"},
		]

		for link in links_data:
			doc.append("links", link)

		# Add shortcut
		doc.append(
			"shortcuts",
			{
				"link_to": "Repair Order",
				"link_type": "DocType",
				"label": "New Repair Order",
				"icon": "plus",
				"color": "#f59e0b",
				"format": "{}",
			},
		)

		doc.insert(ignore_permissions=True)
		print("   ✓ Created: Repairs workspace")
	except Exception as e:
		print(f"   ✗ Failed to create workspace: {e}")


def create_repair_workflow():
	"""Create the Repair Order workflow"""
	print("\n3. Creating Repair Order Workflow...")

	workflow_name = "Repair Order Workflow"

	if frappe.db.exists("Workflow", workflow_name):
		print(f"   - Workflow already exists: {workflow_name}")
		return

	try:
		workflow = frappe.new_doc("Workflow")
		workflow.workflow_name = workflow_name
		workflow.document_type = "Repair Order"
		workflow.workflow_state_field = "status"
		workflow.send_alert_on_update = 1
		workflow.is_active = 1

		# Define workflow states
		states = [
			{"state": "Received", "doc_status": 0},
			{"state": "Estimated", "doc_status": 0},
			{"state": "Approved", "doc_status": 0},
			{"state": "In Progress", "doc_status": 0},
			{"state": "Waiting for Parts", "doc_status": 0},
			{"state": "Quality Check", "doc_status": 0},
			{"state": "Ready for Pickup", "doc_status": 1},
			{"state": "Delivered", "doc_status": 1},
			{"state": "Cancelled", "doc_status": 2},
		]

		for state_data in states:
			workflow.append("workflow_states", state_data)

		# Define workflow transitions
		transitions = [
			{
				"state": "Received",
				"action": "Send Estimate",
				"next_state": "Estimated",
				"allowed": "Sales User\nStore Manager\nSystem Manager",
			},
			{
				"state": "Estimated",
				"action": "Approve",
				"next_state": "Approved",
				"allowed": "System Manager\nStore Manager",
			},
			{
				"state": "Approved",
				"action": "Start Work",
				"next_state": "In Progress",
				"allowed": "Technician\nSystem Manager\nStore Manager",
			},
			{
				"state": "In Progress",
				"action": "Submit for QC",
				"next_state": "Quality Check",
				"allowed": "Technician\nSystem Manager\nStore Manager",
			},
			{
				"state": "Quality Check",
				"action": "Mark Ready",
				"next_state": "Ready for Pickup",
				"allowed": "Technician\nSystem Manager\nStore Manager",
			},
			{
				"state": "Ready for Pickup",
				"action": "Deliver",
				"next_state": "Delivered",
				"allowed": "Sales User\nSystem Manager\nStore Manager",
			},
		]

		for transition_data in transitions:
			workflow.append("workflow_transitions", transition_data)

		workflow.insert(ignore_permissions=True)
		print(f"   ✓ Created: {workflow_name}")
	except Exception as e:
		print(f"   ✗ Failed to create workflow: {e}")


def create_technician_role():
	"""Create the Technician role if it doesn't exist"""
	print("\n4. Creating Technician Role...")

	role_name = "Technician"

	if frappe.db.exists("Role", role_name):
		print(f"   - Role already exists: {role_name}")
		return

	try:
		role = frappe.new_doc("Role")
		role.role_name = role_name
		role.desk_access = 1
		role.insert(ignore_permissions=True)
		print(f"   ✓ Created: {role_name} role")
	except Exception as e:
		print(f"   ✗ Failed to create role: {e}")


def create_repair_settings():
	"""Create single DocType settings for repairs"""
	print("\n5. Creating Repair Settings...")

	settings_to_create = [
		{
			"doctype": "Repair Commission Settings",
			"commission_rate_labor_pct": 20.0,
			"bonus_on_time_pct": 5.0,
			"penalty_late_days": 0.5,
			"min_commission_amount": 50,
			"commission_payment_frequency": "Monthly",
		},
		{
			"doctype": "Repair Accounting Settings",
			"auto_recognize_revenue": 0,
			"recognize_on_delivery": 1,
			"track_material_consumption": 1,
		},
	]

	for setting_data in settings_to_create:
		doctype = setting_data.pop("doctype")
		try:
			if not frappe.db.exists(doctype, doctype):
				doc = frappe.new_doc(doctype)
				doc.update(setting_data)
				doc.insert(ignore_permissions=True)
				print(f"   ✓ Created: {doctype}")
			else:
				print(f"   - Already exists: {doctype}")
		except Exception as e:
			print(f"   ✗ Failed to create {doctype}: {e}")


# Allow running this patch directly
if __name__ == "__main__":
	execute()
