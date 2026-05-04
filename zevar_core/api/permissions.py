"""
POS Permissions API - Role-Based Access Control

Provides permission checks and manager override functionality for POS operations.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime

# Permission levels for POS operations
POS_PERMISSIONS = {
	"pos_access": {"roles": ["Sales User", "Sales Manager", "System Manager"]},
	"create_invoice": {"roles": ["Sales User", "Sales Manager", "System Manager"]},
	"apply_discount": {"roles": ["Sales User", "Sales Manager", "System Manager"], "limit": 10},
	"apply_large_discount": {"roles": ["Sales Manager", "System Manager"], "limit": 100},
	"void_invoice": {"roles": ["Sales Manager", "System Manager"]},
	"process_return": {"roles": ["Sales Manager", "System Manager"]},
	"override_price": {"roles": ["Sales Manager", "System Manager"]},
	"view_reports": {"roles": ["Sales Manager", "System Manager"]},
	"manage_users": {"roles": ["System Manager"]},
	"open_close_register": {"roles": ["Sales User", "Sales Manager", "System Manager"]},
	"process_trade_in": {"roles": ["Sales User", "Sales Manager", "System Manager"]},
	"override_trade_in_2x": {"roles": ["Sales Manager", "System Manager"]},
	"create_layaway": {"roles": ["Sales User", "Sales Manager", "System Manager"]},
	"cancel_layaway": {"roles": ["Sales Manager", "System Manager"]},
}


@frappe.whitelist()
def check_permission(action: str, raise_exception: bool = True) -> bool:
	"""
	Check if current user has permission for a specific POS action.

	Args:
		action: The POS action to check (e.g., 'create_invoice', 'void_invoice')
		raise_exception: Whether to throw exception if not permitted

	Returns:
		True if permitted, False otherwise
	"""
	if action not in POS_PERMISSIONS:
		if raise_exception:
			frappe.throw(_("Unknown permission action: {0}").format(action))
		return False

	permission_config = POS_PERMISSIONS[action]
	user_roles = frappe.get_roles(frappe.session.user)

	# Check if user has any of the required roles
	has_role = any(role in user_roles for role in permission_config["roles"])

	if not has_role:
		if raise_exception:
			frappe.throw(
				_("You don't have permission to perform this action. Required roles: {0}").format(
					", ".join(permission_config["roles"])
				),
				frappe.PermissionError,
			)
		return False

	return True


@frappe.whitelist()
def get_user_permissions() -> dict:
	"""
	Get all POS permissions for the current user.

	Returns:
		Dictionary of permissions with boolean values
	"""
	user_roles = frappe.get_roles(frappe.session.user)
	permissions = {}

	for action, config in POS_PERMISSIONS.items():
		permissions[action] = any(role in user_roles for role in config["roles"])

		# Include discount limit if applicable
		if "limit" in config:
			permissions[f"{action}_limit"] = config["limit"] if permissions[action] else 0

	return permissions


@frappe.whitelist()
def check_discount_permission(discount_percent: float) -> dict:
	"""
	Check if user can apply a specific discount percentage.

	Args:
		discount_percent: The discount percentage to apply

	Returns:
		Dictionary with permission status and whether manager override is needed
	"""
	user_roles = frappe.get_roles(frappe.session.user)

	# Check for large discount permission first
	if any(role in user_roles for role in POS_PERMISSIONS["apply_large_discount"]["roles"]):
		return {"allowed": True, "needs_override": False}

	# Check for regular discount permission
	if any(role in user_roles for role in POS_PERMISSIONS["apply_discount"]["roles"]):
		limit = POS_PERMISSIONS["apply_discount"].get("limit", 10)
		if discount_percent <= limit:
			return {"allowed": True, "needs_override": False}
		else:
			return {
				"allowed": False,
				"needs_override": True,
				"message": _("Discount exceeds {0}% limit. Manager override required.").format(limit),
			}

	return {
		"allowed": False,
		"needs_override": True,
		"message": _("You don't have permission to apply discounts."),
	}


@frappe.whitelist(methods=["POST"])
def request_manager_override(
	action: str,
	reason: str,
	reference_document: str | None = None,
	reference_type: str | None = None,
) -> dict:
	"""
	Request manager override for a restricted action.

	Args:
		action: The action requiring override
		reason: Reason for the override request
		reference_document: Related document name
		reference_type: Related document type

	Returns:
		Override request details
	"""
	check_permission("pos_access")

	# Create override request
	override_request = frappe.new_doc("POS Manager Override")
	override_request.requested_by = frappe.session.user
	override_request.action = action
	override_request.reason = reason
	override_request.status = "Pending"
	override_request.request_time = now_datetime()

	if reference_document and reference_type:
		override_request.reference_document = reference_document
		override_request.reference_type = reference_type

	override_request.insert(ignore_permissions=True)

	return {
		"success": True,
		"request_id": override_request.name,
		"message": _("Override request submitted. Please have a manager approve it."),
	}


@frappe.whitelist(methods=["POST"])
def approve_manager_override(
	request_id: str,
	manager_pin: str,
) -> dict:
	"""
	Approve a manager override request using PIN.

	Args:
		request_id: The override request ID
		manager_pin: Manager's PIN code

	Returns:
		Approval status
	"""
	# Verify manager PIN
	manager = verify_manager_pin(manager_pin)

	if not manager:
		frappe.throw(_("Invalid manager PIN."), frappe.ValidationError)

	# Get override request
	override_request = frappe.get_doc("POS Manager Override", request_id)

	if override_request.status != "Pending":
		frappe.throw(_("This override request has already been processed."))

	# Approve the request
	override_request.status = "Approved"
	override_request.approved_by = manager["user"]
	override_request.approval_time = now_datetime()
	override_request.save(ignore_permissions=True)

	# Log the approval
	log_audit_event(
		action="manager_override_approved",
		details={
			"request_id": request_id,
			"action": override_request.action,
			"requested_by": override_request.requested_by,
			"reason": override_request.reason,
		},
	)

	return {
		"success": True,
		"message": _("Override approved."),
		"approved_by": manager["user"],
	}


@frappe.whitelist()
def verify_manager_pin(pin: str) -> dict | None:
	"""
	Verify a manager's PIN code using bcrypt.

	Args:
		pin: The PIN to verify

	Returns:
		Manager user details if valid, None otherwise
	"""
	if not pin or len(pin) < 4:
		return None

	# Get all managers with hashed PINs set
	managers = frappe.get_all(
		"User",
		filters={
			"enabled": 1,
			"user_type": "System User",
		},
		fields=["name", "full_name", "email", "pos_manager_pin_hash"],
		or_filters=[
			{"pos_manager_pin_hash": ["!=", ""]},
			{"pos_manager_pin_hash": ["is", "set"]},
		],
	)

	for manager in managers:
		if manager.pos_manager_pin_hash:
			try:
				import bcrypt

				# Verify PIN using bcrypt
				if bcrypt.checkpw(pin.encode("utf-8"), manager.pos_manager_pin_hash.encode("utf-8")):
					# Check if user has manager role
					user_roles = frappe.get_roles(manager.name)
					if "Sales Manager" in user_roles or "System Manager" in user_roles:
						return {
							"user": manager.name,
							"full_name": manager.full_name,
							"email": manager.email,
						}
			except (ImportError, ValueError, TypeError):
				# Invalid hash format, skip this user
				continue

	return None


@frappe.whitelist(methods=["POST"])
def set_manager_pin(pin: str) -> dict:
	"""
	Set or update the current user's manager PIN (hashed with bcrypt).

	Args:
		pin: The new PIN to set (will be hashed before storage)

	Returns:
		Success status
	"""
	if not pin or len(pin) < 4:
		frappe.throw(_("PIN must be at least 4 characters long."))

	# Check if user has manager role
	user_roles = frappe.get_roles(frappe.session.user)
	if "Sales Manager" not in user_roles and "System Manager" not in user_roles:
		frappe.throw(_("Only Sales Managers or System Managers can set a manager PIN."))

	try:
		import bcrypt
	except ImportError:
		frappe.throw(_("bcrypt is required to set a manager PIN."))

	# Hash the PIN with bcrypt
	hashed_pin = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

	# Update user's hashed PIN
	frappe.db.set_value(
		"User",
		frappe.session.user,
		"pos_manager_pin_hash",
		hashed_pin,
	)
	frappe.db.commit()  # nosemgrep (manual commit for permission sync)

	return {"success": True, "message": _("Manager PIN updated successfully.")}


@frappe.whitelist()
def get_pos_roles() -> list:
	"""
	Get list of POS-related roles.

	Returns:
		List of role names
	"""
	return ["Sales User", "Sales Manager", "System Manager", "POS User", "Cashier"]


def log_audit_event(
	action: str, details: dict, reference_document: str | None = None, reference_type: str | None = None
):
	"""
	Log an audit event for security tracking.

	Args:
		action: The action being logged
		details: Additional details about the action
		reference_document: Related document
		reference_type: Related document type
	"""
	try:
		audit_log = frappe.new_doc("POS Audit Log")
		audit_log.user = frappe.session.user
		audit_log.event_type = action
		audit_log.category = _get_category_for_action(action)
		audit_log.severity = "Warning" if "denied" in action.lower() or "failed" in action.lower() else "Info"
		audit_log.details = frappe.as_json(details)
		audit_log.timestamp = now_datetime()
		audit_log.ip_address = frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None

		if reference_document:
			audit_log.reference_document = reference_document
		if reference_type:
			audit_log.reference_type = reference_type

		audit_log.insert(ignore_permissions=True)
		frappe.db.commit()  # nosemgrep
	except Exception:
		frappe.log_error("Failed to log audit event", frappe.get_traceback())


def _get_category_for_action(action: str) -> str:
	"""Map action to audit log category."""
	action_lower = action.lower()
	if any(x in action_lower for x in ["invoice", "sale"]):
		return "Sales"
	elif any(x in action_lower for x in ["payment", "refund"]):
		return "Payment"
	elif any(x in action_lower for x in ["discount", "override"]):
		return "Discount"
	elif any(x in action_lower for x in ["session", "register", "cash"]):
		return "Session"
	elif any(x in action_lower for x in ["login", "permission", "manager"]):
		return "Security"
	elif any(x in action_lower for x in ["layaway"]):
		return "Layaway"
	elif any(x in action_lower for x in ["customer"]):
		return "Customer"
	elif any(x in action_lower for x in ["stock", "inventory"]):
		return "Inventory"
	return "Sales"
