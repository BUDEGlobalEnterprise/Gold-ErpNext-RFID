"""
Regenerate Desktop Icons — works without Redis (bench start stopped).

Run with: bench --site zevar.localhost execute zevar_core.patches.regenerate_desktop_icons.execute
"""

import frappe


def execute():
	"""Delete orphaned icons via direct SQL and regenerate from apps + workspaces."""
	from frappe.desk.doctype.desktop_icon.desktop_icon import create_desktop_icons

	icons = frappe.get_all(
		"Desktop Icon",
		fields=["name", "label", "icon_type", "hidden", "standard", "app"],
		limit_page_length=100,
	)

	# Delete orphaned non-standard Link icons that have no matching workspace sidebar
	# Use direct SQL to avoid Redis dependency
	for icon in icons:
		if not icon.standard and icon.icon_type == "Link":
			sidebar_exists = frappe.db.exists("Workspace Sidebar", {"title": icon.label})
			if not sidebar_exists:
				frappe.db.delete("Desktop Icon", {"name": icon.name})

	# Also delete user-created App icons with no proper app link
	for icon in icons:
		if not icon.standard and icon.icon_type == "App" and not icon.app:
			frappe.db.delete("Desktop Icon", {"name": icon.name})

	frappe.db.commit()  # nosemgrep

	# Regenerate standard icons
	create_desktop_icons()
	frappe.db.commit()  # nosemgrep

	# Clear the desktop icons cache (direct, no Redis queue needed)
	try:
		frappe.cache.hdel("desktop_icons", frappe.session.user)
		frappe.cache.hdel("bootinfo", frappe.session.user)
	except Exception:
		pass

	frappe.db.commit()  # nosemgrep
