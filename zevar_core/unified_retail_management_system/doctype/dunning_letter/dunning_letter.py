# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now, getdate, today


class DunningLetter(Document):
	def validate(self):
		self._fetch_account_details()
		self._compute_overdue()

	def on_submit(self):
		self._send_letter()

	def _fetch_account_details(self):
		if not self.finance_account or not frappe.db.exists("In-House Finance Account", self.finance_account):
			return

		acct = frappe.get_doc("In-House Finance Account", self.finance_account)
		self.customer = acct.customer
		self.customer_name = frappe.db.get_value("Customer", acct.customer, "customer_name") or ""
		self.total_balance = flt(acct.current_balance)
		self.interest_rate = flt(acct.interest_rate)
		self.minimum_due = flt(acct.current_balance) * flt(acct.minimum_payment_percent) / 100

		last_payment = frappe.get_all(
			"Customer Ledger Entry",
			filters={"parent": self.finance_account, "parenttype": "In-House Finance Account", "entry_type": "Payment"},
			fields=["entry_date"],
			order_by="entry_date desc",
			limit=1,
		)
		self.last_payment_date = last_payment[0].entry_date if last_payment else None

	def _compute_overdue(self):
		acct = frappe.get_doc("In-House Finance Account", self.finance_account)
		overdue = 0.0
		overdue_entry_date = None
		today_date = getdate(today())

		for entry in acct.ledger_entries or []:
			if flt(entry.debit) > 0:
				days = (today_date - getdate(entry.entry_date)).days
				if days > 30:
					overdue += flt(entry.debit)
					if overdue_entry_date is None:
						overdue_entry_date = entry.entry_date

		self.overdue_amount = flt(overdue)

		if overdue_entry_date:
			self.overdue_days = (today_date - getdate(overdue_entry_date)).days

	def _send_letter(self):
		email = frappe.db.get_value("Customer", self.customer, "email_id")
		if not email:
			frappe.throw(_("Customer has no email address configured."))

		frappe.sendmail(
			recipients=[email],
			subject=self.subject,
			message=self.message_body,
			reference_doctype=self.doctype,
			reference_name=self.name,
			queued=True,
		)

		self.sent_date = now()
		self.sent_by = frappe.session.user
		self.status = "Sent"
		self.save()

		acct = frappe.get_doc("In-House Finance Account", self.finance_account)
		if "Level 3" in (self.dunning_level or ""):
			if acct.status != "Collections":
				acct.status = "Collections"
				acct.flags.ignore_validate_update_after_submit = True
				acct.save()

		from zevar_core.api.audit_log import log_event_safely
		log_event_safely(
			event_type="dunning_letter_sent",
			details={
				"account": self.finance_account,
				"customer": self.customer,
				"level": self.dunning_level,
				"overdue_amount": flt(self.overdue_amount),
				"email": email,
			},
			reference_document=self.name,
			reference_type=self.doctype,
		)
