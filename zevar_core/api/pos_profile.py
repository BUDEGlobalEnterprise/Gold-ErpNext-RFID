"""
POS Profile API - Profile management and selection

Provides endpoints for:
- Listing available POS profiles
- Getting the active profile for current user
- Setting the active profile
"""

import frappe
from frappe import _
from frappe.utils import cstr


@frappe.whitelist()
def get_pos_profiles() -> dict:
	"""
	Get all available POS profiles for the current user.

	Returns:
		dict: Contains 'profiles' list with profile details
	"""
	frappe.has_permission("POS Profile", ptype="read", throw=True)

	profiles = frappe.get_all(
		"POS Profile",
		filters={"disabled": 0},
		fields=[
			"name",
			"company",
			"warehouse",
			"currency",
			"selling_price_list",
			"customer",
			"write_off_account",
			"write_off_cost_center",
			"expense_account",
			"cost_center",
			"custom_enforce_fixed_float",
			"custom_fixed_opening_float",
			"custom_variance_alert_threshold",
		],
		order_by="name",
	)

	# Enrich profiles with additional info
	for profile in profiles:
		# Get warehouse name if available
		if profile.warehouse:
			profile.warehouse_name = (
				frappe.db.get_value("Warehouse", profile.warehouse, "warehouse_name") or profile.warehouse
			)

		# Get store location linked to this profile's warehouse
		if profile.warehouse:
			store_location = frappe.db.get_value(
				"Store Location",
				{"default_warehouse": profile.warehouse, "is_active": 1},
				["name", "store_code", "store_name"],
				as_dict=True,
			)
			if store_location:
				profile.store_location = store_location.name
				profile.store_code = store_location.store_code
				profile.store_name = store_location.store_name

	return {"profiles": profiles, "count": len(profiles)}


@frappe.whitelist()
def get_active_profile() -> dict:
	"""
	Get the active POS profile for the current user.

	The active profile is determined by:
	1. User's default POS Profile setting
	2. Store Location assignment to user
	3. First available profile as fallback

	Returns:
		dict: Contains 'active_profile' with profile details or None
	"""
	user = frappe.session.user

	# Try to get from user's default
	default_profile = frappe.cache.hget("pos_active_profile", user)
	if not default_profile and frappe.db.has_column("User", "pos_profile"):
		default_profile = frappe.db.get_value("User", user, "pos_profile")

	# Check if user has a store location assignment with POS profile
	if not default_profile:
		# Look for employee linked to user
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if employee:
			# Check store location assignment
			store_location = frappe.db.get_value(
				"Store Location",
				{"is_active": 1},
				["pos_profile", "default_warehouse", "name"],
				as_dict=True,
			)
			if store_location and store_location.pos_profile:
				default_profile = store_location.pos_profile

	# Fallback to first available profile
	if not default_profile:
		default_profile = frappe.db.get_value(
			"POS Profile",
			{"disabled": 0},
			"name",
			order_by="creation",
		)

	if not default_profile:
		return {"active_profile": None}

	# Get full profile details
	profile = frappe.get_doc("POS Profile", default_profile)

	active_profile = {
		"name": profile.name,
		"company": profile.company,
		"warehouse": profile.warehouse,
		"currency": profile.currency,
		"selling_price_list": profile.selling_price_list,
		"customer": profile.customer,
		"write_off_account": profile.write_off_account,
		"write_off_cost_center": profile.write_off_cost_center,
		"expense_account": profile.expense_account,
		"cost_center": profile.cost_center,
	}

	# Get warehouse name
	if profile.warehouse:
		active_profile["warehouse_name"] = (
			frappe.db.get_value("Warehouse", profile.warehouse, "warehouse_name") or profile.warehouse
		)

	# Get store location info
	if profile.warehouse:
		store_location = frappe.db.get_value(
			"Store Location",
			{"default_warehouse": profile.warehouse, "is_active": 1},
			["name", "store_code", "store_name", "tax_template", "county_tax_rate"],
			as_dict=True,
		)
		if store_location:
			active_profile["store_location"] = store_location.name
			active_profile["store_code"] = store_location.store_code
			active_profile["store_name"] = store_location.store_name
			active_profile["tax_template"] = store_location.tax_template
			active_profile["county_tax_rate"] = store_location.county_tax_rate

	# Get payment modes for this profile
	payment_modes = []
	if hasattr(profile, "payments") and profile.payments:
		for p in profile.payments:
			payment_modes.append(
				{
					"mode_of_payment": p.mode_of_payment,
					"default": p.default or False,
				}
			)
	active_profile["payment_modes"] = payment_modes

	return {"active_profile": active_profile}


@frappe.whitelist(methods=["POST"])
def set_active_profile(profile_name: str) -> dict:
	"""
	Set the active POS profile for the current user.

	Args:
		profile_name: Name of the POS Profile to set as active

	Returns:
		dict: Success status and message
	"""
	frappe.has_permission("POS Profile", ptype="read", throw=True)

	if not profile_name:
		frappe.throw(_("Profile name is required."))

	# Verify profile exists and is not disabled
	if not frappe.db.exists("POS Profile", profile_name):
		frappe.throw(_("POS Profile '{0}' not found.").format(profile_name))

	if frappe.db.get_value("POS Profile", profile_name, "disabled"):
		frappe.throw(_("POS Profile '{0}' is disabled.").format(profile_name))

	user = frappe.session.user

	# Store in user's session/default
	# Using User document's custom field or session storage
	if frappe.db.has_column("User", "pos_profile"):
		frappe.db.set_value("User", user, "pos_profile", profile_name)

	# Also cache in session for quick access
	frappe.cache.hset("pos_active_profile", user, profile_name)

	return {
		"success": True,
		"message": _("Active profile set to {0}").format(profile_name),
		"profile_name": profile_name,
	}


@frappe.whitelist()
def get_profile_settings(profile_name: str) -> dict:
	"""
	Get detailed settings for a specific POS Profile.

	Args:
		profile_name: Name of the POS Profile

	Returns:
		dict: Complete profile settings including payment modes, item groups, etc.
	"""
	frappe.has_permission("POS Profile", ptype="read", throw=True)

	if not profile_name or not frappe.db.exists("POS Profile", profile_name):
		frappe.throw(_("POS Profile '{0}' not found.").format(profile_name or ""))

	profile = frappe.get_doc("POS Profile", profile_name)

	settings = {
		"name": profile.name,
		"company": profile.company,
		"warehouse": profile.warehouse,
		"currency": profile.currency,
		"selling_price_list": profile.selling_price_list,
		"customer": profile.customer,
		"write_off_account": profile.write_off_account,
		"write_off_cost_center": profile.write_off_cost_center,
		"expense_account": profile.expense_account,
		"cost_center": profile.cost_center,
		"allow_user_to_edit_rate": profile.allow_user_to_edit_rate,
		"allow_user_to_edit_discount": profile.allow_user_to_edit_discount,
		"allow_delete": profile.allow_delete,
		"allow_return": profile.allow_return,
		"always_include_discount_in_rate": profile.always_include_discount_in_rate,
		"taxes_and_charges": profile.taxes_and_charges,
		"campaign": profile.campaign,
		"tc_name": profile.tc_name,
		"terms": profile.terms,
	}

	# Get payment modes
	payment_modes = []
	if hasattr(profile, "payments") and profile.payments:
		for p in profile.payments:
			payment_modes.append(
				{
					"mode_of_payment": p.mode_of_payment,
					"default": p.default if hasattr(p, "default") else False,
				}
			)
	settings["payment_modes"] = payment_modes

	# Get allowed item groups
	item_groups = []
	if hasattr(profile, "item_groups") and profile.item_groups:
		for ig in profile.item_groups:
			item_groups.append(ig.item_group)
	settings["item_groups"] = item_groups

	# Get allowed customer groups
	customer_groups = []
	if hasattr(profile, "customer_groups") and profile.customer_groups:
		for cg in profile.customer_groups:
			customer_groups.append(cg.customer_group)
	settings["customer_groups"] = customer_groups

	return {"settings": settings}
