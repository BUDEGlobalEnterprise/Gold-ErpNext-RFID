"""
POS Session API - Opening and closing cash register sessions

Provides endpoints for:
- Opening a new POS session
- Closing an active session with reconciliation
- Getting current session status
"""

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, now_datetime, nowdate, time_diff_in_hours


@frappe.whitelist()
def get_session_status() -> dict:
	"""
	Get the current POS session status for the logged-in user.

	Returns:
		dict: Session status with details if active session exists
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	user = frappe.session.user

	# Find active POS Opening Entry for this user
	active_session_name = frappe.db.get_value(
		"POS Opening Entry",
		filters={"user": user, "docstatus": 1, "status": "Open"},
		fieldname="name",
		order_by="creation desc",
	)

	if not active_session_name:
		return {
			"has_active_session": False,
			"session": None,
		}

	session = frappe.get_doc("POS Opening Entry", active_session_name)
	session_name = session.name
	pos_profile = session.pos_profile
	period_start = session.period_start_date
	company = session.company
	opening_amount = sum(flt(row.opening_amount) for row in session.balance_details)

	# Calculate session duration
	duration_hours = 0
	if period_start:
		duration_hours = time_diff_in_hours(now_datetime(), get_datetime(period_start))

	# Get sales count and total for this session (cumulative since session start)
	# Calculate total sales since opening date
	start_date = (
		session.period_start_date.date()
		if hasattr(session.period_start_date, "date")
		else session.period_start_date
	)
	invoices = frappe.db.sql(
		"""
		SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total
		FROM `tabSales Invoice`
		WHERE owner = %s
		AND posting_date >= %s
		AND docstatus = 1
		""",
		(user, start_date),
		as_dict=True,
	)
	invoices = invoices[0] if invoices else {"count": 0, "total": 0}

	# Get today's sales count and total (separate from cumulative)
	today = nowdate()
	today_invoices = frappe.db.sql(
		"""
		SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total
		FROM `tabSales Invoice`
		WHERE owner = %s
		AND posting_date = %s
		AND docstatus = 1
		""",
		(user, today),
		as_dict=True,
	)
	today_invoices = today_invoices[0] if today_invoices else {"count": 0, "total": 0}

	# Calculate cash specifically for expected balance
	cash_payments = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(sip.amount), 0)
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.posting_date >= %s
		AND si.docstatus = 1
		AND sip.mode_of_payment = 'Cash'
		""",
		(user, start_date),
	)[0][0]

	# Get opening time
	opening_time = frappe.db.get_value("POS Opening Entry", session_name, "period_start_date")

	# Get warehouse from POS Profile
	warehouse = frappe.db.get_value("POS Profile", pos_profile, "warehouse")

	return {
		"has_active_session": True,
		"session": {
			"name": session_name,
			"pos_profile": pos_profile,
			"company": company,
			"warehouse": warehouse,
			"opening_date": period_start.date()
			if hasattr(period_start, "date")
			else str(period_start).split()[0],
			"opening_time": str(opening_time.time())
			if opening_time and hasattr(opening_time, "time")
			else "",
			"opening_balance": flt(opening_amount),
			"sales_count": invoices.count,
			"sales_total": invoices.total,
			"today_sales_count": today_invoices.count,
			"today_sales_total": today_invoices.total,
			"expected_cash": flt(cash_payments),
			"duration_hours": round(duration_hours, 2),
		},
	}


def _mark_opening_entry_closed(session_name: str, closing_entry_name: str) -> None:
	"""Close the opening entry without hitting ERPNext's stale-save edge case."""
	frappe.db.set_value(
		"POS Opening Entry",
		session_name,
		"pos_closing_entry",
		closing_entry_name,
		update_modified=False,
	)
	opening_entry = frappe.get_doc("POS Opening Entry", session_name)
	opening_entry.reload()
	opening_entry.set_status(update=True, update_modified=False)


def _normalize_cash_breakdown(cash_breakdown):
	"""Convert legacy JSON breakdown payloads into payment rows."""
	if not cash_breakdown:
		return []

	breakdown_list = frappe.parse_json(cash_breakdown) if isinstance(cash_breakdown, str) else cash_breakdown
	if isinstance(breakdown_list, dict):
		total_amount = 0
		for denomination, count in breakdown_list.items():
			total_amount += flt(denomination) * flt(count)
		return [{"mode_of_payment": "Cash", "amount": total_amount}]

	return breakdown_list or []


@frappe.whitelist(methods=["POST"])
def open_pos_session(
	pos_profile: str,
	opening_balance: float,
	cash_breakdown: str | list | None = None,
	notes=None,
) -> dict:
	"""
	Open a new POS session (cash register).

	Args:
		pos_profile: Name of the POS Profile
		opening_balance: Opening cash amount
		cash_breakdown: JSON string or list of denomination breakdown
		notes: Optional opening notes

	Returns:
		dict: Success status and session details
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	user = frappe.session.user

	# Validate inputs
	if not pos_profile:
		frappe.throw(_("POS Profile is required."))

	if not frappe.db.exists("POS Profile", pos_profile):
		frappe.throw(_("POS Profile '{0}' not found.").format(pos_profile))

	# Check for existing open session
	existing_session = frappe.db.get_value(
		"POS Opening Entry",
		filters={
			"user": user,
			"docstatus": 1,
			"status": "Open",
		},
	)

	if existing_session:
		frappe.throw(
			_("You already have an open session: {0}. Please close it first.").format(existing_session)
		)

	# Parse cash breakdown if provided
	breakdown_list = _normalize_cash_breakdown(cash_breakdown)

	# Get POS Profile details
	profile = frappe.get_doc("POS Profile", pos_profile)

	if profile.get("custom_enforce_fixed_float"):
		fixed_float = flt(profile.get("custom_fixed_opening_float", 300.0))
		if flt(opening_balance) != fixed_float:
			frappe.throw(_("Opening balance must be exactly ${0} per store policy.").format(fixed_float))
		opening_balance = fixed_float

	try:
		# Create POS Opening Entry
		opening_entry = frappe.new_doc("POS Opening Entry")
		opening_entry.pos_profile = pos_profile
		opening_entry.user = user
		opening_entry.company = profile.company
		opening_entry.period_start_date = now_datetime()
		# opening_amount is not a field in the main DocType, it's in balance_details

		if notes:
			opening_entry.remarks = notes

		# Add cash breakdown details if provided
		for item in breakdown_list:
			if flt(item.get("amount", 0)) > 0:
				opening_entry.append(
					"balance_details",
					{
						"mode_of_payment": item.get("mode_of_payment", "Cash"),
						"opening_amount": flt(item.get("amount", 0)),
					},
				)

		# If no breakdown provided, add default cash entry
		if not breakdown_list and flt(opening_balance) > 0:
			opening_entry.append(
				"balance_details",
				{
					"mode_of_payment": "Cash",
					"opening_amount": flt(opening_balance),
				},
			)

		opening_entry.insert(ignore_permissions=True)
		opening_entry.submit()

		from zevar_core.api.audit_log import log_event_safely

		log_event_safely(
			event_type="session_opened",
			details={
				"session_name": opening_entry.name,
				"pos_profile": pos_profile,
				"opening_balance": flt(opening_balance),
				"cash_breakdown": breakdown_list,
				"notes": notes,
			},
			reference_document=opening_entry.name,
			reference_type="POS Opening Entry",
		)

		# Notify managers about session opening
		_notify_managers(
			"pos_session_event",
			{
				"event_type": "session_opened",
				"user": frappe.session.user,
				"session_name": opening_entry.name,
				"pos_profile": pos_profile,
				"opening_balance": flt(opening_balance),
				"timestamp": str(now_datetime()),
			},
		)

		return {
			"success": True,
			"session_name": opening_entry.name,
			"status": "Open",
			"message": _("POS Session opened successfully"),
			"opening_balance": flt(opening_balance),
		}

	except Exception as e:
		frappe.log_error("POS Session Opening Failed", frappe.get_traceback())
		if isinstance(e, frappe.ValidationError):
			raise
		frappe.throw(_("Failed to open POS session: {0}").format(str(e)))


@frappe.whitelist()
def preview_close(session_name: str, total_cash_counted: float) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)
	profile = frappe.get_doc("POS Profile", session.pos_profile)

	fixed_float = (
		flt(profile.get("custom_fixed_opening_float", 300.0))
		if profile.get("custom_enforce_fixed_float")
		else sum(flt(row.opening_amount) for row in session.balance_details)
	)

	# Calculate expected amounts per payment mode
	start_date = (
		session.period_start_date.date()
		if hasattr(session.period_start_date, "date")
		else session.period_start_date
	)
	payments = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment, SUM(sip.amount) as amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.docstatus = 1
		AND si.posting_date >= %s
		GROUP BY sip.mode_of_payment
		""",
		(session.user, start_date),
		as_dict=True,
	)

	expected_cash = sum(flt(p.amount) for p in payments if p.mode_of_payment == "Cash")
	total_expected_sales = sum(flt(p.amount) for p in payments)

	# Include cash movements in expected balance
	cash_movements = frappe.get_all(
		"Cash Movement",
		filters={"session": session_name, "docstatus": 1},
		fields=["movement_type", "amount"],
	)
	net_cash_movement = sum(
		flt(m.amount) if m.movement_type == "Cash In" else -flt(m.amount)
		for m in cash_movements
	)

	# Calculate variance against total expected (since UI has only one input)
	total_actual = flt(total_cash_counted)
	total_expected_balance = fixed_float + total_expected_sales + net_cash_movement
	variance = total_actual - total_expected_balance

	return {
		"opening_balance": fixed_float,
		"expected_cash": expected_cash,
		"total_expected": total_expected_balance,
		"variance": variance,
		"payments": payments,
		"cash_taken_in": flt(total_cash_counted) - fixed_float,
		"alert_threshold": flt(profile.get("custom_variance_alert_threshold", 5.0)),
	}


@frappe.whitelist(methods=["POST"])
def close_pos_session_v2(
	session_name: str,
	total_cash_counted: float,
	breakdown: str | list | None = None,
	notes=None,
) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	user = frappe.session.user

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	if session.user != user:
		if "Sales Manager" not in frappe.get_roles(user) and "System Manager" not in frappe.get_roles(user):
			frappe.throw(_("You can only close your own sessions."))

	if session.docstatus != 1:
		frappe.throw(_("Session must be submitted before closing."))

	if session.status != "Open":
		frappe.throw(_("Session is already closed."))

	profile = frappe.get_doc("POS Profile", session.pos_profile)

	# If fixed float is not enforced, delegate to old logic
	if not profile.get("custom_enforce_fixed_float"):
		return close_pos_session(session_name, total_cash_counted, breakdown, notes)

	preview = preview_close(session_name, total_cash_counted)

	fixed_float = preview["opening_balance"]
	cash_taken_in = preview["cash_taken_in"]
	expected_cash = preview["expected_cash"]
	variance = preview["variance"]
	alert_threshold = preview["alert_threshold"]

	if abs(variance) > alert_threshold:
		if "Sales Manager" not in frappe.get_roles(user) and "System Manager" not in frappe.get_roles(user):
			frappe.throw(
				_("Variance of ${0} exceeds threshold of ${1}. Manager override required.").format(
					abs(variance), alert_threshold
				)
			)

	breakdown_list = _normalize_cash_breakdown(breakdown)

	try:
		from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import (
			make_closing_entry_from_opening,
		)

		closing_entry = make_closing_entry_from_opening(session)
		closing_entry.period_end_date = now_datetime()

		if notes:
			closing_entry.remarks = notes

		# Calculate expected amounts per mode from invoices
		start_date = (
			session.period_start_date.date()
			if hasattr(session.period_start_date, "date")
			else session.period_start_date
		)
		payments = frappe.db.sql(
			"""
			SELECT sip.mode_of_payment, SUM(sip.amount) as amount
			FROM `tabSales Invoice Payment` sip
			JOIN `tabSales Invoice` si ON sip.parent = si.name
			WHERE si.owner = %s
			AND si.docstatus = 1
			AND si.posting_date >= %s
			GROUP BY sip.mode_of_payment
			""",
			(session.user, start_date),
			as_dict=True,
		)

		# Include cash movements
		cash_movements = frappe.get_all(
			"Cash Movement",
			filters={"session": session_name, "docstatus": 1},
			fields=["movement_type", "amount"],
		)
		net_cash_movement = sum(
			flt(m.amount) if m.movement_type == "Cash In" else -flt(m.amount)
			for m in cash_movements
		)

		# Calculate total variance to distribute to Cash
		total_actual = flt(total_cash_counted)
		total_sales = sum(flt(p.amount) for p in payments)
		total_expected = fixed_float + total_sales + net_cash_movement
		total_variance = total_actual - total_expected

		# Sync payment reconciliation for ALL modes
		closing_entry.set("payment_reconciliation", [])

		# Track if we handled Cash
		cash_handled = False

		for p in payments:
			mode = p.mode_of_payment
			expected_sale = flt(p.amount)
			opening = fixed_float if mode == "Cash" else 0
			expected_total = opening + expected_sale
			closing = 0

			if mode == "Cash":
				# Cash gets the opening + expected sales + the total variance
				closing = expected_total + total_variance
				cash_handled = True
			else:
				# Other modes: closing matches expected
				closing = expected_total

			closing_entry.append(
				"payment_reconciliation",
				{
					"mode_of_payment": mode,
					"opening_amount": opening,
					"expected_amount": expected_total,
					"closing_amount": closing,
				},
			)

		# Ensure Cash row exists even if no cash sales
		if not cash_handled:
			closing_entry.append(
				"payment_reconciliation",
				{
					"mode_of_payment": "Cash",
					"opening_amount": fixed_float,
					"expected_amount": fixed_float,
					"closing_amount": fixed_float + total_variance,
				},
			)

		closing_entry.insert(ignore_permissions=True)

		def _safe_update_opening_entry(for_cancel: bool = False) -> None:
			if for_cancel:
				return
			_mark_opening_entry_closed(session_name, closing_entry.name)

		closing_entry.update_opening_entry = _safe_update_opening_entry
		closing_entry.submit()

		# Write to POS Audit Log
		frappe.get_doc(
			{
				"doctype": "POS Audit Log",
				"user": user,
				"event_type": "fixed_float_enforced",
				"description": f"Session closed with fixed float {fixed_float}. Total counted: {total_cash_counted}. Variance: {variance}",
				"reference_document": closing_entry.name,
				"reference_type": "POS Closing Entry",
				"payload": frappe.as_json(
					{
						"fixed_float": fixed_float,
						"total_counted": total_cash_counted,
						"cash_taken_in": cash_taken_in,
						"expected": expected_cash,
						"variance": variance,
					}
				),
			}
		).insert(ignore_permissions=True)

		variance_status = "balanced"
		if variance > 0:
			variance_status = "excess"
		elif variance < 0:
			variance_status = "shortage"

		# Notify managers about session closing
		_notify_managers(
			"pos_session_event",
			{
				"event_type": "session_closed",
				"user": session.user,
				"session_name": session_name,
				"pos_profile": session.pos_profile,
				"closing_entry": closing_entry.name,
				"variance": variance,
				"timestamp": str(now_datetime()),
			},
		)

		return {
			"success": True,
			"closing_entry": closing_entry.name,
			"message": _("POS Session closed successfully"),
			"opening_balance": fixed_float,
			"total_sales": total_sales,
			"closing_balance": flt(total_cash_counted),
			"cash_taken_in": cash_taken_in,
			"expected_balance": fixed_float + expected_cash,
			"variance": variance,
			"variance_status": variance_status,
			"breakdown_by_mode": breakdown_list,
		}

	except Exception as e:
		frappe.log_error("POS Session Closing Failed", frappe.get_traceback())
		if isinstance(e, frappe.ValidationError):
			raise
		frappe.throw(_("Failed to close POS session: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def close_pos_session(
	session_name: str,
	closing_balance: float,
	cash_breakdown: str | list | None = None,
	notes=None,
) -> dict:
	"""
	Close an active POS session with reconciliation.

	Args:
		session_name: Name of the POS Opening Entry
		closing_balance: Actual closing cash amount
		cash_breakdown: JSON string or list of denomination breakdown
		notes: Optional closing notes

	Returns:
		dict: Success status, variance details, and summary
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	user = frappe.session.user

	# Validate session exists and belongs to user
	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	if session.user != user:
		# Allow managers to close other users' sessions
		if "Sales Manager" not in frappe.get_roles(user) and "System Manager" not in frappe.get_roles(user):
			frappe.throw(_("You can only close your own sessions."))

	if session.docstatus != 1:
		frappe.throw(_("Session must be submitted before closing."))

	if session.status != "Open":
		frappe.throw(_("Session is already closed."))

	# Parse cash breakdown if provided
	breakdown_list = _normalize_cash_breakdown(cash_breakdown)

	# Calculate expected closing balance
	opening_balance = sum(flt(row.opening_amount) for row in session.balance_details)

	# Get total sales for this session
	sales_data = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(grand_total), 0) as total
		FROM `tabSales Invoice`
		WHERE owner = %s
		AND creation >= %s
		AND docstatus = 1
		""",
		(user, session.creation),
		as_dict=True,
	)

	# Include cash movements
	cash_movements = frappe.get_all(
		"Cash Movement",
		filters={"session": session_name, "docstatus": 1},
		fields=["movement_type", "amount"],
	)
	net_cash_movement = sum(
		flt(m.amount) if m.movement_type == "Cash In" else -flt(m.amount)
		for m in cash_movements
	)

	total_sales = flt(sales_data[0].get("total", 0)) if sales_data else 0
	expected_balance = opening_balance + total_sales + net_cash_movement
	variance = flt(closing_balance) - expected_balance

	try:
		from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import (
			make_closing_entry_from_opening,
		)

		closing_entry = make_closing_entry_from_opening(session)
		closing_entry.period_end_date = now_datetime()

		if notes:
			closing_entry.remarks = notes

		closing_entry.set("payment_reconciliation", [])

		# Add cash breakdown details
		for item in breakdown_list:
			if flt(item.get("amount", 0)) > 0:
				closing_entry.append(
					"payment_reconciliation",
					{
						"mode_of_payment": item.get("mode_of_payment", "Cash"),
						"opening_amount": flt(item.get("opening_amount", 0)),
						"closing_amount": flt(item.get("amount", 0)),
						"expected_amount": flt(item.get("expected_amount", item.get("amount", 0))),
					},
				)

		# If no breakdown provided, add default cash entry
		if not breakdown_list and flt(closing_balance) > 0:
			closing_entry.append(
				"payment_reconciliation",
				{
					"mode_of_payment": "Cash",
					"opening_amount": opening_balance,
					"closing_amount": flt(closing_balance),
					"expected_amount": expected_balance,
				},
			)

		closing_entry.insert(ignore_permissions=True)

		def _safe_update_opening_entry(for_cancel: bool = False) -> None:
			if for_cancel:
				return
			_mark_opening_entry_closed(session_name, closing_entry.name)

		closing_entry.update_opening_entry = _safe_update_opening_entry
		closing_entry.submit()

		from zevar_core.api.audit_log import log_event_safely

		# Determine variance status
		variance_status = "balanced"
		if variance > 0:
			variance_status = "excess"
		elif variance < 0:
			variance_status = "shortage"

		log_event_safely(
			event_type="session_closed",
			details={
				"session_name": session_name,
				"closing_entry": closing_entry.name,
				"pos_profile": session.pos_profile,
				"opening_balance": flt(opening_balance),
				"closing_balance": flt(closing_balance),
				"expected_balance": flt(expected_balance),
				"total_sales": flt(total_sales),
				"variance": flt(variance),
				"variance_status": variance_status,
				"notes": notes,
			},
			reference_document=closing_entry.name,
			reference_type="POS Closing Entry",
		)

		if variance != 0:
			log_event_safely(
				event_type="cash_variance_detected",
				details={
					"session_name": session_name,
					"closing_entry": closing_entry.name,
					"variance": flt(variance),
					"variance_status": variance_status,
					"expected_balance": flt(expected_balance),
					"closing_balance": flt(closing_balance),
				},
				reference_document=closing_entry.name,
				reference_type="POS Closing Entry",
			)

		# Notify managers about session closing
		_notify_managers(
			"pos_session_event",
			{
				"event_type": "session_closed",
				"user": session.user,
				"session_name": session_name,
				"pos_profile": session.pos_profile,
				"closing_entry": closing_entry.name,
				"variance": variance,
				"timestamp": str(now_datetime()),
			},
		)

		return {
			"success": True,
			"closing_entry": closing_entry.name,
			"message": _("POS Session closed successfully"),
			"opening_balance": opening_balance,
			"total_sales": total_sales,
			"closing_balance": flt(closing_balance),
			"expected_balance": expected_balance,
			"variance": variance,
			"variance_status": variance_status,
		}

	except Exception as e:
		frappe.log_error("POS Session Closing Failed", frappe.get_traceback())
		if isinstance(e, frappe.ValidationError):
			raise
		frappe.throw(_("Failed to close POS session: {0}").format(str(e)))


@frappe.whitelist()
def get_session_sales(session_name: str) -> dict:
	"""
	Get all sales for a specific POS session.

	Args:
		session_name: Name of the POS Opening Entry

	Returns:
		dict: List of sales invoices for the session
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	# Get all sales invoices for this session
	sales = frappe.get_all(
		"Sales Invoice",
		filters={
			"owner": session.user,
			"creation": [">=", session.creation],
			"docstatus": 1,
		},
		fields=[
			"name",
			"customer",
			"posting_date",
			"posting_time",
			"grand_total",
			"status",
			"currency",
		],
		order_by="posting_date, posting_time",
	)

	# Calculate totals
	total = sum(flt(s.get("grand_total", 0)) for s in sales)

	return {
		"session_name": session_name,
		"sales": sales,
		"total_count": len(sales),
		"total_amount": total,
	}


@frappe.whitelist()
def get_all_active_sessions() -> dict:
	"""
	Get all currently open POS sessions. Admin/manager only.

	Returns:
		dict: List of active sessions with user, profile, and sales info.
	"""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	sessions = frappe.get_all(
		"POS Opening Entry",
		filters={"docstatus": 1, "status": "Open"},
		fields=["name", "user", "pos_profile", "company", "period_start_date"],
		order_by="period_start_date desc",
	)

	enriched = []
	for session in sessions:
		# Get user full name
		full_name = frappe.db.get_value("User", session.user, "full_name") or session.user
		session_dict = {
			"name": session.name,
			"user": session.user,
			"user_full_name": full_name,
			"pos_profile": session.pos_profile,
			"company": session.company,
			"period_start_date": str(session.period_start_date) if session.period_start_date else None,
		}

		# Sum opening amount from balance details
		session_doc = frappe.get_doc("POS Opening Entry", session.name)
		opening_amount = sum(flt(d.opening_amount) for d in session_doc.balance_details)
		session_dict["opening_amount"] = opening_amount

		# Get warehouse from POS Profile
		warehouse = frappe.db.get_value("POS Profile", session.pos_profile, "warehouse")
		session_dict["warehouse"] = warehouse

		# Get sales count and total for this session (cumulative since session start)
		sales_data = frappe.db.sql(
			"""
			SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total
			FROM `tabSales Invoice`
			WHERE owner = %s
			AND creation >= %s
			AND docstatus = 1
			""",
			(session.user, session_doc.creation),
			as_dict=True,
		)
		session_dict["sales_count"] = sales_data[0].get("count", 0) if sales_data else 0
		session_dict["sales_total"] = flt(sales_data[0].get("total", 0)) if sales_data else 0

		# Get today's sales for this session
		today_sales_data = frappe.db.sql(
			"""
			SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total
			FROM `tabSales Invoice`
			WHERE owner = %s
			AND posting_date = %s
			AND docstatus = 1
			""",
			(session.user, nowdate()),
			as_dict=True,
		)
		session_dict["today_sales_count"] = today_sales_data[0].get("count", 0) if today_sales_data else 0
		session_dict["today_sales_total"] = flt(today_sales_data[0].get("total", 0)) if today_sales_data else 0

		session_dict["duration_hours"] = round(
			time_diff_in_hours(now_datetime(), get_datetime(session.period_start_date)), 2
		)

		enriched.append(session_dict)

	return {
		"sessions": enriched,
		"total_count": len(enriched),
	}


@frappe.whitelist(methods=["POST"])
def force_close_session(session_name: str, reason: str | None = None) -> dict:
	"""
	Force-close another user's POS session. Admin/manager only.

	Args:
		session_name: Name of the POS Opening Entry to close
		reason: Reason for force closure

	Returns:
		dict: Success status and closing details
	"""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	if session.status != "Open":
		frappe.throw(_("Session is already closed."))

	# Get expected closing balance
	opening_balance = sum(flt(row.opening_amount) for row in session.balance_details)

	sales_data = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(grand_total), 0) as total
		FROM `tabSales Invoice`
		WHERE owner = %s
		AND creation >= %s
		AND docstatus = 1
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	total_sales = flt(sales_data[0].get("total", 0)) if sales_data else 0
	closing_balance = opening_balance + total_sales

	# Build notes
	force_close_note = f"Force closed by {frappe.session.user}"
	if reason:
		force_close_note += f". Reason: {reason}"
	closing_notes = f"{session.remarks or ''}\n{force_close_note}".strip()

	return close_pos_session(
		session_name=session_name,
		closing_balance=closing_balance,
		cash_breakdown=None,
		notes=closing_notes,
	)


def _notify_managers(event_name: str, data: dict) -> None:
	"""Send a realtime event to all users with Sales Manager or Store Manager role."""
	try:
		managers = frappe.get_all(
			"Has Role",
			filters={"role": ["in", ["Sales Manager", "Store Manager"]], "parenttype": "User"},
			fields=["parent"],
		)
		for mgr in managers:
			frappe.publish_realtime(event_name, data, user=mgr.parent)
	except Exception:
		frappe.log_error("POS Manager Notification Failed", frappe.get_traceback())


@frappe.whitelist()
def get_live_sales_feed(hours: int = 24) -> dict:
	"""
	Get recent sales events for live monitoring. Admin/manager only.

	Args:
		hours: Number of hours to look back (default 24)

	Returns:
		dict: Recent invoices, open sessions, and summary stats
	"""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	from frappe.utils import add_hours
	from frappe.utils import now_datetime as _now

	since = add_hours(_now(), -int(hours or 24))

	# Get recent POS invoices
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"creation": [">=", since], "docstatus": 1, "is_pos": 1},
		fields=["name", "customer", "grand_total", "owner", "posting_date", "posting_time", "creation"],
		order_by="creation desc",
		limit=100,
	)

	# Enrich with user full names
	if invoices:
		owner_ids = list({inv.owner for inv in invoices if inv.owner})
		user_names = {}
		if owner_ids:
			users = frappe.get_all("User", filters={"name": ["in", owner_ids]}, fields=["name", "full_name"])
			user_names = {u.name: u.full_name for u in users}
		for inv in invoices:
			inv["salesperson_name"] = user_names.get(inv.owner, inv.owner)

	# Get open sessions
	open_sessions = frappe.get_all(
		"POS Opening Entry",
		filters={"docstatus": 1, "status": "Open"},
		fields=["name", "user", "pos_profile", "period_start_date"],
	)

	# Enrich sessions
	if open_sessions:
		session_user_ids = list({s.user for s in open_sessions if s.user})
		session_user_names = {}
		if session_user_ids:
			users = frappe.get_all(
				"User", filters={"name": ["in", session_user_ids]}, fields=["name", "full_name"]
			)
			session_user_names = {u.name: u.full_name for u in users}
		for s in open_sessions:
			s["user_full_name"] = session_user_names.get(s.user, s.user)
			s["warehouse"] = frappe.db.get_value("POS Profile", s.pos_profile, "warehouse")
			s["duration_hours"] = round(
				time_diff_in_hours(now_datetime(), get_datetime(s.period_start_date)), 2
			)

	return {
		"recent_invoices": invoices,
		"open_sessions": open_sessions,
		"summary": {
			"total_sales": sum(flt(i.grand_total) for i in invoices),
			"invoice_count": len(invoices),
			"open_session_count": len(open_sessions),
			"hours": int(hours or 24),
		},
	}

@frappe.whitelist(methods=["POST"])
def record_cash_movement(
	session_name: str,
	movement_type: str,
	amount: float,
	reason: str,
	notes=None,
	manager_pin=None,
) -> dict:
	"""Record a cash in/out movement during an active POS session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	session = frappe.get_doc("POS Opening Entry", session_name)
	if session.status != "Open":
		frappe.throw(_("Session is not open"))
	authorized_by = None
	if movement_type == "Cash Out" and flt(amount) > 100:
		if not manager_pin:
			frappe.throw(_("Manager PIN required for cash out over $100"))
		from zevar_core.api.permissions import verify_manager_pin
		manager = verify_manager_pin(manager_pin)
		if not manager:
			frappe.throw(_("Invalid manager PIN"))
		authorized_by = manager["user"]
	movement = frappe.new_doc("Cash Movement")
	movement.session = session_name
	movement.movement_type = movement_type
	movement.amount = flt(amount)
	movement.reason = reason
	movement.notes = notes
	movement.authorized_by = authorized_by
	movement.insert(ignore_permissions=True)
	movement.submit()
	return {
		"success": True,
		"movement_name": movement.name,
		"message": _("Cash {0} of ${1} recorded").format(
			"in" if movement_type == "Cash In" else "out", flt(amount)
		),
	}
@frappe.whitelist()
def get_cash_movements(session_name: str) -> dict:
	"""Get all cash movements for a session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	movements = frappe.get_all(
		"Cash Movement",
		filters={"session": session_name, "docstatus": 1},
		fields=[
			"name",
			"movement_type",
			"amount",
			"reason",
			"notes",
			"authorized_by",
			"creation",
		],
		order_by="creation asc",
	)
	total_in = sum(flt(m.amount) for m in movements if m.movement_type == "Cash In")
	total_out = sum(flt(m.amount) for m in movements if m.movement_type == "Cash Out")
	return {
		"movements": movements,
		"total_in": total_in,
		"total_out": total_out,
		"net": total_in - total_out,
	}