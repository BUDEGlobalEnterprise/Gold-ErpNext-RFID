"""
Simple script to fix desktop icons - run in bench console

Usage:
    bench --site zevar.localhost console
    >> runzevar("fix_icons")
"""

import frappe


def fix_icons():
	"""Fix desktop icons, apps screen, and shortcuts."""
	from zevar_core.fix_desktop_icons import (
		create_missing_app_icons,
		create_missing_desktop_icons_for_workspaces,
		import_all_desktop_icons,
		verify_and_fix_shortcuts,
	)

	frappe.clear_cache()

	# Import all desktop icons
	imported, updated, errors = import_all_desktop_icons()
	print(f"Desktop icons: {imported} imported, {updated} updated, {errors} errors")

	# Create missing app icons
	create_missing_app_icons()
	print("App icons created")

	# Create desktop icons for workspaces
	create_missing_desktop_icons_for_workspaces()
	print("Workspace icons created")

	# Verify shortcuts
	shortcut_count = verify_and_fix_shortcuts()
	print(f"Shortcuts: {shortcut_count} configured")

	frappe.clear_cache()
	print("Done! Please clear your browser cache.")


if __name__ == "__main__":
	fix_icons()
