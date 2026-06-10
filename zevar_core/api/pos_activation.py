"""
POS Profile Activation API - Manager-controlled register activation

Provides endpoints for:
- Activating a POS profile (manager only)
- Deactivating a POS profile (manager only, graceful session close)
- Auto-deactivation scheduler
- Checking activation status
"""

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, get_time, now_datetime, nowdate, time_diff_in_seconds


@frappe.whitelist(methods=["POST"])
def activate_pos_profile(profile_name: str) -> dict:
	"""Activate a POS profile so it can be used for sales. Manager only."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	if not profile_name or not frappe.db.exists("POS Profile", profile_name):
		frappe.throw(_("POS Profile '{0}' not found.").format(profile_name or ""))

	if frappe.db.get_value("POS Profile", profile_name, "disabled"):
		frappe.throw(_("POS Profile '{0}' is disabled and cannot be activated.").format(profile_name))

	profile = frappe.get_doc("POS Profile", profile_name)

	if not profile.meta.has_field("custom_is_activated"):
		frappe.throw(_("Activation fields not yet installed. Run bench migrate first."))

	if getattr(profile, "custom_is_activated", 0):
		activated_by = getattr(profile, "custom_activated_by", "")
		activated_at = getattr(profile, "custom_activated_at", "")
		frappe.throw(
			_("POS Profile '{0}' is already activated by {1} at {2}.").format(
				profile_name, activated_by, activated_at
			)
		)

	profile.custom_is_activated = 1
	profile.custom_activated_by = frappe.session.user
	profile.custom_activated_at = now_datetime()
	profile.save(ignore_permissions=True)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="pos_profile_activated",
		details={
			"profile": profile_name,
			"activated_by": frappe.session.user,
		},
		reference_document=profile_name,
		reference_type="POS Profile",
	)

	# Notify all managers
	_notify_activation(
		"pos_profile_activation",
		{
			"event_type": "activated",
			"profile_name": profile_name,
			"activated_by": frappe.session.user,
			"timestamp": str(now_datetime()),
		},
	)

	return {
		"success": True,
		"profile_name": profile_name,
		"activated_by": frappe.session.user,
		"activated_at": str(now_datetime()),
		"message": _("POS Profile '{0}' activated successfully.").format(profile_name),
	}


@frappe.whitelist(methods=["POST"])
def deactivate_pos_profile(profile_name: str, reason: str | None = None) -> dict:
	"""
	Deactivate a POS profile. If a session is open, prompt cashier to close.
	Manager only.
	"""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	if not profile_name or not frappe.db.exists("POS Profile", profile_name):
		frappe.throw(_("POS Profile '{0}' not found.").format(profile_name or ""))

	profile = frappe.get_doc("POS Profile", profile_name)

	if not getattr(profile, "custom_is_activated", 0):
		frappe.throw(_("POS Profile '{0}' is not currently activated.").format(profile_name))

	profile.custom_is_activated = 0
	profile.custom_activated_by = None
	profile.custom_activated_at = None
	profile.save(ignore_permissions=True)

	# Notify cashier if there's an open session
	open_session = frappe.db.get_value(
		"POS Opening Entry",
		filters={"pos_profile": profile_name, "docstatus": 1, "status": "Open"},
		fieldname=["name", "user"],
		as_dict=True,
	)

	if open_session:
		frappe.publish_realtime(
			"pos_profile_deactivated",
			{
				"profile_name": profile_name,
				"session_name": open_session.name,
				"reason": reason or "Deactivated by manager",
				"timestamp": str(now_datetime()),
			},
			user=open_session.user,
		)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="pos_profile_deactivated",
		details={
			"profile": profile_name,
			"deactivated_by": frappe.session.user,
			"reason": reason,
		},
		reference_document=profile_name,
		reference_type="POS Profile",
	)

	return {
		"success": True,
		"profile_name": profile_name,
		"open_session": open_session.name if open_session else None,
		"message": _("POS Profile '{0}' deactivated.").format(profile_name),
	}


@frappe.whitelist(methods=["GET"])
def get_activation_status(profile_name: str) -> dict:
	"""Check if a POS profile is activated. Available to POS users."""
	frappe.only_for(["Sales User", "Sales Manager", "Store Manager", "System Manager"])

	if not profile_name or not frappe.db.exists("POS Profile", profile_name):
		frappe.throw(_("POS Profile '{0}' not found.").format(profile_name or ""))

	profile_values = frappe.db.get_value(
		"POS Profile",
		profile_name,
		[
			"disabled",
			"custom_is_activated",
			"custom_activated_by",
			"custom_activated_at",
			"custom_auto_deactivate_time",
		],
		as_dict=True,
	)

	if not profile_values:
		return {"is_activated": False, "can_use": False}

	is_activated = bool(getattr(profile_values, "custom_is_activated", 0))
	is_disabled = bool(profile_values.disabled)

	# Check if auto-deactivate time has passed
	auto_deactivate = getattr(profile_values, "custom_auto_deactivate_time", None)
	if is_activated and auto_deactivate:
		now = get_time(now_datetime())
		if now >= auto_deactivate:
			is_activated = False

	return {
		"is_activated": is_activated,
		"can_use": is_activated and not is_disabled,
		"activated_by": getattr(profile_values, "custom_activated_by", None),
		"activated_at": str(getattr(profile_values, "custom_activated_at", ""))
		if getattr(profile_values, "custom_activated_at", None)
		else None,
		"auto_deactivate_time": str(auto_deactivate) if auto_deactivate else None,
	}


@frappe.whitelist(methods=["GET"])
def get_all_activation_statuses() -> dict:
	"""Get activation status for all POS profiles. Manager only."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	profiles = frappe.get_all(
		"POS Profile",
		filters={"disabled": 0},
		fields=[
			"name",
			"custom_is_activated",
			"custom_activated_by",
			"custom_activated_at",
			"custom_auto_deactivate_time",
		],
		order_by="name",
	)

	result = []
	for p in profiles:
		is_activated = bool(getattr(p, "custom_is_activated", 0))
		activated_by_name = ""
		if getattr(p, "custom_activated_by", None):
			activated_by_name = (
				frappe.db.get_value("User", p.custom_activated_by, "full_name") or p.custom_activated_by
			)

		# Check for open session
		open_session = frappe.db.get_value(
			"POS Opening Entry",
			filters={"pos_profile": p.name, "docstatus": 1, "status": "Open"},
			fieldname="name",
		)

		result.append(
			{
				"profile_name": p.name,
				"is_activated": is_activated,
				"activated_by": getattr(p, "custom_activated_by", None),
				"activated_by_name": activated_by_name,
				"activated_at": str(p.custom_activated_at)
				if getattr(p, "custom_activated_at", None)
				else None,
				"auto_deactivate_time": str(p.custom_auto_deactivate_time)
				if getattr(p, "custom_auto_deactivate_time", None)
				else None,
				"has_open_session": bool(open_session),
				"open_session_name": open_session,
			}
		)

	return {"profiles": result, "count": len(result)}


def auto_deactivate_profiles():
	"""
	Scheduler: Check all activated profiles and deactivate if past auto-deactivate time.
	Register in hooks.py scheduler_events.
	"""
	profiles = frappe.get_all(
		"POS Profile",
		filters={"disabled": 0, "custom_is_activated": 1},
		fields=["name", "custom_auto_deactivate_time"],
	)

	now = get_time(now_datetime())
	deactivated = []

	for p in profiles:
		auto_time = getattr(p, "custom_auto_deactivate_time", None)
		if not auto_time:
			continue

		if now >= auto_time:
			frappe.db.set_value(
				"POS Profile",
				p.name,
				{
					"custom_is_activated": 0,
					"custom_activated_by": None,
					"custom_activated_at": None,
				},
			)

			# Notify cashier if session is open
			open_session = frappe.db.get_value(
				"POS Opening Entry",
				filters={"pos_profile": p.name, "docstatus": 1, "status": "Open"},
				fieldname=["name", "user"],
				as_dict=True,
			)
			if open_session:
				frappe.publish_realtime(
					"pos_profile_deactivated",
					{
						"profile_name": p.name,
						"session_name": open_session.name,
						"reason": "Auto-deactivated at scheduled time",
						"timestamp": str(now_datetime()),
					},
					user=open_session.user,
				)

			deactivated.append(p.name)

	return {"deactivated": deactivated, "count": len(deactivated)}


def _notify_activation(event_name: str, data: dict) -> None:
	try:
		managers = frappe.get_all(
			"Has Role",
			filters={"role": ["in", ["Sales Manager", "Store Manager"]], "parenttype": "User"},
			fields=["parent"],
		)
		for mgr in managers:
			frappe.publish_realtime(event_name, data, user=mgr.parent)
	except Exception:
		frappe.log_error("POS Activation Notification Failed", frappe.get_traceback())
