import frappe
from frappe.tests.utils import FrappeTestCase


class TestZevarMetal(FrappeTestCase):
	def setUp(self):
		self.cleanup_test_data()

	def tearDown(self):
		self.cleanup_test_data()

	def cleanup_test_data(self):
		for name in ["Test Metal Gold", "Test Metal Silver", "Test Metal Platinum"]:
			if frappe.db.exists("Zevar Metal", name):
				frappe.delete_doc("Zevar Metal", name, ignore_permissions=True, force=True)
		frappe.db.commit()  # nosemgrep

	def test_create_zevar_metal(self):
		doc = frappe.get_doc({
			"doctype": "Zevar Metal",
			"metal_name": "Test Metal Gold",
			"metal_code": "TMG"
		}).insert(ignore_permissions=True)
		self.assertEqual(doc.name, "Test Metal Gold")

	def test_zevar_metal_autoname_is_field_metal_name(self):
		meta = frappe.get_meta("Zevar Metal")
		self.assertEqual(meta.autoname, "field:metal_name")

	def test_zevar_metal_unique_name(self):
		frappe.get_doc({
			"doctype": "Zevar Metal",
			"metal_name": "Test Metal Gold",
			"metal_code": "TMG"
		}).insert(ignore_permissions=True)

		duplicate = frappe.get_doc({
			"doctype": "Zevar Metal",
			"metal_name": "Test Metal Gold",
			"metal_code": "TMG"
		})
		self.assertRaises(frappe.exceptions.DuplicateEntryError, duplicate.insert)

	def test_zevar_metal_delete(self):
		frappe.get_doc({
			"doctype": "Zevar Metal",
			"metal_name": "Test Metal Gold",
			"metal_code": "TMG"
		}).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Zevar Metal", "Test Metal Gold"))

		frappe.delete_doc("Zevar Metal", "Test Metal Gold", ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Zevar Metal", "Test Metal Gold"))

	def test_zevar_metal_rename(self):
		frappe.get_doc({
			"doctype": "Zevar Metal",
			"metal_name": "Test Metal Gold",
			"metal_code": "TMG"
		}).insert(ignore_permissions=True)

		meta = frappe.get_meta("Zevar Metal")
		self.assertTrue(meta.allow_rename)

	def test_zevar_metal_multiple_types(self):
		codes = {"Test Metal Gold": "TMG", "Test Metal Silver": "TMS", "Test Metal Platinum": "TMP"}
		for name in ["Test Metal Gold", "Test Metal Silver", "Test Metal Platinum"]:
			frappe.get_doc({
				"doctype": "Zevar Metal",
				"metal_name": name,
				"metal_code": codes[name]
			}).insert(ignore_permissions=True)

		metals = frappe.get_all(
			"Zevar Metal",
			filters={"name": ["in", ["Test Metal Gold", "Test Metal Silver", "Test Metal Platinum"]]},
			pluck="name",
		)
		self.assertEqual(len(metals), 3)

	def test_zevar_metal_used_in_gold_rate_log(self):
		frappe.get_doc({
			"doctype": "Zevar Metal",
			"metal_name": "Test Metal Gold",
			"metal_code": "TMG"
		}).insert(ignore_permissions=True)

		meta = frappe.get_meta("Gold Rate Log")
		metal_field = next((f for f in meta.fields if f.fieldname == "metal"), None)
		self.assertIsNotNone(metal_field)
		self.assertEqual(metal_field.fieldtype, "Link")
		self.assertEqual(metal_field.options, "Zevar Metal")

	def test_zevar_metal_system_manager_permission(self):
		meta = frappe.get_meta("Zevar Metal")
		perm = meta.permissions[0] if meta.permissions else None
		self.assertIsNotNone(perm)
		self.assertEqual(perm.role, "System Manager")
		self.assertTrue(perm.create)
		self.assertTrue(perm.write)
		self.assertTrue(perm.delete)
		self.assertTrue(perm.read)
