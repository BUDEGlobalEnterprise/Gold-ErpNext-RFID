"""
Direct Patch to Fix Desktop Icon Creation Bug in Frappe v16.11.0

This patch directly modifies the core Frappe file to fix two bugs:

Bug 1 (Line 46): References non-existent 'module_name' field
Bug 2 (Line 250): Sets non-existent 'app_name' field

This confirms the bug exists in the core Frappe code.
Remove this patch after the official fix is released.
"""

import frappe


def execute():
	"""
	Directly patch the core Frappe desktop_icon.py file.
	This is a temporary workaround until Frappe fixes the bug upstream.
	"""
	import os

	# Path to the core Frappe file
	core_file_path = frappe.get_app_path("frappe")
	core_file_path = os.path.join(
		core_file_path, "frappe", "desk", "doctype", "desktop_icon", "desktop_icon.py"
	)

	# Read the current content
	with open(core_file_path) as f:  # nosemgrep
		content = f.read()

	# Fix 1: Remove module_name reference in validate()
	# Original line 46:
	#     self.label = self.module_name
	if "self.label = self.module_name" in content:
		content = content.replace(
			"self.label = self.module_name",
			"# self.label = self.module_name  # BUG FIX: module_name field doesn't exist in v16",
		)

	# Fix 2: Change app_name to app in create_desktop_icons_from_workspace
	# Original line 250:
	#     icon.app_name = app_name
	if "icon.app_name = app_name" in content:
		content = content.replace(
			"icon.app_name = app_name",
			"icon.app = app_name  # BUG FIX: app_name field doesn't exist, use 'app'",
		)

	# Write the patched content back
	with open(core_file_path, "w") as f:  # nosemgrep
		f.write(content)

	# Reload the DocType to apply changes
	frappe.reload_doc("Desk", "doctype", "Desktop Icon")
