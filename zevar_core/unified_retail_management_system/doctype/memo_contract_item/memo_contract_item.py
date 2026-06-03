# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MemoContractItem(Document):
	def validate(self):
		self._sync_line_status_from_status()

	def _sync_line_status_from_status(self):
		"""Keep line_status in sync with the legacy status field."""
		status_map = {
			"On Memo": "Open",
			"Sold": "Sold",
			"Returned": "Returned",
			"Lost": "Lost",
		}
		expected = status_map.get(self.status, self.line_status)
		if expected and self.line_status != expected:
			self.line_status = expected

	def record_return(self, returned_by=None, return_slip=None, vendor_signed_by=None):
		"""Mark this item as returned with audit trail."""
		if self.line_status not in ("Open", "On Memo"):
			frappe.throw(
				_("Item {0} cannot be returned — current status is '{1}'").format(
					self.item_code, self.line_status
				)
			)

		self.line_status = "Returned"
		self.status = "Returned"
		self.returned_at = now_datetime()
		self.returned_by = returned_by or frappe.session.user
		self.date_returned = frappe.utils.today()

		if return_slip:
			self.return_slip_ref = return_slip
		if vendor_signed_by:
			self.vendor_signed_by = vendor_signed_by
			self.vendor_signed_at = now_datetime()

		self.save(ignore_permissions=True)
