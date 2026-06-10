"""
Dunning, Write-offs, and Customer Statements API

Provides:
- Automated dunning level determination
- Dunning letter creation and sending
- Write-off request and approval workflow
- Customer statement generation (PDF-ready)
- Batch dunning for overdue accounts
"""

import frappe
from frappe import _
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, now, today

# ── Dunning ────────────────────────────────────────────────


@frappe.whitelist(methods=["GET"])
def get_overdue_accounts(min_days: int = 30) -> list:
	"""Return finance accounts with overdue balances."""
	frappe.only_for(["Sales Manager", "Accounts Manager", "System Manager"])

	min_days = int(min_days)
	today_date = getdate(today())

	accounts = frappe.get_all(
		"In-House Finance Account",
		filters={"status": ["in", ["Active", "Collections"]], "current_balance": [">", 0]},
		fields=["name", "customer", "current_balance", "interest_rate", "status"],
	)

	result = []
	for acct in accounts:
		customer_name = frappe.db.get_value("Customer", acct.customer, "customer_name") or ""
		email = frappe.db.get_value("Customer", acct.customer, "email_id") or ""

		entries = frappe.get_all(
			"Customer Ledger Entry",
			filters={"parent": acct.name, "parenttype": "In-House Finance Account"},
			fields=["entry_date", "entry_type", "debit", "credit"],
			order_by="entry_date asc",
		)

		overdue = 0.0
		oldest_overdue = None
		last_payment = None

		for entry in entries:
			if flt(entry.debit) > 0:
				days = (today_date - getdate(entry.entry_date)).days
				if days > min_days:
					overdue += flt(entry.debit)
					if oldest_overdue is None:
						oldest_overdue = entry.entry_date
			if entry.entry_type == "Payment" and flt(entry.credit) > 0:
				last_payment = entry.entry_date

		if overdue > 0:
			overdue_days = (today_date - getdate(oldest_overdue)).days if oldest_overdue else 0
			level = _determine_dunning_level(overdue_days)
			result.append(
				{
					"account": acct.name,
					"customer": acct.customer,
					"customer_name": customer_name,
					"email": email,
					"total_balance": flt(acct.current_balance),
					"overdue_amount": flt(overdue),
					"overdue_days": overdue_days,
					"suggested_level": level,
					"last_payment": str(last_payment) if last_payment else None,
					"status": acct.status,
				}
			)

	return sorted(result, key=lambda x: x["overdue_days"], reverse=True)


def _determine_dunning_level(days: int) -> str:
	if days >= 90:
		return "Level 3 - Collections Notice"
	elif days >= 60:
		return "Level 2 - Final Notice"
	return "Level 1 - Reminder"


@frappe.whitelist(methods=["POST"])
def create_dunning_letter(finance_account: str, dunning_level: str | None = None) -> dict:
	"""Create a dunning letter for an overdue account."""
	frappe.only_for(["Sales Manager", "Accounts Manager", "System Manager"])

	if not frappe.db.exists("In-House Finance Account", finance_account):
		frappe.throw(_("Finance Account '{0}' not found.").format(finance_account))

	acct = frappe.get_doc("In-House Finance Account", finance_account)
	customer_name = frappe.db.get_value("Customer", acct.customer, "customer_name") or ""
	email = frappe.db.get_value("Customer", acct.customer, "email_id") or ""

	today_date = getdate(today())
	overdue = 0.0
	oldest_overdue = None
	for entry in acct.ledger_entries or []:
		if flt(entry.debit) > 0:
			days = (today_date - getdate(entry.entry_date)).days
			if days > 30:
				overdue += flt(entry.debit)
				if oldest_overdue is None:
					oldest_overdue = entry.entry_date

	overdue_days = (today_date - getdate(oldest_overdue)).days if oldest_overdue else 0
	level = dunning_level or _determine_dunning_level(overdue_days)

	subject, body = _get_dunning_template(
		level,
		{
			"customer_name": customer_name,
			"account_id": finance_account,
			"overdue_amount": flt(overdue),
			"total_balance": flt(acct.current_balance),
			"minimum_due": flt(acct.current_balance) * flt(acct.minimum_payment_percent) / 100,
			"overdue_days": overdue_days,
			"store_name": frappe.db.get_single_value("Selling Settings", "company") or "Zevar Jewelry",
		},
	)

	letter = frappe.get_doc(
		{
			"doctype": "Dunning Letter",
			"finance_account": finance_account,
			"customer": acct.customer,
			"customer_name": customer_name,
			"dunning_level": level,
			"status": "Draft",
			"overdue_days": overdue_days,
			"overdue_amount": flt(overdue),
			"total_balance": flt(acct.current_balance),
			"minimum_due": flt(acct.current_balance) * flt(acct.minimum_payment_percent) / 100,
			"interest_rate": flt(acct.interest_rate),
			"subject": subject,
			"message_body": body,
		}
	)
	letter.insert(ignore_permissions=True)

	return {
		"success": True,
		"letter_id": letter.name,
		"level": level,
		"email": email,
	}


def _get_dunning_template(level: str, ctx: dict) -> tuple:
	template_map = {
		"Level 1": "Dunning Level 1 Reminder",
		"Level 2": "Dunning Level 2 Final Notice",
		"Level 3": "Dunning Level 3 Collections",
	}
	template_name = None
	for key, name in template_map.items():
		if key in level:
			template_name = name
			break

	if template_name and frappe.db.exists("Email Template", template_name):
		from frappe.email.doctype.email_template.email_template import get_email_template

		ctx["company"] = ctx.get("store_name", "Zevar Jewelry")
		try:
			subject, body = get_email_template(template_name, ctx)
			return subject, body
		except Exception:
			pass

	# Fallback to hardcoded if template not installed
	if "Level 3" in level:
		subject = f"COLLECTIONS NOTICE - Account {ctx['account_id']}"
		body = (
			f"<p>Dear {ctx['customer_name']},</p>"
			f"<p>This is our <strong>final notice</strong> regarding your overdue balance of "
			f"<strong>${ctx['overdue_amount']:,.2f}</strong> on account <strong>{ctx['account_id']}</strong>.</p>"
			f"<p>Your account is now <strong>{ctx['overdue_days']} days overdue</strong>.</p>"
			f"<p>Total outstanding balance: <strong>${ctx['total_balance']:,.2f}</strong></p>"
			f"<p>Please contact us immediately at our store to arrange payment.</p>"
			f"<p>Sincerely,<br>{ctx['store_name']}</p>"
		)
	elif "Level 2" in level:
		subject = f"FINAL NOTICE - Account {ctx['account_id']} Payment Overdue"
		body = (
			f"<p>Dear {ctx['customer_name']},</p>"
			f"<p>Account <strong>{ctx['account_id']}</strong> has an overdue balance "
			f"of <strong>${ctx['overdue_amount']:,.2f}</strong> (<strong>{ctx['overdue_days']} days past due</strong>).</p>"
			f"<p>Total balance: <strong>${ctx['total_balance']:,.2f}</strong></p>"
			f"<p>Minimum payment due: <strong>${ctx['minimum_due']:,.2f}</strong></p>"
			f"<p>This is your <strong>final notice</strong>. Please make a payment or contact us within 15 days.</p>"
			f"<p>Sincerely,<br>{ctx['store_name']}</p>"
		)
	else:
		subject = f"Friendly Reminder - Account {ctx['account_id']} Payment Due"
		body = (
			f"<p>Dear {ctx['customer_name']},</p>"
			f"<p>This is a friendly reminder that your account "
			f"<strong>{ctx['account_id']}</strong> has a balance of <strong>${ctx['total_balance']:,.2f}</strong>.</p>"
			f"<p>Minimum payment due: <strong>${ctx['minimum_due']:,.2f}</strong></p>"
			f"<p>You can make a payment at our store or contact us to arrange a payment schedule.</p>"
			f"<p>Thank you for being a valued customer.<br>{ctx['store_name']}</p>"
		)

	return subject, body


@frappe.whitelist(methods=["POST"])
def send_dunning_letter(letter_id: str) -> dict:
	"""Submit (send) a draft dunning letter."""
	frappe.only_for(["Sales Manager", "Accounts Manager", "System Manager"])

	letter = frappe.get_doc("Dunning Letter", letter_id)
	if letter.status != "Draft":
		frappe.throw(_("Only draft letters can be sent."))

	letter.submit()
	return {"success": True, "status": letter.status}


# ── Batch Dunning (Scheduled) ──────────────────────────────


def run_auto_dunning():
	"""
	Scheduled Job: automatically create dunning letters for overdue accounts.
	Only creates letters if one hasn't been sent in the last 30 days for the same level.
	"""
	overdue = get_overdue_accounts(min_days=30)

	for acct in overdue:
		existing = frappe.get_all(
			"Dunning Letter",
			filters={
				"finance_account": acct["account"],
				"dunning_level": acct["suggested_level"],
				"sent_date": [">=", add_months(today(), -1)],
			},
			limit=1,
		)
		if not existing:
			try:
				create_dunning_letter(acct["account"], acct["suggested_level"])
			except Exception:
				frappe.log_error(f"Auto Dunning Error: {acct['account']}", frappe.get_traceback())


# ── Customer Statements ────────────────────────────────────


@frappe.whitelist(methods=["GET"])
def generate_customer_statement(account_id: str, month: int | None = None, year: int | None = None) -> dict:
	"""Generate a detailed customer statement for a given period."""
	frappe.only_for(["Sales User", "Sales Manager", "Accounts Manager", "System Manager"])

	if not frappe.db.exists("In-House Finance Account", account_id):
		frappe.throw(_("Finance Account '{0}' not found.").format(account_id))

	acct = frappe.get_doc("In-House Finance Account", account_id)
	customer = frappe.get_doc("Customer", acct.customer)
	customer_name = customer.customer_name
	email = customer.email_id or ""

	from frappe.utils import getdate

	today_date = getdate(today())

	if month is not None:
		month = int(month)
	if year is not None:
		year = int(year)

	if month and year:
		stmt_date = getdate(f"{year}-{month:02d}-01")
	else:
		stmt_date = add_months(today_date, -1)
		month = stmt_date.month
		year = stmt_date.year

	period_start = get_first_day(stmt_date)
	period_end = get_last_day(stmt_date)

	entries = []
	opening_balance = 0.0
	total_debits = 0.0
	total_credits = 0.0

	for row in acct.ledger_entries or []:
		entry_date = getdate(row.entry_date)

		if entry_date < period_start:
			opening_balance += flt(row.debit) - flt(row.credit)
		elif entry_date >= period_start and entry_date <= period_end:
			total_debits += flt(row.debit)
			total_credits += flt(row.credit)
			entries.append(
				{
					"date": str(row.entry_date),
					"type": row.entry_type,
					"description": row.description,
					"debit": flt(row.debit),
					"credit": flt(row.credit),
					"balance": flt(row.balance),
				}
			)

	closing_balance = opening_balance + total_debits - total_credits
	min_payment_pct = flt(acct.minimum_payment_percent) or 10
	minimum_due = max(0, flt(closing_balance) * min_payment_pct / 100)

	store_name = frappe.db.get_single_value("Selling Settings", "company") or "Zevar Jewelry"
	store_address = frappe.db.get_value("Company", store_name, "address_line1") or ""

	statement = {
		"account_id": account_id,
		"customer": acct.customer,
		"customer_name": customer_name,
		"customer_email": email,
		"customer_address": _get_customer_address(acct.customer),
		"store_name": store_name,
		"store_address": store_address,
		"statement_date": str(today_date),
		"period_start": str(period_start),
		"period_end": str(period_end),
		"period_label": period_start.strftime("%B %Y"),
		"opening_balance": flt(opening_balance),
		"total_debits": flt(total_debits),
		"total_credits": flt(total_credits),
		"closing_balance": flt(closing_balance),
		"minimum_due": flt(minimum_due),
		"payment_due_date": str(get_last_day(today_date)),
		"interest_rate": flt(acct.interest_rate),
		"account_status": acct.status,
		"entries": entries,
	}

	return statement


def _get_customer_address(customer: str) -> str:
	addr = frappe.get_all(
		"Address",
		filters={"link_doctype": "Customer", "link_name": customer},
		fields=["address_line1", "address_line2", "city", "state", "pincode"],
		limit=1,
	)
	if addr:
		a = addr[0]
		parts = [a.get("address_line1", ""), a.get("address_line2", "")]
		city_state = f"{a.get('city', '')}, {a.get('state', '')} {a.get('pincode', '')}"
		parts.append(city_state)
		return ", ".join(p for p in parts if p)
	return ""


@frappe.whitelist(methods=["POST"])
def email_customer_statement(account_id: str, month: int | None = None, year: int | None = None) -> dict:
	"""Generate and email a customer statement."""
	frappe.only_for(["Sales Manager", "Accounts Manager", "System Manager"])

	stmt = generate_customer_statement(account_id, month, year)

	if not stmt["customer_email"]:
		frappe.throw(_("Customer has no email address configured."))

	body = _format_statement_email(stmt)
	subject = f"Your {stmt['period_label']} Statement - Account {stmt['account_id']}"

	frappe.sendmail(
		recipients=[stmt["customer_email"]],
		subject=subject,
		message=body,
		reference_doctype="In-House Finance Account",
		reference_name=account_id,
		queued=True,
	)

	return {"success": True, "email": stmt["customer_email"], "period": stmt["period_label"]}


def _format_statement_email(stmt: dict) -> str:
	rows = ""
	for e in stmt["entries"]:
		rows += (
			f"<tr>"
			f"<td style='padding:4px 8px'>{e['date']}</td>"
			f"<td style='padding:4px 8px'>{e['type']}</td>"
			f"<td style='padding:4px 8px'>{e['description']}</td>"
			f"<td style='padding:4px 8px;text-align:right'>{e['debit']:,.2f}</td>"
			f"<td style='padding:4px 8px;text-align:right'>{e['credit']:,.2f}</td>"
			f"<td style='padding:4px 8px;text-align:right'>{e['balance']:,.2f}</td>"
			f"</tr>"
		)

	return (
		f"<p>Dear {stmt['customer_name']},</p>"
		f"<p>Please find your account statement for <strong>{stmt['period_label']}</strong> below.</p>"
		f"<table border='1' cellpadding='4' cellspacing='0' style='border-collapse:collapse;width:100%'>"
		f"<tr style='background:#f0f0f0'>"
		f"<th>Date</th><th>Type</th><th>Description</th>"
		f"<th style='text-align:right'>Debit</th><th style='text-align:right'>Credit</th>"
		f"<th style='text-align:right'>Balance</th>"
		f"</tr>"
		f"{rows}"
		f"</table>"
		f"<p style='margin-top:12px'>"
		f"<strong>Opening Balance:</strong> ${stmt['opening_balance']:,.2f}<br>"
		f"<strong>Total Charges:</strong> ${stmt['total_debits']:,.2f}<br>"
		f"<strong>Total Payments:</strong> ${stmt['total_credits']:,.2f}<br>"
		f"<strong>Closing Balance:</strong> ${stmt['closing_balance']:,.2f}<br>"
		f"<strong>Minimum Payment Due:</strong> ${stmt['minimum_due']:,.2f} by {stmt['payment_due_date']}"
		f"</p>"
		f"<p>Thank you for your business.<br>{stmt['store_name']}</p>"
	)


# ── Batch Statement Sending (Scheduled) ────────────────────


def send_monthly_statements():
	"""
	Scheduled Job: send monthly statements to all active finance account holders.
	Runs on the 1st of each month for the previous month.
	"""
	accounts = frappe.get_all(
		"In-House Finance Account",
		filters={"status": ["in", ["Active", "Collections"]], "current_balance": [">", 0]},
		fields=["name", "customer"],
	)

	for acct in accounts:
		email = frappe.db.get_value("Customer", acct.customer, "email_id")
		if email:
			try:
				email_customer_statement(acct.name)
			except Exception:
				frappe.log_error(f"Statement Email Error: {acct.name}", frappe.get_traceback())
