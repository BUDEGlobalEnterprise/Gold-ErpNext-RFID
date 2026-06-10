import frappe
from frappe.tests.utils import FrappeTestCase


class TestPOSSyncConflict(FrappeTestCase):
	def test_create_conflict(self):
		doc = frappe.get_doc(
			{
				"doctype": "POS Sync Conflict",
				"idempotency_key": "test-conflict-001",
				"conflict_type": "stock_unavailable",
				"server_error": "Item RG001 not available in Showcase",
				"offline_order": '{"items": [{"item_code": "RG001"}]}',
			}
		).insert(ignore_permissions=True)

		self.assertEqual(doc.resolution, "pending")
		self.assertIsNotNone(doc.created_at)

		doc.resolve("resolved_cancel", notes="Customer chose to cancel")
		self.assertEqual(doc.resolution, "resolved_cancel")
		self.assertEqual(doc.resolved_by, frappe.session.user)

		doc.delete()
