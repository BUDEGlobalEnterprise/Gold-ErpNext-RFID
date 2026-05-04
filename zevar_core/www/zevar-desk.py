"""
Zevar Custom Desk Page Controller

Renders the modern, accessible desk page with customizable shortcuts.
"""

import frappe
from frappe import _

no_cache = 1


def get_context(context):
	"""
	Prepare context for the custom desk page.

	Args:
		context: Frappe page context dictionary

	Returns:
		dict: Updated context with page data
	"""
	# Check if user is logged in
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	# Add page title
	context.title = _("Zevar Desk")

	# Add page metadata
	context.meta = {
		"description": _("Zevar Jewelry Retail Management Desk"),
		"keywords": _("zevar, jewelry, retail, pos, management"),
	}

	# Check if user can manage shortcuts
	context.can_manage_shortcuts = (
		frappe.has_permission("Zevar Desk Shortcut", "write", throw=True)
		or frappe.user.has_role("System Manager")
		or frappe.user.has_role("Desk Customization Manager")
	)

	# Add breadcrumbs
	context.breadcrumbs = [
		{"label": _("Home"), "url": "/"},
		{"label": _("Zevar Desk"), "url": "/zevar-desk"},
	]

	# Include required JS/CSS libraries
	context.include_js = ["feather-icons", "vue"]
	context.include_css = ["zevar_core/css/desk.css"]

	return context


@frappe.whitelist(allow_guest=False)
def get_desk_data():
	"""
	Get all data needed for the desk page in one API call.

	Returns:
		dict: Contains shortcuts, stats, and activity
	"""
	from zevar_core.api.shortcuts import (
		get_desk_shortcuts,
		get_quick_stats,
		get_recent_activity,
	)

	return {
		"shortcuts": get_desk_shortcuts(),
		"stats": get_quick_stats(),
		"activity": get_recent_activity(),
	}
