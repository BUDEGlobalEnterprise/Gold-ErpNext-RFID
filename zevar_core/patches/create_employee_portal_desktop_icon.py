"""
Create Employee Portal as a standalone Desktop Icon.

Since add_to_apps_screen only supports one entry per app,
the Employee Portal must be created as a separate Desktop Icon
rather than through the hooks mechanism.
"""

import frappe


def execute() -> None:
	"""Create or update the Employee Portal desktop icon via database."""
	existing_name = frappe.db.exists("Desktop Icon", {"label": "Employee Portal", "link_type": "External"})
	if existing_name:
		icon = frappe.get_doc("Desktop Icon", existing_name)
		if icon.logo_url != "/assets/zevar_core/images/employee_portal_logo.svg":
			icon.logo_url = "/assets/zevar_core/images/employee_portal_logo.svg"
			icon.save()
		return

	icon = frappe.new_doc("Desktop Icon")
	icon.label = "Employee Portal"
	icon.link_type = "External"
	icon.link = "/employee-portal"
	icon.icon_type = "Link"
	icon.app = "zevar_core"
	icon.logo_url = "/assets/zevar_core/images/employee_portal_logo.svg"
	icon.insert(ignore_if_duplicate=True)
	frappe.db.commit()  # nosemgrep
