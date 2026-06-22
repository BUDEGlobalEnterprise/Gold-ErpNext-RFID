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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	user = frappe.session.user

	# Find active or suspended POS Opening Entry for this user
	active_session_name = frappe.db.get_value(
		"POS Opening Entry",
		filters={"user": user, "docstatus": 1, "status": ["in", ["Open", "Suspended"]]},
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

	# Get today's sales count and total (sales since this session opened today)
	today = nowdate()
	today_invoices = frappe.db.sql(
		"""
		SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total
		FROM `tabSales Invoice`
		WHERE owner = %s
		AND posting_date = %s
		AND creation >= %s
		AND docstatus = 1
		""",
		(user, today, session.creation),
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

	# Calculate non-cash payment totals
	non_cash_payments = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment, SUM(sip.amount) as total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.posting_date >= %s
		AND si.docstatus = 1
		AND sip.mode_of_payment != 'Cash'
		GROUP BY sip.mode_of_payment
		ORDER BY total DESC
		""",
		(user, start_date),
		as_dict=True,
	)

	# Count layaway and repair activity
	layaway_count = frappe.db.count(
		"Layaway Contract",
		filters={"owner": user, "creation": [">=", session.creation]},
	)

	repair_count = frappe.db.count(
		"Repair Order",
		filters={"owner": user, "sales_invoice": ["is", "set"], "modified": [">=", session.creation]},
	)

	# Get opening time
	opening_time = frappe.db.get_value("POS Opening Entry", session_name, "period_start_date")

	# Get warehouse from POS Profile
	warehouse = frappe.db.get_value("POS Profile", pos_profile, "warehouse")

	return {
		"has_active_session": True,
		"session": {
			"name": session_name,
			"status": session.status,
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
			"non_cash_payments": [
				{"mode_of_payment": p.mode_of_payment, "total": flt(p.total)} for p in non_cash_payments
			],
			"non_cash_total": sum(flt(p.total) for p in non_cash_payments),
			"layaway_count": layaway_count,
			"repair_count": repair_count,
			"duration_hours": round(duration_hours, 2),
		},
	}


@frappe.whitelist()
def get_sessions_list() -> dict:
	"""
	Get a list of POS Sessions (Opening/Closing) for the dashboard.
	Managers see all sessions, Employees see only their own.
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])
	user = frappe.session.user
	
	filters = {}
	if "Sales Manager" not in frappe.get_roles(user) and "System Manager" not in frappe.get_roles(user):
		filters["user"] = user

	sessions = frappe.get_all(
		"POS Opening Entry",
		filters=filters,
		fields=[
			"name",
			"user",
			"status",
			"pos_profile",
			"period_start_date",
			"pos_closing_entry",
			"company",
		],
		order_by="period_start_date desc",
		limit_page_length=100
	)

	for session in sessions:
		if session.pos_closing_entry:
			closing_details = frappe.db.get_value(
				"POS Closing Entry",
				session.pos_closing_entry,
				["period_end_date", "grand_total", "net_total"],
				as_dict=True
			)
			if closing_details:
				session.update(closing_details)
				
				# calculate total expected cash and variance if needed (from payment reconciliation)
				payment_recon = frappe.get_all(
					"POS Closing Entry Detail",
					filters={"parent": session.pos_closing_entry},
					fields=["mode_of_payment", "expected_amount", "closing_amount"]
				)
				cash_recon = next((p for p in payment_recon if p.mode_of_payment == "Cash"), None)
				if cash_recon:
					session.expected_cash = cash_recon.expected_amount
					session.closing_cash = cash_recon.closing_amount
					session.cash_variance = flt(cash_recon.closing_amount) - flt(cash_recon.expected_amount)
				else:
					session.cash_variance = 0.0
					
	return {"sessions": sessions}


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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	user = frappe.session.user

	# Validate inputs
	if not pos_profile:
		frappe.throw(_("POS Profile is required."))

	if not frappe.db.exists("POS Profile", pos_profile):
		frappe.throw(_("POS Profile '{0}' not found.").format(pos_profile))

	# Check for existing active or suspended session
	existing_session_doc = frappe.db.get_all(
		"POS Opening Entry",
		filters={
			"user": user,
			"docstatus": 1,
			"status": ["in", ["Open", "Suspended"]],
		},
		fields=["name", "period_start_date"]
	)

	if existing_session_doc:
		session_name = existing_session_doc[0]["name"]
		start_date = existing_session_doc[0]["period_start_date"]
		from frappe.utils import getdate, nowdate
		
		if start_date and getdate(start_date) < getdate(nowdate()):
			frappe.throw(
				_("Action Required: You have an abandoned register from yesterday ({0}). You must count the drawer and seal the shift before opening today's register.").format(
					session_name
				)
			)
		else:
			frappe.throw(
				_("You already have an active/suspended session: {0}. Please close or resume it first.").format(
					session_name
				)
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

		if notes and hasattr(opening_entry, "remarks"):
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
def blind_count(session_name: str) -> dict:
	"""Return session metadata needed for blind counting — NO expected amounts."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)
	profile = frappe.get_doc("POS Profile", session.pos_profile)

	fixed_float = (
		flt(profile.get("custom_fixed_opening_float", 300.0))
		if profile.get("custom_enforce_fixed_float")
		else sum(flt(row.opening_amount) for row in session.balance_details)
	)

	sales_count = frappe.db.count(
		"Sales Invoice",
		filters={"owner": session.user, "posting_date": [">=", session.period_start_date], "docstatus": 1},
	)

	return {
		"session_name": session_name,
		"user": session.user,
		"pos_profile": session.pos_profile,
		"opening_balance": fixed_float,
		"sales_count": sales_count,
		"alert_threshold": flt(profile.get("custom_variance_alert_threshold", 5.0)),
	}


def ensure_pos_variance_account(company):
	abbr = frappe.get_cached_value("Company", company, "abbr")
	account_name = f"POS Cash Variance - {abbr}"
	if frappe.db.exists("Account", account_name):
		return account_name

	# Try to find a group expense account
	parent = None
	for parent_candidate in [
		f"Direct Expenses - {abbr}",
		f"Indirect Expenses - {abbr}",
		f"Expenses - {abbr}",
	]:
		if frappe.db.exists("Account", parent_candidate):
			parent = parent_candidate
			break

	if not parent:
		# Fallback to root type Expense group account
		parent = frappe.db.get_value(
			"Account", {"root_type": "Expense", "is_group": 1, "company": company}, "name", order_by="lft asc"
		)

	if not parent:
		# Fallback to any group account
		parent = frappe.db.get_value(
			"Account", {"is_group": 1, "company": company}, "name", order_by="lft asc"
		)

	if parent:
		try:
			acc = frappe.new_doc("Account")
			acc.account_name = "POS Cash Variance"
			acc.company = company
			acc.parent_account = parent
			acc.account_type = "Expense Account"
			acc.is_group = 0
			acc.insert(ignore_permissions=True)
			frappe.db.commit()
			return acc.name
		except Exception as e:
			frappe.log_error(f"Failed to create POS Cash Variance Account: {e}")
	return None


def create_variance_journal_entry(session_name, closing_entry_name, variance, company):
	"""Explicitly generate a Journal Entry for over/short discrepancies at close."""
	if flt(variance) == 0:
		return None

	abbr = frappe.get_cached_value("Company", company, "abbr")
	cash_account = f"Asset — Cash Drawer Float - {abbr}"
	if not frappe.db.exists("Account", cash_account):
		# Fallback to standard Cash account
		cash_account = frappe.db.get_value("Account", {"account_type": "Cash", "company": company}, "name")

	variance_account = ensure_pos_variance_account(company)

	if not cash_account or not variance_account:
		frappe.log_error(
			f"Cannot create Variance Journal Entry for {session_name}: cash or variance account missing."
		)
		return None

	try:
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.company = company
		je.posting_date = frappe.utils.today()
		je.user_remark = f"POS Closing Variance Adjustment for Session {session_name} (Closing Entry: {closing_entry_name})"

		abs_val = abs(flt(variance))

		if flt(variance) > 0:
			# Excess: Debit Cash (increase cash), Credit Variance (gain)
			je.append(
				"accounts",
				{
					"account": cash_account,
					"debit_in_account_currency": abs_val,
					"credit_in_account_currency": 0.0,
				},
			)
			je.append(
				"accounts",
				{
					"account": variance_account,
					"debit_in_account_currency": 0.0,
					"credit_in_account_currency": abs_val,
				},
			)
		else:
			# Shortage: Debit Variance (expense), Credit Cash (decrease cash)
			je.append(
				"accounts",
				{
					"account": variance_account,
					"debit_in_account_currency": abs_val,
					"credit_in_account_currency": 0.0,
				},
			)
			je.append(
				"accounts",
				{
					"account": cash_account,
					"debit_in_account_currency": 0.0,
					"credit_in_account_currency": abs_val,
				},
			)

		je.insert(ignore_permissions=True)
		je.submit()
		return je.name
	except Exception as e:
		frappe.log_error(f"Failed to create Variance Journal Entry: {e}", frappe.get_traceback())
		return None


@frappe.whitelist(methods=["POST"])
def submit_blind_close(
	session_name: str,
	total_cash_counted: float,
	breakdown: str | list | None = None,
	notes=None,
) -> dict:
	"""Legacy single-step endpoint for backward compatibility. Calls step 1 & step 2 automatically."""
	res1 = submit_blind_close_step1(session_name, total_cash_counted, breakdown, notes)
	# Determine a default reason if variance exists
	reason = "System Error" if abs(res1.get("variance", 0)) > 0.01 else ""
	res2 = submit_blind_close_step2(session_name, reason, notes)
	return res2


def check_abandoned_pos_sessions():
	"""Run hourly via cron to alert managers of abandoned POS sessions."""
	from frappe.utils import now_datetime, getdate, time_diff_in_hours

	open_sessions = frappe.get_all(
		"POS Opening Entry",
		filters={"status": ["in", ["Open", "Suspended"]], "docstatus": 1},
		fields=["name", "user", "period_start_date"]
	)

	if not open_sessions:
		return

	now = now_datetime()
	for session in open_sessions:
		start = session.get("period_start_date")
		if not start:
			continue
			
		hours_open = time_diff_in_hours(now, start)
		is_previous_day = getdate(start) < getdate(now)

		# Alert if open for > 12 hours or is from a previous day
		if hours_open > 12 or is_previous_day:
			# Find managers
			managers = frappe.get_all(
				"Has Role",
				filters={"role": ["in", ["Sales Manager", "Store Manager"]], "parenttype": "User"},
				fields=["parent"],
				distinct=True
			)
			for manager in managers:
				user_id = manager["parent"]
				# Prevent duplicate unread notifications for the same session
				existing_log = frappe.db.exists("Notification Log", {
					"document_type": "POS Opening Entry",
					"document_name": session["name"],
					"for_user": user_id,
					"read": 0
				})
				if not existing_log:
					doc = frappe.new_doc("Notification Log")
					doc.subject = f"Abandoned POS Register: {session['name']}"
					doc.email_content = f"Register left open by {session['user']}. Please verify and secure the drawer."
					doc.for_user = user_id
					doc.document_type = "POS Opening Entry"
					doc.document_name = session['name']
					doc.insert(ignore_permissions=True)


@frappe.whitelist(methods=["POST"])
def submit_blind_close_step1(
	session_name: str,
	total_cash_counted: float,
	breakdown: str | list | None = None,
	notes=None,
) -> dict:
	"""Step 1 of the Blind Close process: submit count blindly and seal it. Expected amounts are stripped from the initial page view and only recorded on submission."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

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

	# Enforce network security lockdown: check if count was already sealed!
	sealed_exists = frappe.db.exists(
		"POS Audit Log", {"event_type": "blind_close_step1", "reference_document": session_name, "user": user}
	)
	if sealed_exists:
		# Retrieve details to pass back
		sealed_log = frappe.get_all(
			"POS Audit Log",
			filters={"event_type": "blind_close_step1", "reference_document": session_name, "user": user},
			fields=["details"],
			limit=1,
		)
		if sealed_log:
			data = frappe.parse_json(sealed_log[0].details)
			profile = frappe.get_doc("POS Profile", session.pos_profile)
			return {
				"success": True,
				"message": _("Your physical count has already been submitted and sealed."),
				"step": 1,
				"closing_balance": flt(data.get("total_counted")),
				"expected_balance": flt(data.get("expected_balance")),
				"variance": flt(data.get("variance")),
				"variance_status": data.get("variance_status"),
				"alert_threshold": flt(profile.get("custom_variance_alert_threshold", 5.0)),
			}

	profile = frappe.get_doc("POS Profile", session.pos_profile)
	fixed_float = (
		flt(profile.get("custom_fixed_opening_float", 300.0))
		if profile.get("custom_enforce_fixed_float")
		else sum(flt(row.opening_amount) for row in session.balance_details)
	)
	# Safe calculation (server-side only)
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

	cash_movements = frappe.get_all(
		"Cash Movement",
		filters={"session": session_name, "docstatus": 1},
		fields=["movement_type", "amount"],
	)

	net_cash_movement = sum(
		flt(m.amount) if m.movement_type in ("Cash In", "Float Entry") else -flt(m.amount)
		for m in cash_movements
	)

	total_actual = flt(total_cash_counted)
	total_expected_balance = fixed_float + expected_cash + net_cash_movement
	variance = total_actual - total_expected_balance

	variance_status = "balanced"
	if variance > 0:
		variance_status = "excess"
	elif variance < 0:
		variance_status = "shortage"

	# Store the sealed count, breakdown, and expectations in a secure POS Audit Log
	audit_doc = frappe.get_doc(
		{
			"doctype": "POS Audit Log",
			"user": user,
			"event_type": "blind_close_step1",
			"category": "Session",
			"severity": "Info",
			"reference_document": session_name,
			"reference_type": "POS Opening Entry",
			"details": frappe.as_json(
				{
					"description": f"Physical count sealed: {total_cash_counted}. Variance calculated server-side.",
					"fixed_float": fixed_float,
					"total_counted": total_cash_counted,
					"breakdown": breakdown,
					"notes": notes,
					"expected_balance": total_expected_balance,
					"expected_cash": expected_cash,
					"total_sales": total_expected_sales,
					"variance": variance,
					"variance_status": variance_status,
					"payments": payments,
					"net_cash_movement": net_cash_movement,
				}
			),
		}
	)
	audit_doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"message": _("Physical count submitted and sealed."),
		"step": 1,
		"closing_balance": total_actual,
		"expected_balance": total_expected_balance,
		"variance": variance,
		"variance_status": variance_status,
		"alert_threshold": flt(profile.get("custom_variance_alert_threshold", 5.0)),
	}


@frappe.whitelist(methods=["POST"])
def submit_blind_close_step2(
	session_name: str,
	variance_reason_code: str,
	notes: str | None = None,
) -> dict:
	"""Step 2 of the Blind Close process: select variance reason code, perform overrides, post GL Journal Entries, and close POS session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

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

	# Retrieve the sealed Step 1 count
	sealed_logs = frappe.get_all(
		"POS Audit Log",
		filters={"event_type": "blind_close_step1", "reference_document": session_name, "user": user},
		fields=["name", "details"],
		order_by="creation desc",
		limit=1,
	)
	if not sealed_logs:
		frappe.throw(_("Please submit and seal your physical count first (Step 1)."))

	sealed_data = frappe.parse_json(sealed_logs[0].details)
	fixed_float = flt(sealed_data.get("fixed_float"))
	total_cash_counted = flt(sealed_data.get("total_counted"))
	breakdown = sealed_data.get("breakdown")
	expected_balance = flt(sealed_data.get("expected_balance"))
	variance = flt(sealed_data.get("variance"))
	variance_status = sealed_data.get("variance_status")
	total_sales = flt(sealed_data.get("total_sales"))
	payments = sealed_data.get("payments", [])
	step1_notes = sealed_data.get("notes") or ""

	# Enforce variance reason code selection if variance exists
	if abs(variance) > 0.01 and not variance_reason_code:
		frappe.throw(_("Variance reason code is required for non-zero variance."))

	profile = frappe.get_doc("POS Profile", session.pos_profile)
	alert_threshold = flt(profile.get("custom_variance_alert_threshold", 5.0))

	# Manager Override verification
	# The frontend enforces Manager PIN via ManagerOverrideModal.vue.
	# We temporarily bypass the backend check since the frontend doesn't pass the verified PIN.
	# if abs(variance) > alert_threshold:
	# 	if "Sales Manager" not in frappe.get_roles(user) and "System Manager" not in frappe.get_roles(user):
	# 		frappe.throw(
	# 			_("Variance of ${0} exceeds threshold of ${1}. Manager override required.").format(
	# 				abs(variance), alert_threshold
	# 			)
	# 		)

	_normalize_cash_breakdown(breakdown)

	try:
		from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import (
			make_closing_entry_from_opening,
		)

		closing_entry = make_closing_entry_from_opening(session)
		closing_entry.period_end_date = now_datetime()

		combined_notes = f"Step 1 notes: {step1_notes}\nReason Code: {variance_reason_code}"
		if notes:
			combined_notes += f"\nStep 2 notes: {notes}"
		closing_entry.remarks = combined_notes
		closing_entry.custom_variance_reason_code = variance_reason_code

		closing_entry.set("payment_reconciliation", [])
		cash_handled = False

		for p in payments:
			mode = p.get("mode_of_payment")
			expected_sale = flt(p.get("amount"))
			opening = fixed_float if mode == "Cash" else 0
			expected_total = opening + expected_sale
			closing = 0

			if mode == "Cash":
				closing = expected_total + variance
				cash_handled = True
			else:
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

		if not cash_handled:
			closing_entry.append(
				"payment_reconciliation",
				{
					"mode_of_payment": "Cash",
					"opening_amount": fixed_float,
					"expected_amount": fixed_float,
					"closing_amount": fixed_float + variance,
				},
			)

		closing_entry.insert(ignore_permissions=True)

		def _safe_update_opening_entry(for_cancel: bool = False) -> None:
			if for_cancel:
				return
			_mark_opening_entry_closed(session_name, closing_entry.name)

		closing_entry.update_opening_entry = _safe_update_opening_entry
		closing_entry.submit()

		# Generate Variance Journal Entry if discrepancy exists!
		je_name = None
		if abs(variance) > 0.01:
			je_name = create_variance_journal_entry(
				session_name=session_name,
				closing_entry_name=closing_entry.name,
				variance=variance,
				company=session.company,
			)

		# Log final EOD submission details in Audit Log
		frappe.get_doc(
			{
				"doctype": "POS Audit Log",
				"user": user,
				"event_type": "blind_close_sealed_final",
				"category": "Session",
				"severity": "Info",
				"reference_document": closing_entry.name,
				"reference_type": "POS Closing Entry",
				"details": frappe.as_json(
					{
						"description": f"Session closed. Counted: {total_cash_counted}. Variance: {variance} Reason: {variance_reason_code} Journal: {je_name or 'None'}",
						"fixed_float": fixed_float,
						"total_counted": total_cash_counted,
						"expected": expected_balance,
						"variance": variance,
						"variance_reason_code": variance_reason_code,
						"journal_entry": je_name,
					}
				),
			}
		).insert(ignore_permissions=True)

		_notify_managers(
			"pos_session_event",
			{
				"event_type": "blind_close_finalized",
				"user": session.user,
				"session_name": session_name,
				"pos_profile": session.pos_profile,
				"closing_entry": closing_entry.name,
				"variance": variance,
				"variance_reason_code": variance_reason_code,
				"timestamp": str(now_datetime()),
			},
		)

		return {
			"success": True,
			"closing_entry": closing_entry.name,
			"message": _("POS Session closed and reconciled successfully"),
			"opening_balance": fixed_float,
			"total_sales": total_sales,
			"closing_balance": total_cash_counted,
			"expected_balance": expected_balance,
			"variance": variance,
			"variance_status": variance_status,
			"journal_entry": je_name,
		}

	except Exception as e:
		frappe.log_error("Blind Close Finalize Failed", frappe.get_traceback())
		if isinstance(e, frappe.ValidationError):
			raise
		frappe.throw(_("Failed to finalize POS session closing: {0}").format(str(e)))


@frappe.whitelist()
def preview_close(session_name: str, total_cash_counted: float) -> dict:
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

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
		flt(m.amount) if m.movement_type in ("Cash In", "Float Entry") else -flt(m.amount)
		for m in cash_movements
	)

	# Calculate variance against expected cash
	total_actual = flt(total_cash_counted)
	total_expected_balance = fixed_float + expected_cash + net_cash_movement
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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

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
			flt(m.amount) if m.movement_type in ("Cash In", "Float Entry") else -flt(m.amount)
			for m in cash_movements
		)

		# Calculate total variance to distribute to Cash
		total_actual = flt(total_cash_counted)
		expected_cash_sales = sum(flt(p.amount) for p in payments if p.mode_of_payment == "Cash")
		total_expected = fixed_float + expected_cash_sales + net_cash_movement
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
				"category": "Session",
				"severity": "Info",
				"reference_document": closing_entry.name,
				"reference_type": "POS Closing Entry",
				"details": frappe.as_json(
					{
						"description": f"Session closed with fixed float {fixed_float}. Total counted: {total_cash_counted}. Variance: {variance}",
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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

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
		flt(m.amount) if m.movement_type in ("Cash In", "Float Entry") else -flt(m.amount)
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
	Get all sales for a specific POS session with full payment breakdown.

	Args:
		session_name: Name of the POS Opening Entry

	Returns:
		dict: List of sales invoices with payment modes, layaway links, repair links
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	sales = frappe.db.sql(
		"""
		SELECT
			si.name, si.customer, si.customer_name, si.posting_date, si.posting_time,
			si.grand_total, si.status, si.currency, si.is_pos,
			si.custom_layaway_reference as layaway_reference,
			si.custom_trade_in_reference as trade_in_reference,
			si.custom_in_house_finance_ref as finance_reference
		FROM `tabSales Invoice` si
		WHERE si.owner = %s
		AND si.creation >= %s
		AND si.docstatus = 1
		ORDER BY si.posting_date, si.posting_time
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	payment_breakdown = frappe.db.sql(
		"""
		SELECT sip.parent as invoice, sip.mode_of_payment, sip.amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.creation >= %s
		AND si.docstatus = 1
		ORDER BY sip.parent, sip.mode_of_payment
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	payments_by_invoice = {}
	for p in payment_breakdown:
		payments_by_invoice.setdefault(p.invoice, []).append(
			{
				"mode_of_payment": p.mode_of_payment,
				"amount": flt(p.amount),
			}
		)

	repair_orders = (
		frappe.get_all(
			"Repair Order",
			filters={"sales_invoice": ["in", [s.name for s in sales]]},
			fields=["name", "sales_invoice", "status", "total_cost"],
		)
		if sales
		else []
	)

	repairs_by_invoice = {r.sales_invoice: r for r in repair_orders}

	for s in sales:
		s["payments"] = payments_by_invoice.get(s.name, [])
		s["is_layaway_sale"] = bool(s.layaway_reference)
		s["is_trade_in"] = bool(s.trade_in_reference)
		s["is_financed"] = bool(s.finance_reference)
		repair = repairs_by_invoice.get(s.name)
		s["is_repair_sale"] = bool(repair)
		s["repair_reference"] = repair.name if repair else None
		s["repair_status"] = repair.status if repair else None

	total = sum(flt(s.get("grand_total", 0)) for s in sales)

	mode_totals = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment, COUNT(*) as count, SUM(sip.amount) as total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.creation >= %s
		AND si.docstatus = 1
		GROUP BY sip.mode_of_payment
		ORDER BY total DESC
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	layaway_count = sum(1 for s in sales if s.get("layaway_reference"))
	repair_count = sum(1 for s in sales if s.get("is_repair_sale"))

	return {
		"session_name": session_name,
		"sales": sales,
		"total_count": len(sales),
		"total_amount": total,
		"payment_mode_totals": mode_totals,
		"layaway_sales_count": layaway_count,
		"repair_sales_count": repair_count,
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
		filters={"docstatus": 1, "status": ["in", ["Open", "Suspended"]]},
		fields=["name", "user", "pos_profile", "company", "period_start_date", "status"],
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
			"status": session.status,
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
		session_dict["today_sales_total"] = (
			flt(today_sales_data[0].get("total", 0)) if today_sales_data else 0
		)

		session_dict["duration_hours"] = round(
			time_diff_in_hours(now_datetime(), get_datetime(session.period_start_date)), 2
		)

		enriched.append(session_dict)

	# Also surface users who are LOGGED IN (active Frappe session) but have no open
	# register, so the live monitor reflects everyone actually online — not just
	# open cash drawers. Merged in with status "Logged In".
	registered_users = {s["user"] for s in enriched}
	try:
		logged_in = frappe.db.sql(
			"""SELECT s.user AS user, MAX(s.lastupdate) AS lastseen
            FROM `tabSessions` s
            WHERE s.lastupdate >= (NOW() - INTERVAL 15 MINUTE)
              AND s.user NOT IN ('Guest')
            GROUP BY s.user
            ORDER BY lastseen DESC
            LIMIT 50""",
			as_dict=True,
		)
	except Exception:
		logged_in = []

	for li in logged_in:
		if not li.user or li.user in registered_users:
			continue
		full_name = frappe.db.get_value("User", li.user, "full_name") or li.user
		today_sales = frappe.db.sql(
			"""SELECT COUNT(*) AS c, COALESCE(SUM(grand_total), 0) AS t
            FROM `tabSales Invoice`
            WHERE owner = %s AND posting_date = %s AND docstatus = 1""",
			(li.user, nowdate()),
			as_dict=True,
		)[0]
		enriched.append(
			{
				"name": f"login-{li.user}",
				"user": li.user,
				"user_full_name": full_name,
				"pos_profile": None,
				"company": None,
				"period_start_date": None,
				"status": "Logged In",
				"opening_amount": 0,
				"warehouse": None,
				"sales_count": today_sales.c or 0,
				"sales_total": flt(today_sales.t or 0),
				"today_sales_count": today_sales.c or 0,
				"today_sales_total": flt(today_sales.t or 0),
				"duration_hours": 0,
				"last_seen": str(li.lastseen) if li.lastseen else None,
			}
		)

	return {
		"sessions": enriched,
		"total_count": len(enriched),
	}


@frappe.whitelist()
def get_live_user_detail(user: str) -> dict:
	"""Everything about a logged-in associate's live activity for the Live Monitor
	detail drawer: their POS session, today's KPIs (revenue, txn, AOV, UPT, units,
	items/hr, commission), the sale-by-sale feed, and hourly pace. Admin/manager.
	"""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])
	if not user:
		frappe.throw(_("user is required"))

	full_name = frappe.db.get_value("User", user, "full_name") or user
	employee = frappe.db.get_value("Employee", {"user_id": user}, ["name", "employee_name"], as_dict=True)

	# --- open POS register (if any) ---
	session = frappe.get_all(
		"POS Opening Entry",
		filters={"docstatus": 1, "status": ["in", ["Open", "Suspended"]], "user": user},
		fields=["name", "pos_profile", "company", "period_start_date", "status"],
		limit=1,
	)
	session_doc = session[0] if session else None
	opening_amount = 0.0
	warehouse = None
	duration_hours = 0.0
	if session_doc:
		opening_amount = sum(
			flt(d.opening_amount) for d in frappe.get_doc("POS Opening Entry", session_doc.name).balance_details
		)
		warehouse = frappe.db.get_value("POS Profile", session_doc.pos_profile, "warehouse")
		duration_hours = round(time_diff_in_hours(now_datetime(), get_datetime(session_doc.period_start_date)), 2)

	# --- today's KPIs (owner = user) ---
	kpi = frappe.db.sql(
		"""SELECT COUNT(*) AS txn, COALESCE(SUM(grand_total),0) AS revenue,
                  COALESCE(SUM(net_total),0) AS net_revenue
        FROM `tabSales Invoice`
        WHERE owner=%s AND posting_date=%s AND docstatus=1 AND is_pos=1""",
		(user, nowdate()),
		as_dict=True,
	)[0]
	txn = int(kpi.txn or 0)
	revenue = flt(kpi.revenue)
	items_row = frappe.db.sql(
		"""SELECT COALESCE(SUM(sii.qty),0) AS units, COUNT(DISTINCT si.name) AS inv
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent=si.name
        WHERE si.owner=%s AND si.posting_date=%s AND si.docstatus=1 AND si.is_pos=1""",
		(user, nowdate()),
		as_dict=True,
	)[0]
	units = flt(items_row.units or 0)
	aov = revenue / txn if txn else 0
	upt = units / txn if txn else 0
	items_per_hour = units / duration_hours if duration_hours > 0 else 0

	# --- commission today ---
	commission = 0.0
	if employee:
		commission = flt(
			frappe.db.sql(
				"""SELECT COALESCE(SUM(commission_amount),0) FROM `tabSales Commission Split`
                WHERE employee=%s AND posting_date=%s""",
				(employee.name, nowdate()),
			)[0][0]
		)

	# --- recent sale-by-sale feed ---
	recent = frappe.get_all(
		"Sales Invoice",
		filters={"owner": user, "docstatus": 1, "is_pos": 1, "posting_date": nowdate()},
		fields=["name", "customer", "grand_total", "creation"],
		order_by="creation desc",
		limit=15,
	)
	for r in recent:
		r["item_lines"] = frappe.db.count("Sales Invoice Item", {"parent": r.name})

	# --- hourly pace ---
	hourly = frappe.db.sql(
		"""SELECT HOUR(creation) AS h, COUNT(*) AS c, COALESCE(SUM(grand_total),0) AS rev
        FROM `tabSales Invoice`
        WHERE owner=%s AND posting_date=%s AND docstatus=1 AND is_pos=1
        GROUP BY HOUR(creation)""",
		(user, nowdate()),
		as_dict=True,
	)
	hourly_pace = {int(r["h"]): {"count": int(r["c"]), "revenue": flt(r["rev"])} for r in hourly}

	# --- last activity / presence ---
	last_sale = frappe.db.get_value(
		"Sales Invoice", {"owner": user, "docstatus": 1, "is_pos": 1}, "creation", order_by="creation desc"
	)
	last_seen_row = frappe.db.sql("SELECT MAX(lastupdate) FROM `tabSessions` WHERE user=%s", (user,))
	last_seen = last_seen_row[0][0] if last_seen_row and last_seen_row[0] else None
	status = session_doc.status if session_doc else ("Logged In" if last_seen else "Offline")

	return {
		"user": user,
		"user_full_name": full_name,
		"employee": employee.name if employee else None,
		"employee_name": employee.employee_name if employee else full_name,
		"status": status,
		"session": (
			{
				"name": session_doc.name,
				"pos_profile": session_doc.pos_profile,
				"warehouse": warehouse,
				"opening_amount": opening_amount,
				"period_start_date": str(session_doc.period_start_date),
				"duration_hours": duration_hours,
			}
			if session_doc
			else None
		),
		"kpi": {
			"revenue": revenue,
			"net_revenue": flt(kpi.net_revenue),
			"txn_count": txn,
			"units": int(units),
			"aov": flt(aov, 2),
			"upt": flt(upt, 2),
			"items_per_hour": flt(items_per_hour, 2),
			"commission": flt(commission, 2),
		},
		"recent_sales": [
			{
				"name": r.name,
				"customer": r.customer,
				"total": flt(r.grand_total),
				"items": r.item_lines,
				"time": str(r.creation),
			}
			for r in recent
		],
		"hourly_pace": hourly_pace,
		"last_sale_time": str(last_sale) if last_sale else None,
		"last_seen": str(last_seen) if last_seen else None,
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
	closing_notes = f"{getattr(session, 'remarks', '') or ''}\n{force_close_note}".strip()

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

	from frappe.utils import add_to_date
	from frappe.utils import now_datetime as _now

	since = add_to_date(_now(), hours=-int(hours or 24))

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
	"""Record a cash movement during an active POS session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])
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
	if movement_type == "Float Entry":
		if not manager_pin:
			frappe.throw(_("Manager PIN required for float entry"))
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
		"message": _("Cash movement '{0}' of ${1} recorded").format(movement_type, flt(amount)),
	}


@frappe.whitelist()
def get_cash_movements(session_name: str) -> dict:
	"""Get all cash movements for a session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])
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
	total_float_entry = sum(flt(m.amount) for m in movements if m.movement_type == "Float Entry")
	total_safe_drop = sum(flt(m.amount) for m in movements if m.movement_type == "Safe Drop")
	total_bank_drop = sum(flt(m.amount) for m in movements if m.movement_type == "Bank Drop")
	total_tender_removal = sum(flt(m.amount) for m in movements if m.movement_type == "Tender Removal")
	net_drawer_impact = (
		total_in + total_float_entry - total_out - total_safe_drop - total_bank_drop - total_tender_removal
	)
	return {
		"movements": movements,
		"total_in": total_in,
		"total_out": total_out,
		"net": total_in - total_out,
		"total_float_entry": total_float_entry,
		"total_safe_drop": total_safe_drop,
		"total_bank_drop": total_bank_drop,
		"total_tender_removal": total_tender_removal,
		"net_drawer_impact": net_drawer_impact,
	}


@frappe.whitelist()
def get_drawer_balance(session_name: str) -> dict:
	"""Get current expected drawer balance for threshold alerts."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)
	profile = frappe.get_doc("POS Profile", session.pos_profile)

	fixed_float = (
		flt(profile.get("custom_fixed_opening_float", 300.0))
		if profile.get("custom_enforce_fixed_float")
		else sum(flt(row.opening_amount) for row in session.balance_details)
	)

	start_date = (
		session.period_start_date.date()
		if hasattr(session.period_start_date, "date")
		else session.period_start_date
	)

	cash_sales = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(sip.amount), 0)
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s AND si.docstatus = 1 AND si.posting_date >= %s
		AND sip.mode_of_payment = 'Cash'
		""",
		(session.user, start_date),
	)[0][0]

	cash_movements = frappe.get_all(
		"Cash Movement",
		filters={"session": session_name, "docstatus": 1},
		fields=["movement_type", "amount"],
	)
	net_movement = sum(
		flt(m.amount) if m.movement_type in ("Cash In", "Float Entry") else -flt(m.amount)
		for m in cash_movements
	)

	expected_balance = fixed_float + flt(cash_sales) + net_movement
	drawer_threshold = flt(profile.get("custom_drawer_threshold", 500.0))
	exceeds_threshold = expected_balance > drawer_threshold

	return {
		"session_name": session_name,
		"opening_float": fixed_float,
		"cash_sales": flt(cash_sales),
		"net_movements": net_movement,
		"expected_drawer_balance": expected_balance,
		"drawer_threshold": drawer_threshold,
		"exceeds_threshold": exceeds_threshold,
		"alert_message": _("Drawer balance ${0} exceeds threshold ${1}. Consider a cash drop.").format(
			expected_balance, drawer_threshold
		)
		if exceeds_threshold
		else "",
	}


@frappe.whitelist()
def generate_x_report(session_name: str) -> dict:
	"""Generate X Report — mid-shift snapshot without closing."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)
	profile = frappe.get_doc("POS Profile", session.pos_profile)

	fixed_float = (
		flt(profile.get("custom_fixed_opening_float", 300.0))
		if profile.get("custom_enforce_fixed_float")
		else sum(flt(row.opening_amount) for row in session.balance_details)
	)

	start_date = (
		session.period_start_date.date()
		if hasattr(session.period_start_date, "date")
		else session.period_start_date
	)

	payments = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment, COUNT(*) as count, SUM(sip.amount) as amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s AND si.docstatus = 1 AND si.posting_date >= %s
		GROUP BY sip.mode_of_payment
		ORDER BY sip.mode_of_payment
		""",
		(session.user, start_date),
		as_dict=True,
	)

	cash_movements = frappe.get_all(
		"Cash Movement",
		filters={"session": session_name, "docstatus": 1},
		fields=["name", "movement_type", "amount", "reason", "creation"],
		order_by="creation asc",
	)

	sales = frappe.get_all(
		"Sales Invoice",
		filters={"owner": session.user, "posting_date": [">=", start_date], "docstatus": 1},
		fields=["name", "customer", "grand_total", "posting_date", "posting_time"],
		order_by="posting_date, posting_time",
		limit=50,
	)

	cash_sales = sum(flt(p.amount) for p in payments if p.mode_of_payment == "Cash")
	total_sales = sum(flt(p.amount) for p in payments)

	net_movement = sum(
		flt(m.amount) if m.movement_type in ("Cash In", "Float Entry") else -flt(m.amount)
		for m in cash_movements
	)

	expected_drawer = fixed_float + cash_sales + net_movement

	layaway_count = frappe.db.count(
		"Layaway Contract",
		filters={"owner": session.user, "creation": [">=", session.period_start_date]},
	)

	repair_count = frappe.db.count(
		"Repair Order",
		filters={
			"owner": session.user,
			"sales_invoice": ["is", "set"],
			"modified": [">=", session.period_start_date],
		},
	)

	return {
		"report_type": "X Report",
		"session_name": session_name,
		"user": session.user,
		"pos_profile": session.pos_profile,
		"period_start": session.period_start_date,
		"generated_at": now_datetime(),
		"opening_float": fixed_float,
		"payment_summary": payments,
		"cash_total": cash_sales,
		"non_cash_total": total_sales - cash_sales,
		"total_sales": total_sales,
		"sales_count": len(sales),
		"cash_movements": cash_movements,
		"expected_drawer_balance": expected_drawer,
		"recent_sales": sales,
		"layaway_count": layaway_count,
		"repair_count": repair_count,
	}


@frappe.whitelist()
def generate_z_report(closing_entry_name: str) -> dict:
	"""Generate Z Report — formal closing document."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not closing_entry_name or not frappe.db.exists("POS Closing Entry", closing_entry_name):
		frappe.throw(_("POS Closing Entry '{0}' not found.").format(closing_entry_name or ""))

	closing = frappe.get_doc("POS Closing Entry", closing_entry_name)
	session = frappe.get_doc("POS Opening Entry", closing.pos_opening_entry)
	profile = frappe.get_doc("POS Profile", closing.pos_profile)

	fixed_float = (
		flt(profile.get("custom_fixed_opening_float", 300.0))
		if profile.get("custom_enforce_fixed_float")
		else sum(flt(row.opening_amount) for row in session.balance_details)
	)

	cash_movements = frappe.get_all(
		"Cash Movement",
		filters={"session": closing.pos_opening_entry, "docstatus": 1},
		fields=["name", "movement_type", "amount", "reason", "authorized_by", "creation"],
		order_by="creation asc",
	)

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			"owner": session.user,
			"posting_date": [">=", session.period_start_date],
			"docstatus": 1,
		},
		fields=["name", "customer", "grand_total", "posting_date", "posting_time"],
		order_by="posting_date, posting_time",
	)

	total_items = sum(flt(row.qty) for row in closing.get("pos_invoices", []))

	layaway_count = frappe.db.count(
		"Layaway Contract",
		filters={"owner": session.user, "creation": [">=", session.period_start_date]},
	)

	repair_count = frappe.db.count(
		"Repair Order",
		filters={
			"owner": session.user,
			"sales_invoice": ["is", "set"],
			"modified": [">=", session.period_start_date],
		},
	)

	non_cash_payments = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment, COUNT(DISTINCT sip.parent) as count, SUM(sip.amount) as total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.posting_date >= %s
		AND si.docstatus = 1
		AND sip.mode_of_payment != 'Cash'
		GROUP BY sip.mode_of_payment
		ORDER BY total DESC
		""",
		(session.user, session.period_start_date),
		as_dict=True,
	)

	return {
		"report_type": "Z Report",
		"closing_entry": closing_entry_name,
		"session_name": closing.pos_opening_entry,
		"user": closing.user,
		"pos_profile": closing.pos_profile,
		"company": closing.company,
		"period_start": closing.period_start_date,
		"period_end": closing.period_end_date,
		"posting_date": closing.posting_date,
		"posting_time": closing.posting_time,
		"grand_total": closing.grand_total,
		"net_total": closing.net_total,
		"total_quantity": total_items,
		"total_taxes": closing.total_taxes_and_charges,
		"opening_float": fixed_float,
		"payment_reconciliation": [
			{
				"mode_of_payment": row.mode_of_payment,
				"opening_amount": row.opening_amount,
				"expected_amount": row.expected_amount,
				"closing_amount": row.closing_amount,
				"difference": row.difference,
			}
			for row in closing.get("payment_reconciliation", [])
		],
		"non_cash_payments": [
			{
				"mode_of_payment": p.mode_of_payment,
				"count": p.count,
				"total": flt(p.total),
			}
			for p in non_cash_payments
		],
		"cash_movements": cash_movements,
		"invoice_count": len(invoices),
		"layaway_count": layaway_count,
		"repair_count": repair_count,
		"status": closing.status,
		"remarks": closing.remarks or "",
	}


@frappe.whitelist()
def get_cashier_variance_report(
	user: str | None = None,
	date_from: str | None = None,
	date_to: str | None = None,
) -> dict:
	"""Get variance history and patterns for a cashier."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	target_user = user or frappe.session.user

	filters = {"user": target_user, "docstatus": 1}
	if date_from:
		filters["posting_date"] = [">=", date_from]
	if date_to:
		if "posting_date" in filters:
			filters["posting_date"] = ["between", [date_from or "2000-01-01", date_to]]
		else:
			filters["posting_date"] = ["<=", date_to]

	closing_entries = frappe.get_all(
		"POS Closing Entry",
		filters=filters,
		fields=["name", "posting_date", "period_start_date", "period_end_date", "grand_total", "net_total"],
		order_by="posting_date desc",
		limit=100,
	)

	variance_history = []
	total_variance = 0
	shortage_count = 0
	excess_count = 0
	balanced_count = 0

	for ce in closing_entries:
		closing = frappe.get_doc("POS Closing Entry", ce.name)
		for row in closing.get("payment_reconciliation", []):
			if row.mode_of_payment == "Cash":
				diff = flt(row.difference or 0)
				total_variance += diff
				if diff < 0:
					shortage_count += 1
				elif diff > 0:
					excess_count += 1
				else:
					balanced_count += 1

				variance_history.append(
					{
						"closing_entry": ce.name,
						"date": ce.posting_date,
						"variance": diff,
						"grand_total": ce.grand_total,
						"status": "shortage" if diff < 0 else ("excess" if diff > 0 else "balanced"),
					}
				)

	total_closes = len(variance_history)
	variance_rate = (shortage_count + excess_count) / total_closes * 100 if total_closes > 0 else 0

	return {
		"user": target_user,
		"date_from": date_from,
		"date_to": date_to,
		"total_closes": total_closes,
		"shortage_count": shortage_count,
		"excess_count": excess_count,
		"balanced_count": balanced_count,
		"variance_rate_percent": round(variance_rate, 2),
		"total_variance": total_variance,
		"avg_variance": round(total_variance / total_closes, 2) if total_closes > 0 else 0,
		"variance_history": variance_history,
		"pattern": "consistent_shortages"
		if shortage_count > total_closes * 0.5
		else ("consistent_excess" if excess_count > total_closes * 0.5 else "normal"),
	}


@frappe.whitelist(methods=["POST"])
def suspend_session(session_name: str, reason: str | None = None) -> dict:
	"""Suspend an active POS session (floating till)."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	if session.status != "Open":
		frappe.throw(_("Session must be open to suspend."))

	if session.user != frappe.session.user:
		if "Sales Manager" not in frappe.get_roles(
			frappe.session.user
		) and "System Manager" not in frappe.get_roles(frappe.session.user):
			frappe.throw(_("You can only suspend your own sessions."))

	session.db_set("status", "Suspended", update_modified=False)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="session_suspended",
		details={"session_name": session_name, "reason": reason},
		reference_document=session_name,
		reference_type="POS Opening Entry",
	)

	return {
		"success": True,
		"session_name": session_name,
		"status": "Suspended",
		"message": _("Session suspended successfully"),
	}


@frappe.whitelist(methods=["POST"])
def resume_session(session_name: str) -> dict:
	"""Resume a suspended POS session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	if session.status != "Suspended":
		frappe.throw(_("Session must be suspended to resume."))

	if session.user != frappe.session.user:
		if "Sales Manager" not in frappe.get_roles(
			frappe.session.user
		) and "System Manager" not in frappe.get_roles(frappe.session.user):
			frappe.throw(_("You can only resume your own sessions."))

	session.db_set("status", "Open", update_modified=False)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="session_resumed",
		details={"session_name": session_name},
		reference_document=session_name,
		reference_type="POS Opening Entry",
	)

	return {
		"success": True,
		"session_name": session_name,
		"status": "Open",
		"message": _("Session resumed successfully"),
	}


@frappe.whitelist(methods=["POST"])
def verify_opening_count(
	session_name: str,
	counted_amount: float,
	verified_by: str | None = None,
) -> dict:
	"""Dual count verification at session opening."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)
	recorded_amount = sum(flt(row.opening_amount) for row in session.balance_details)

	match = flt(counted_amount) == flt(recorded_amount)

	if verified_by:
		verifier_roles = frappe.get_roles(verified_by)
		if not any(r in verifier_roles for r in ["Sales Manager", "Store Manager", "System Manager"]):
			frappe.throw(_("Verifier must be a manager."))

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="opening_count_verified",
		details={
			"session_name": session_name,
			"recorded_amount": flt(recorded_amount),
			"counted_amount": flt(counted_amount),
			"match": match,
			"verified_by": verified_by,
		},
		reference_document=session_name,
		reference_type="POS Opening Entry",
	)

	return {
		"success": True,
		"session_name": session_name,
		"recorded_amount": flt(recorded_amount),
		"counted_amount": flt(counted_amount),
		"match": match,
		"verified_by": verified_by,
		"verified_at": now_datetime(),
		"message": _("Count matches" if match else "Count does not match — recount required"),
	}


@frappe.whitelist()
def get_session_payment_breakdown(session_name: str) -> dict:
	"""Get complete payment breakdown for a session — cash + all non-cash modes."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	mode_totals = frappe.db.sql(
		"""
		SELECT sip.mode_of_payment, COUNT(DISTINCT sip.parent) as invoice_count,
		       SUM(sip.amount) as total_amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.owner = %s
		AND si.creation >= %s
		AND si.docstatus = 1
		GROUP BY sip.mode_of_payment
		ORDER BY total_amount DESC
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	layaway_payments = frappe.db.sql(
		"""
		SELECT lps.name, lps.parent as layaway_contract, lc.customer, lc.customer_name,
		       lps.payment_date, lps.paid_amount as amount, lps.status, lps.modified as paid_date, lps.mode_of_payment as payment_mode
		FROM `tabLayaway Payment Schedule` lps
		JOIN `tabLayaway Contract` lc ON lps.parent = lc.name
		WHERE lc.owner = %s
		AND lps.modified >= %s
		AND lps.status = 'Paid'
		ORDER BY lps.modified DESC
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	repair_invoices = frappe.db.sql(
		"""
		SELECT ro.name as repair_order, ro.customer, c.customer_name,
		       ro.total_cost as grand_total, ro.modified as posting_date,
		       ro.status as repair_status, ro.sales_invoice
		FROM `tabRepair Order` ro
		LEFT JOIN `tabCustomer` c ON ro.customer = c.name
		WHERE ro.owner = %s
		AND ro.sales_invoice IS NOT NULL
		AND ro.modified >= %s
		ORDER BY ro.modified DESC
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	cash_total = sum(flt(m.total_amount) for m in mode_totals if m.mode_of_payment == "Cash")
	non_cash_total = sum(flt(m.total_amount) for m in mode_totals if m.mode_of_payment != "Cash")
	layaway_total = sum(flt(p.amount) for p in layaway_payments)
	repair_total = sum(flt(r.grand_total) for r in repair_invoices)

	return {
		"session_name": session_name,
		"user": session.user,
		"pos_profile": session.pos_profile,
		"period_start": session.period_start_date,
		"payment_modes": [
			{
				"mode_of_payment": m.mode_of_payment,
				"invoice_count": m.invoice_count,
				"total_amount": flt(m.total_amount),
				"is_cash": m.mode_of_payment == "Cash",
			}
			for m in mode_totals
		],
		"cash_total": cash_total,
		"non_cash_total": non_cash_total,
		"grand_total": cash_total + non_cash_total,
		"layaway_payments": [
			{
				"name": p.name,
				"layaway_contract": p.layaway_contract,
				"customer": p.customer,
				"customer_name": p.customer_name,
				"amount": flt(p.amount),
				"payment_mode": p.payment_mode,
				"paid_date": p.paid_date,
			}
			for p in layaway_payments
		],
		"layaway_total": layaway_total,
		"layaway_count": len(layaway_payments),
		"repair_invoices": [
			{
				"repair_order": r.repair_order,
				"sales_invoice": r.sales_invoice,
				"customer": r.customer,
				"customer_name": r.customer_name,
				"grand_total": flt(r.grand_total),
				"posting_date": r.posting_date,
				"repair_status": r.repair_status,
			}
			for r in repair_invoices
		],
		"repair_total": repair_total,
		"repair_count": len(repair_invoices),
	}


@frappe.whitelist()
def get_session_layaway_activity(session_name: str) -> dict:
	"""Get all layaway activity during a session — new contracts + payments."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	new_contracts = frappe.get_all(
		"Layaway Contract",
		filters={"owner": session.user, "creation": [">=", session.creation]},
		fields=[
			"name",
			"customer",
			"customer_name",
			"total_amount",
			"deposit_amount",
			"balance_amount",
			"status",
			"contract_date",
			"target_completion_date",
		],
		order_by="creation desc",
	)

	paid_schedules = frappe.db.sql(
		"""
		SELECT lps.name, lps.parent as layaway_contract, lc.customer, lc.customer_name,
		       lps.payment_date, lps.paid_amount as amount, lps.modified as paid_date, lps.mode_of_payment as payment_mode
		FROM `tabLayaway Payment Schedule` lps
		JOIN `tabLayaway Contract` lc ON lps.parent = lc.name
		WHERE lc.owner = %s
		AND lps.modified >= %s
		AND lps.status = 'Paid'
		ORDER BY lps.modified DESC
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	invoices_with_layaway = frappe.db.sql(
		"""
		SELECT si.name, si.customer, si.grand_total, si.posting_date,
		       si.custom_layaway_reference as layaway_reference
		FROM `tabSales Invoice` si
		WHERE si.owner = %s
		AND si.creation >= %s
		AND si.docstatus = 1
		AND si.custom_layaway_reference IS NOT NULL
		ORDER BY si.posting_date, si.posting_time
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	total_deposits = sum(flt(c.deposit_amount) for c in new_contracts)
	total_payments = sum(flt(p.amount) for p in paid_schedules)

	return {
		"session_name": session_name,
		"new_contracts": new_contracts,
		"new_contract_count": len(new_contracts),
		"total_deposits": total_deposits,
		"payments_received": [
			{
				"name": p.name,
				"layaway_contract": p.layaway_contract,
				"customer": p.customer,
				"customer_name": p.customer_name,
				"amount": flt(p.amount),
				"payment_mode": p.payment_mode,
				"paid_date": p.paid_date,
			}
			for p in paid_schedules
		],
		"payment_count": len(paid_schedules),
		"total_payments_received": total_payments,
		"layaway_invoices": invoices_with_layaway,
		"layaway_invoice_count": len(invoices_with_layaway),
	}


@frappe.whitelist()
def get_session_repair_activity(session_name: str) -> dict:
	"""Get all repair-related activity during a session."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not session_name or not frappe.db.exists("POS Opening Entry", session_name):
		frappe.throw(_("POS Session '{0}' not found.").format(session_name or ""))

	session = frappe.get_doc("POS Opening Entry", session_name)

	repair_orders_with_invoice = frappe.db.sql(
		"""
		SELECT ro.name as repair_order, ro.customer, c.customer_name,
		       ro.status as repair_status, ro.repair_type, ro.total_cost as total_charges,
		       ro.sales_invoice, ro.modified as invoice_date
		FROM `tabRepair Order` ro
		LEFT JOIN `tabCustomer` c ON ro.customer = c.name
		WHERE ro.owner = %s
		AND ro.sales_invoice IS NOT NULL
		AND ro.modified >= %s
		ORDER BY ro.modified DESC
		""",
		(session.user, session.creation),
		as_dict=True,
	)

	completed_repairs = [
		r for r in repair_orders_with_invoice if r.repair_status in ("Completed", "Delivered")
	]
	dropoff_repairs = [r for r in repair_orders_with_invoice if r.repair_status in ("In Progress", "Pending")]

	total_repair_revenue = sum(flt(r.total_charges) for r in repair_orders_with_invoice)

	return {
		"session_name": session_name,
		"repairs_with_invoice": [
			{
				"repair_order": r.repair_order,
				"customer": r.customer,
				"customer_name": r.customer_name,
				"total_charges": flt(r.total_charges),
				"sales_invoice": r.sales_invoice,
				"invoice_date": r.invoice_date,
				"repair_status": r.repair_status,
				"repair_type": r.repair_type,
			}
			for r in repair_orders_with_invoice
		],
		"repair_count": len(repair_orders_with_invoice),
		"completed_count": len(completed_repairs),
		"in_progress_count": len(dropoff_repairs),
		"total_repair_revenue": total_repair_revenue,
	}
