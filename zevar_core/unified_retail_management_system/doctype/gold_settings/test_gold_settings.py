import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime


class TestGoldSettings(FrappeTestCase):
	def setUp(self):
		self.cleanup_test_data()

	def tearDown(self):
		self.cleanup_test_data()

	def cleanup_test_data(self):
		if not frappe.db.table_exists("Gold Settings"):
			return
		# Ensure DocType is synced from JSON (Select options need correct newline separators)
		frappe.reload_doc("zevar_core", "doctype", "gold_settings")
		if frappe.db.exists("Gold Settings", "Gold Settings"):
			frappe.db.sql("DELETE FROM `tabGold Settings` WHERE name = 'Gold Settings'")
			frappe.db.commit()

	def test_gold_settings_is_single_doctype(self):
		meta = frappe.get_meta("Gold Settings")
		self.assertTrue(meta.issingle)

	def test_gold_settings_create_and_read(self):
		doc = frappe.get_doc("Gold Settings", "Gold Settings")
		doc.api_endpoint = "https://data-asg.goldprice.org/dbXRates/USD"
		doc.auto_update = 1
		doc.update_frequency = "15 min"
		doc.save(ignore_permissions=True)

		loaded = frappe.get_doc("Gold Settings", "Gold Settings")
		self.assertEqual(loaded.api_endpoint, "https://data-asg.goldprice.org/dbXRates/USD")
		self.assertTrue(loaded.auto_update)
		self.assertEqual(loaded.update_frequency, "15 min")

	def test_gold_settings_auto_update_default_false(self):
		doc = frappe.get_doc("Gold Settings", "Gold Settings")
		self.assertEqual(doc.auto_update, 0)

	def test_gold_settings_update_frequency_options(self):
		meta = frappe.get_meta("Gold Settings")
		freq_field = None
		for f in meta.fields:
			if f.fieldname == "update_frequency":
				freq_field = f
				break
		self.assertIsNotNone(freq_field)
		options = freq_field.options.split("\n") if freq_field.options else []
		options = [o.strip() for o in options if o.strip()]
		self.assertIn("15 min", options)
		self.assertIn("30 min", options)
		self.assertIn("60 min", options)

	def test_gold_settings_api_endpoint_field_type(self):
		meta = frappe.get_meta("Gold Settings")
		field = next((f for f in meta.fields if f.fieldname == "api_endpoint"), None)
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "Data")

	def test_gold_settings_api_key_is_password_type(self):
		meta = frappe.get_meta("Gold Settings")
		field = next((f for f in meta.fields if f.fieldname == "api_key"), None)
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "Password")

	def test_gold_settings_base_currency_is_link(self):
		meta = frappe.get_meta("Gold Settings")
		field = next((f for f in meta.fields if f.fieldname == "base_currency"), None)
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "Link")
		self.assertEqual(field.options, "Currency")

	def test_gold_settings_save_and_reload(self):
		doc = frappe.get_doc("Gold Settings", "Gold Settings")
		doc.api_endpoint = "https://test.example.com/api"
		doc.auto_update = 1
		doc.update_frequency = "30 min"
		doc.save(ignore_permissions=True)

		frappe.db.commit()
		frappe.clear_cache()

		loaded = frappe.get_doc("Gold Settings", "Gold Settings")
		self.assertEqual(loaded.api_endpoint, "https://test.example.com/api")
		self.assertEqual(loaded.update_frequency, "30 min")

	def test_gold_settings_update_endpoint(self):
		doc = frappe.get_doc("Gold Settings", "Gold Settings")
		doc.api_endpoint = "https://old-api.example.com"
		doc.save(ignore_permissions=True)

		doc.api_endpoint = "https://new-api.example.com"
		doc.save(ignore_permissions=True)

		loaded = frappe.get_doc("Gold Settings", "Gold Settings")
		self.assertEqual(loaded.api_endpoint, "https://new-api.example.com")
