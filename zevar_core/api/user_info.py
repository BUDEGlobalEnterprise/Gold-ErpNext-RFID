"""
User Info API for POS Dashboard.

Provides current user information including roles for role-based
dashboard tile rendering.
"""

import frappe


@frappe.whitelist(allow_guest=True)
def get_user_info():
	"""Return current user info with roles for the POS dashboard.

	Returns:
		dict: Contains user email, full_name, and list of role names.
	"""
	user = frappe.session.user
	if user == "Guest":
		return "Guest"

	roles = frappe.get_roles(user)
	full_name = frappe.db.get_value("User", user, "full_name") or user

	return {
		"user": user,
		"full_name": full_name,
		"roles": roles,
	}
