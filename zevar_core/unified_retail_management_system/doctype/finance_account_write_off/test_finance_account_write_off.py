# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


class TestFinanceAccountWriteOff(FrappeTestCase):
	def test_validate_amount_positive(self):
		wo = frappe.new_doc("Finance Account Write Off")
		wo.finance_account = "FIN-001"
		wo.write_off_amount = -100
		wo.reason = "Other"
		wo.approved_by = "Administrator"
		self.assertRaises(frappe.ValidationError, wo.insert)

	def test_write_off_exceeds_balance(self):
		wo = frappe.new_doc("Finance Account Write Off")
		wo.finance_account = "FIN-001"
		wo.write_off_amount = 999999
		wo.reason = "Other"
		wo.approved_by = "Administrator"
		self.assertRaises(frappe.ValidationError, wo.insert)
