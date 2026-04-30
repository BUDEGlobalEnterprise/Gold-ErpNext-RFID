import frappe
from frappe.tests.utils import FrappeTestCase


class TestReportSubscriptions(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()

	def test_create_subscription(self):
		from zevar_core.api.reports import create_report_subscription

		result = create_report_subscription(
			report_id="low_stock_alert",
			cron_expression="0 22 * * *",
			delivery_method="Email",
			export_format="PDF",
		)
		self.assertEqual(result["status"], "created")
		self.assertTrue(result["name"])
		self.assertEqual(result["report_title"], "Low Stock Alert")

		if frappe.db.exists("Report Subscription", result["name"]):
			frappe.delete_doc("Report Subscription", result["name"], force=True)

	def test_get_subscriptions(self):
		from zevar_core.api.reports import (
			create_report_subscription,
			get_report_subscriptions,
		)

		sub = create_report_subscription(
			report_id="hourly_sales",
			cron_expression="0 22 * * *",
			delivery_method="Email",
		)
		subs = get_report_subscriptions()
		self.assertIsInstance(subs, list)
		ids = [s["report_id"] for s in subs]
		self.assertIn("hourly_sales", ids)

		if frappe.db.exists("Report Subscription", sub["name"]):
			frappe.delete_doc("Report Subscription", sub["name"], force=True)

	def test_delete_subscription(self):
		from zevar_core.api.reports import (
			create_report_subscription,
			delete_report_subscription,
		)

		sub = create_report_subscription(
			report_id="gold_rate_history",
			cron_expression="0 8 * * 1",
		)
		result = delete_report_subscription(name=sub["name"])
		self.assertEqual(result["status"], "deleted")
		self.assertFalse(frappe.db.exists("Report Subscription", sub["name"]))

	def test_toggle_subscription(self):
		from zevar_core.api.reports import (
			create_report_subscription,
			toggle_report_subscription,
		)

		sub = create_report_subscription(
			report_id="aged_inventory",
			cron_expression="0 22 * * *",
		)
		result = toggle_report_subscription(name=sub["name"])
		self.assertEqual(result["status"], "toggled")
		self.assertFalse(result["enabled"])

		result2 = toggle_report_subscription(name=sub["name"])
		self.assertTrue(result2["enabled"])

		if frappe.db.exists("Report Subscription", sub["name"]):
			frappe.delete_doc("Report Subscription", sub["name"], force=True)

	def test_duplicate_subscription_rejected(self):
		from zevar_core.api.reports import create_report_subscription

		sub = create_report_subscription(
			report_id="fast_moving_items",
			cron_expression="0 22 * * *",
		)
		with self.assertRaises(frappe.DuplicateEntryError):
			create_report_subscription(
				report_id="fast_moving_items",
				cron_expression="0 22 * * *",
			)
		if frappe.db.exists("Report Subscription", sub["name"]):
			frappe.delete_doc("Report Subscription", sub["name"], force=True)

	def test_unknown_report_rejected(self):
		from zevar_core.api.reports import create_report_subscription

		with self.assertRaises(frappe.ValidationError):
			create_report_subscription(report_id="nonexistent_report")

	def test_subscription_doc_type_fields(self):
		doc = frappe.new_doc("Report Subscription")
		doc.user = frappe.session.user
		doc.report_id = "test_report"
		doc.cron_expression = "0 22 * * *"
		doc.delivery_method = "Email"
		doc.export_format = "PDF"
		doc.insert(ignore_permissions=True)

		self.assertTrue(doc.name)
		self.assertEqual(doc.schedule_label, "Daily at 10 PM")
		self.assertTrue(doc.report_title)

		frappe.delete_doc("Report Subscription", doc.name, force=True)
