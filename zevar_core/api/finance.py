"""
Finance API - In-House Finance account payments and scheduled charges
"""

import frappe
from frappe import _
from frappe.utils import flt, today


@frappe.whitelist(methods=["GET"])
def get_customer_finance_account(customer: str) -> dict:
	"""Return the In-House Finance Account details for a customer."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	accounts = frappe.get_all(
		"In-House Finance Account",
		filters={"customer": customer},
		limit=1,
	)
	if not accounts:
		return {"exists": False}

	doc = frappe.get_doc("In-House Finance Account", accounts[0].name)

	return {
		"exists": True,
		"account_id": doc.name,
		"customer": doc.customer,
		"status": doc.status,
		"credit_limit": flt(doc.credit_limit),
		"current_balance": flt(doc.current_balance),
		"available_credit": flt(doc.available_credit),
		"interest_rate": flt(doc.interest_rate),
		"minimum_payment_percent": flt(doc.minimum_payment_percent),
		"ledger_entries": [
			{
				"entry_date": str(row.entry_date),
				"entry_type": row.entry_type,
				"description": row.description,
				"debit": flt(row.debit),
				"credit": flt(row.credit),
				"balance": flt(row.balance),
			}
			for row in (doc.ledger_entries or [])
		],
	}


@frappe.whitelist(methods=["POST"])
def process_finance_payment(account_id: str, amount: float, mode_of_payment: str) -> dict:
	"""Process a payment towards an In-House Finance Account balance."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	amount_flt = flt(amount)
	if amount_flt <= 0:
		frappe.throw(_("Payment amount must be greater than zero."))

	if not mode_of_payment:
		frappe.throw(_("Mode of payment is required."))

	if not account_id or not frappe.db.exists("In-House Finance Account", account_id):
		frappe.throw(_("Finance Account '{0}' not found.").format(account_id))

	doc = frappe.get_doc("In-House Finance Account", account_id)

	if doc.status in ("Closed", "Suspended"):
		frappe.throw(_("Account is {0}. Cannot process payment.").format(doc.status))

	if amount_flt > flt(doc.current_balance):
		frappe.throw(_("Payment amount cannot exceed current balance."))

	try:
		doc.append(
			"ledger_entries",
			{
				"entry_date": today(),
				"entry_type": "Payment",
				"description": f"Payment via {mode_of_payment}",
				"credit": amount_flt,
			},
		)

		# Recalculate balances
		running_balance = 0.0
		for entry in doc.get("ledger_entries", []):
			running_balance += flt(entry.debit) - flt(entry.credit)
			entry.balance = running_balance

		doc.current_balance = running_balance
		doc.available_credit = flt(doc.credit_limit) - running_balance

		doc.flags.ignore_validate_update_after_submit = True
		doc.save(ignore_permissions=True)

		from zevar_core.api.audit_log import log_event_safely

		log_event_safely(
			event_type="finance_payment",
			details={
				"account_id": doc.name,
				"customer": doc.customer,
				"payment_amount": amount_flt,
				"mode_of_payment": mode_of_payment,
				"new_balance": flt(doc.current_balance),
				"available_credit": flt(doc.available_credit),
			},
			reference_document=doc.name,
			reference_type="In-House Finance Account",
		)

		frappe.db.commit()  # nosemgrep

		return {
			"success": True,
			"new_balance": doc.current_balance,
			"available_credit": doc.available_credit,
			"message": "Finance Payment processed successfully",
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Finance Payment Error", frappe.get_traceback())
		raise frappe.ValidationError(f"Failed to process Finance Payment: {e!s}")


@frappe.whitelist(methods=["GET"])
def generate_monthly_statement(account_id: str, month: int, year: int) -> dict:
	"""Generate a monthly statement for an In-House Finance Account."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not account_id or not frappe.db.exists("In-House Finance Account", account_id):
		frappe.throw(_("Finance Account '{0}' not found.").format(account_id))

	month = int(month)
	year = int(year)
	if month < 1 or month > 12:
		frappe.throw(_("Month must be between 1 and 12."))

	doc = frappe.get_doc("In-House Finance Account", account_id)

	# Filter ledger entries for the requested month
	from frappe.utils import getdate

	entries = []
	total_debits = 0.0
	total_credits = 0.0

	for row in doc.ledger_entries or []:
		entry_date = getdate(row.entry_date)
		if entry_date.month == month and entry_date.year == year:
			total_debits += flt(row.debit)
			total_credits += flt(row.credit)
			entries.append(
				{
					"entry_date": str(row.entry_date),
					"entry_type": row.entry_type,
					"description": row.description,
					"debit": flt(row.debit),
					"credit": flt(row.credit),
				}
			)

	# Compute opening balance (sum of all entries before this month)
	opening_balance = 0.0
	for row in doc.ledger_entries or []:
		entry_date = getdate(row.entry_date)
		if entry_date.year < year or (entry_date.year == year and entry_date.month < month):
			opening_balance += flt(row.debit) - flt(row.credit)

	closing_balance = opening_balance + total_debits - total_credits

	return {
		"account_id": doc.name,
		"customer": doc.customer,
		"month": month,
		"year": year,
		"opening_balance": opening_balance,
		"total_debits": total_debits,
		"total_credits": total_credits,
		"closing_balance": closing_balance,
		"entries": entries,
	}


def apply_finance_charges():
	"""
	Scheduled Job: apply monthly interest to active accounts with balances.
	Not whitelisted — called only by scheduler.
	"""
	accounts = frappe.get_all(
		"In-House Finance Account",
		filters={"status": ["in", ["Active", "Collections"]], "current_balance": [">", 0]},
		fields=["name", "interest_rate", "current_balance"],
	)

	for acc in accounts:
		interest_rate = flt(acc.interest_rate)
		if interest_rate <= 0:
			continue

		monthly_rate = interest_rate / 12 / 100
		charge_amount = flt(acc.current_balance * monthly_rate, 2)

		if charge_amount > 0:
			try:
				doc = frappe.get_doc("In-House Finance Account", acc.name)

				doc.append(
					"ledger_entries",
					{
						"entry_date": today(),
						"entry_type": "Finance Charge",
						"description": f"Monthly Finance Charge ({interest_rate}% APR)",
						"debit": charge_amount,
					},
				)

				# Recalculate balances
				running_balance = 0.0
				for entry in doc.get("ledger_entries", []):
					running_balance += flt(entry.debit) - flt(entry.credit)
					entry.balance = running_balance

				doc.current_balance = running_balance
				doc.available_credit = flt(doc.credit_limit) - running_balance

				doc.flags.ignore_validate_update_after_submit = True
				doc.save(ignore_permissions=True)
				frappe.db.commit()  # nosemgrep
			except Exception:
				frappe.db.rollback()
				frappe.log_error(f"Finance Charge Error for {acc.name}", frappe.get_traceback())


@frappe.whitelist(methods=["GET"])
def get_dashboard_summary():
	"""KPI snapshot for the Finance tab: net profit, AR, AP, cash."""
	frappe.only_for(["System Manager", "Accounts Manager", "Store Manager", "Sales Manager"])

	company = frappe.defaults.get_user_default("Company")
	if not company:
		company = frappe.db.get_value("Company", {}, "name")

	from frappe.utils import getdate

	today = frappe.utils.nowdate()
	month_start = getdate(today).replace(day=1)

	from frappe.query_builder.functions import Coalesce, Sum

	income_total = 0.0
	expense_total = 0.0
	ar_outstanding = 0.0
	ap_outstanding = 0.0
	cash_balance = 0.0

	# Income MTD
	income_accounts = frappe.get_all(
		"Account", filters={"root_type": "Income", "company": company, "is_group": 0}, pluck="name"
	)
	if income_accounts:
		gl = frappe.qb.DocType("GL Entry")
		row = (
			frappe.qb.from_(gl)
			.select(Coalesce(Sum(gl.credit - gl.debit), 0).as_("total"))
			.where(
				(gl.account.isin(income_accounts))
				& (gl.docstatus == 1)
				& (gl.posting_date >= month_start)
				& (gl.posting_date <= today)
				& (gl.company == company)
				& (gl.is_cancelled == 0)
			)
		).run(as_dict=True)
		income_total = flt(row[0].total) if row else 0

	# Expense MTD
	expense_accounts = frappe.get_all(
		"Account", filters={"root_type": "Expense", "company": company, "is_group": 0}, pluck="name"
	)
	if expense_accounts:
		gl = frappe.qb.DocType("GL Entry")
		row = (
			frappe.qb.from_(gl)
			.select(Coalesce(Sum(gl.debit - gl.credit), 0).as_("total"))
			.where(
				(gl.account.isin(expense_accounts))
				& (gl.docstatus == 1)
				& (gl.posting_date >= month_start)
				& (gl.posting_date <= today)
				& (gl.company == company)
				& (gl.is_cancelled == 0)
			)
		).run(as_dict=True)
		expense_total = flt(row[0].total) if row else 0

	# AR outstanding
	default_receivable = frappe.db.get_value(
		"Account", {"account_type": "Receivable", "company": company, "is_group": 0}, "name"
	)
	if default_receivable:
		row = frappe.db.sql(
			"""SELECT COALESCE(SUM(debit - credit), 0) AS bal
			FROM `tabGL Entry`
			WHERE account = %s AND docstatus = 1 AND is_cancelled = 0""",
			(default_receivable,),
			as_dict=True,
		)
		ar_outstanding = flt(row[0].bal) if row else 0

	# AP outstanding
	default_payable = frappe.db.get_value(
		"Account", {"account_type": "Payable", "company": company, "is_group": 0}, "name"
	)
	if default_payable:
		row = frappe.db.sql(
			"""SELECT COALESCE(SUM(credit - debit), 0) AS bal
			FROM `tabGL Entry`
			WHERE account = %s AND docstatus = 1 AND is_cancelled = 0""",
			(default_payable,),
			as_dict=True,
		)
		ap_outstanding = flt(row[0].bal) if row else 0

	# Cash / bank balance
	cash_accounts = frappe.get_all(
		"Account",
		filters={"account_type": "Cash", "company": company, "is_group": 0},
		pluck="name",
	)
	bank_accounts = frappe.get_all(
		"Account",
		filters={"account_type": "Bank", "company": company, "is_group": 0},
		pluck="name",
	)
	all_liquid = cash_accounts + bank_accounts
	if all_liquid:
		placeholders = ", ".join(["%s"] * len(all_liquid))
		row = frappe.db.sql(
			f"""SELECT COALESCE(SUM(debit - credit), 0) AS bal
			FROM `tabGL Entry`
			WHERE account IN ({placeholders}) AND docstatus = 1 AND is_cancelled = 0""",
			tuple(all_liquid),
			as_dict=True,
		)
		cash_balance = flt(row[0].bal) if row else 0

	return {
		"net_profit_mtd": flt(income_total - expense_total, 2),
		"ar_outstanding": flt(ar_outstanding, 2),
		"ap_outstanding": flt(ap_outstanding, 2),
		"cash_balance": flt(cash_balance, 2),
	}
