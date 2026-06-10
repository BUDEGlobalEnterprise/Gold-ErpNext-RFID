# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now, today


class FinanceAccountWriteOff(Document):
	def validate(self):
		self._fetch_account_info()
		self._validate_amount()
		self.approval_date = self.approval_date or today()

	def on_submit(self):
		self._apply_write_off()

	def before_cancel(self):
		self._reverse_write_off()

	def _fetch_account_info(self):
		if not self.finance_account:
			return
		acct = frappe.get_doc("In-House Finance Account", self.finance_account)
		self.customer = acct.customer
		self.customer_name = frappe.db.get_value("Customer", acct.customer, "customer_name") or ""
		self.remaining_balance = flt(acct.current_balance) - flt(self.write_off_amount)
		self.account_status_before = acct.status

	def _validate_amount(self):
		if flt(self.write_off_amount) <= 0:
			frappe.throw(_("Write-off amount must be greater than zero."))

		acct = frappe.get_doc("In-House Finance Account", self.finance_account)
		if flt(self.write_off_amount) > flt(acct.current_balance):
			frappe.throw(
				_("Write-off amount cannot exceed current balance of {0}.").format(flt(acct.current_balance))
			)

		if self.approved_by == frappe.session.user:
			frappe.throw(_("You cannot approve your own write-off request."))

	def _apply_write_off(self):
		acct = frappe.get_doc("In-House Finance Account", self.finance_account)

		acct.append(
			"ledger_entries",
			{
				"entry_date": self.write_off_date or today(),
				"entry_type": "Write-Off",
				"description": f"Bad Debt Write-Off: {self.reason or 'N/A'}",
				"credit": flt(self.write_off_amount),
			},
		)

		running_balance = 0.0
		for entry in acct.ledger_entries:
			running_balance += flt(entry.debit) - flt(entry.credit)
			entry.balance = running_balance

		acct.current_balance = running_balance
		acct.available_credit = flt(acct.credit_limit) - running_balance
		acct.status = "Closed" if flt(acct.current_balance) <= 0 else "Collections"

		self.account_status_after = acct.status
		self.remaining_balance = flt(acct.current_balance)

		acct.flags.ignore_validate_update_after_submit = True
		acct.save()

		from zevar_core.api.audit_log import log_event_safely

		log_event_safely(
			event_type="finance_write_off",
			details={
				"account": self.finance_account,
				"customer": self.customer,
				"amount": flt(self.write_off_amount),
				"reason": self.reason,
				"approved_by": self.approved_by,
			},
			reference_document=self.name,
			reference_type=self.doctype,
		)

	def _reverse_write_off(self):
		acct = frappe.get_doc("In-House Finance Account", self.finance_account)

		acct.append(
			"ledger_entries",
			{
				"entry_date": today(),
				"entry_type": "Purchase",
				"description": f"Write-Off Cancellation: {self.name}",
				"debit": flt(self.write_off_amount),
			},
		)

		running_balance = 0.0
		for entry in acct.ledger_entries:
			running_balance += flt(entry.debit) - flt(entry.credit)
			entry.balance = running_balance

		acct.current_balance = running_balance
		acct.available_credit = flt(acct.credit_limit) - running_balance
		if flt(acct.current_balance) > 0:
			acct.status = "Active"

		acct.flags.ignore_validate_update_after_submit = True
		acct.save()
