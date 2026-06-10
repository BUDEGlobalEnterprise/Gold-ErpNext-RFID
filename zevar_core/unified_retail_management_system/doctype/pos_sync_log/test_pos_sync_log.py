import frappe
from frappe.tests.utils import FrappeTestCase


class TestPOSSyncLog(FrappeTestCase):
	def test_idempotency_key_uniqueness(self):
		key = "test-idem-key-001"
		if frappe.db.exists("POS Sync Log", {"idempotency_key": key}):
			frappe.delete_doc("POS Sync Log", frappe.db.get_value("POS Sync Log", {"idempotency_key": key}))

		doc = frappe.get_doc(
			{
				"doctype": "POS Sync Log",
				"idempotency_key": key,
				"sales_invoice": "SINV-00001",
			}
		).insert(ignore_permissions=True)

		duplicate = frappe.get_doc(
			{
				"doctype": "POS Sync Log",
				"idempotency_key": key,
				"sales_invoice": "SINV-00002",
			}
		)

		self.assertRaises(frappe.DuplicateEntryError, duplicate.insert, ignore_permissions=True)
		doc.delete()
