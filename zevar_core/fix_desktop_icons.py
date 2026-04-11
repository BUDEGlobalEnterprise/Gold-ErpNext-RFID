"""
Fix Desktop Icons, Apps Screen, and Shortcuts for Zevar POS

This script:
1. Imports all desktop icons from all apps into the database
2. Ensures all apps appear on the apps screen
3. Verifies shortcuts are properly configured
"""

import json
import os

import frappe
from frappe.modules.import_file import import_file_by_path


def import_all_desktop_icons():
	"""Import desktop icons from JSON files in all installed apps."""
	frappe.clear_cache()
	imported_count = 0
	skipped_count = 0
	error_count = 0

	apps = frappe.get_installed_apps()
	frappe.logger().info(f"Scanning {len(apps)} installed apps for desktop icons...")

	for app_name in apps:
		app_path = frappe.get_pymodule_path(app_name)
		icons_dir = os.path.join(app_path, os.path.basename(app_path), "desktop_icon")

		if not os.path.exists(icons_dir):
			# Try alternate path (some apps don't have nested folder)
			icons_dir = os.path.join(app_path, "desktop_icon")

		if not os.path.exists(icons_dir):
			continue

		frappe.logger().info(f"Processing {app_name} desktop icons...")

		for fname in os.listdir(icons_dir):
			if not fname.endswith(".json"):
				continue

			file_path = os.path.join(icons_dir, fname)

			try:
				with open(  # nosemgrep
					file_path
				) as f:
					icon_data = json.load(f)

				# Must have doctype key to be valid
				if not icon_data.get("doctype"):
					frappe.log_error(
						f"Desktop icon {fname} missing 'doctype' key",
						"Desktop Icon Import",
					)
					error_count += 1
					continue

				icon_name = icon_data.get("name")

				# Check if already exists
				if icon_name and frappe.db.exists("Desktop Icon", icon_name):
					# Update existing icon
					doc = frappe.get_doc("Desktop Icon", icon_name)
					for key, value in icon_data.items():
						if key not in ["doctype", "name", "creation", "modified", "modified_by", "owner"]:
							setattr(doc, key, value)
					doc.save(ignore_permissions=True)
					skipped_count += 1
				else:
					# Import new icon
					import_file_by_path(file_path)
					imported_count += 1

				frappe.db.commit()  # nosemgrep

			except Exception as e:
				frappe.log_error(
					f"Failed to import desktop icon {fname}: {e}",
					"Desktop Icon Import",
				)
				error_count += 1

	# Clear cache to ensure icons appear immediately
	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")
	for user in frappe.get_all("User", pluck="name"):
		frappe.cache.hdel("desktop_icons", user)
		frappe.cache.hdel("bootinfo", user)

	frappe.logger().info(
		f"Desktop icons import complete: {imported_count} imported, {skipped_count} updated, {error_count} errors"
	)

	return imported_count, skipped_count, error_count


def create_missing_app_icons():
	"""Create desktop icons for apps that don't have any defined."""
	from frappe.desk.doctype.desktop_icon.desktop_icon import (
		create_desktop_icons_from_installed_apps,
	)

	create_desktop_icons_from_installed_apps()


def verify_and_fix_shortcuts():
	"""Verify shortcuts are properly configured."""
	if not frappe.db.exists("DocType", "Zevar Desk Shortcut"):
		frappe.logger().warning("Zevar Desk Shortcut DocType not found, skipping shortcuts")
		return 0

	try:
		from zevar_core.install import create_default_desk_shortcuts
		from zevar_core.shortcut_seed import get_default_shortcuts

		create_default_desk_shortcuts()
		frappe.logger().info("Shortcuts verified and created")
		return len(get_default_shortcuts())
	except Exception as e:
		frappe.log_error(f"Failed to create shortcuts: {e}", "Shortcut Creation")
		return 0


def create_missing_desktop_icons_for_workspaces():
	"""Create desktop icons for workspaces that don't have one."""
	from frappe.desk.doctype.desktop_icon.desktop_icon import (
		create_desktop_icons_from_workspace,
	)

	try:
		create_desktop_icons_from_workspace()
	except Exception as e:
		frappe.log_error(
			f"Failed to create desktop icons from workspace: {e}",
			"Desktop Icon Workspace Creation",
		)
		frappe.logger().warning(f"Skipping desktop icon creation: {e}")


def execute():
	"""Execute all fixes."""
	# Check if frappe is already initialized (e.g., from after_migrate hook)
	already_initialized = frappe.local.site is not None if hasattr(frappe.local, "site") else False

	if not already_initialized:
		# Get site from environment or use default
		import os

		site = os.environ.get("FRAPPE_SITE", "site1.local")
		frappe.init(site=site)
		frappe.connect()

	try:
		frappe.logger().info("=" * 60)
		frappe.logger().info("Starting Desktop Icons, Apps, and Shortcuts Fix")
		frappe.logger().info("=" * 60)

		# Step 1: Import all desktop icons
		frappe.logger().info("Step 1: Importing desktop icons from all apps...")
		imported, updated, errors = import_all_desktop_icons()

		# Step 2: Create missing app icons
		frappe.logger().info("Step 2: Creating missing app icons...")
		create_missing_app_icons()

		# Step 3: Create desktop icons for workspaces
		frappe.logger().info("Step 3: Creating desktop icons for workspaces...")
		create_missing_desktop_icons_for_workspaces()

		# Step 4: Verify and fix shortcuts
		frappe.logger().info("Step 4: Verifying and fixing shortcuts...")
		shortcut_count = verify_and_fix_shortcuts()

		# Summary
		frappe.logger().info("=" * 60)
		frappe.logger().info("Fix Complete!")
		frappe.logger().info(f"  Desktop Icons: {imported} imported, {updated} updated, {errors} errors")
		frappe.logger().info(f"  Shortcuts: {shortcut_count} shortcuts configured")
		frappe.logger().info("=" * 60)

	finally:
		if not already_initialized:
			frappe.destroy()


if __name__ == "__main__":
	execute()
