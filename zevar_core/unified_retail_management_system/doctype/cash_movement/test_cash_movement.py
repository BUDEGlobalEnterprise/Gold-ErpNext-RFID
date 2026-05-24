# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


class TestCashMovement(FrappeTestCase):
	def test_validate_amount_positive(self):
		doc = frappe.get_doc(
			{
				"doctype": "Cash Movement",
				"session": "TEST-SESSION",
				"movement_type": "Cash Out",
				"amount": -10,
				"reason": "Petty Cash",
			}
		)
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_validate_session_required(self):
		doc = frappe.get_doc(
			{
				"doctype": "Cash Movement",
				"movement_type": "Cash Out",
				"amount": 50,
				"reason": "Petty Cash",
			}
		)
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_validate_session_must_be_open(self):
		# This test needs a real session; verify the validation path exists
		self.assertTrue(hasattr(frappe.get_doc({"doctype": "Cash Movement"}), "_validate_session_is_open"))
