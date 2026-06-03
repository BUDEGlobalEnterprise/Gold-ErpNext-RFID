import frappe
from frappe.tests.utils import FrappeTestCase


class TestZevarPurity(FrappeTestCase):
	def setUp(self):
		self.cleanup_test_data()

	def tearDown(self):
		self.cleanup_test_data()

	def cleanup_test_data(self):
		for name in [
			"Test 24K",
			"Test 22K",
			"Test 18Kt",
			"Test 14Kt",
			"Test 10k",
			"Test 999 Fine",
			"Test 925 Sterling",
		]:
			if frappe.db.exists("Zevar Purity", name):
				frappe.delete_doc("Zevar Purity", name, ignore_permissions=True, force=True)
		frappe.db.commit()  # nosemgrep

	def test_create_zevar_purity(self):
		doc = frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 24K",
				"purity_code": "T24K",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)
		self.assertEqual(doc.name, "Test 24K")
		self.assertEqual(float(doc.fine_metal_content), 0.999)

	def test_zevar_purity_autoname_is_field_purity_name(self):
		meta = frappe.get_meta("Zevar Purity")
		self.assertEqual(meta.autoname, "field:purity_name")

	def test_zevar_purity_unique_name(self):
		frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 24K",
				"purity_code": "T24K",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)

		duplicate = frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 24K",
				"purity_code": "T24K",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		)
		self.assertRaises(frappe.exceptions.DuplicateEntryError, duplicate.insert)

	def test_zevar_purity_fine_metal_content_field(self):
		meta = frappe.get_meta("Zevar Purity")
		field = next((f for f in meta.fields if f.fieldname == "fine_metal_content"), None)
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "Float")

	def test_zevar_purity_delete(self):
		frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 24K",
				"purity_code": "T24K",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Zevar Purity", "Test 24K"))

		frappe.delete_doc("Zevar Purity", "Test 24K", ignore_permissions=True)
		self.assertFalse(frappe.db.exists("Zevar Purity", "Test 24K"))

	def test_zevar_purity_multiple_purities(self):
		purities = [
			("Test 24K", "T24K", 0.999),
			("Test 22K", "T22K", 0.916),
			("Test 18Kt", "T18K", 0.750),
			("Test 14Kt", "T14K", 0.585),
			("Test 10k", "T10K", 0.417),
		]
		for name, code, content in purities:
			frappe.get_doc(
				{
					"doctype": "Zevar Purity",
					"purity_name": name,
					"purity_code": code,
					"fine_metal_content": content,
					"metal": "Yellow Gold",
				}
			).insert(ignore_permissions=True)

		all_purities = frappe.get_all("Zevar Purity", filters={"name": ["like", "Test %"]}, pluck="name")
		self.assertEqual(len(all_purities), 5)

	def test_zevar_purity_silver_purities(self):
		frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 999 Fine",
				"purity_code": "T999",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 925 Sterling",
				"purity_code": "T925",
				"fine_metal_content": 0.925,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)

		doc_999 = frappe.get_doc("Zevar Purity", "Test 999 Fine")
		doc_925 = frappe.get_doc("Zevar Purity", "Test 925 Sterling")
		self.assertEqual(float(doc_999.fine_metal_content), 0.999)
		self.assertEqual(float(doc_925.fine_metal_content), 0.925)

	def test_zevar_purity_update_content(self):
		doc = frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 24K",
				"purity_code": "T24K",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)

		doc.fine_metal_content = 0.995
		doc.save(ignore_permissions=True)

		loaded = frappe.get_doc("Zevar Purity", "Test 24K")
		self.assertEqual(float(loaded.fine_metal_content), 0.995)

	def test_zevar_purity_used_in_gold_rate_log(self):
		frappe.get_doc(
			{
				"doctype": "Zevar Purity",
				"purity_name": "Test 24K",
				"purity_code": "T24K",
				"fine_metal_content": 0.999,
				"metal": "Yellow Gold",
			}
		).insert(ignore_permissions=True)

		meta = frappe.get_meta("Gold Rate Log")
		purity_field = next((f for f in meta.fields if f.fieldname == "purity"), None)
		self.assertIsNotNone(purity_field)
		self.assertEqual(purity_field.fieldtype, "Link")
		self.assertEqual(purity_field.options, "Zevar Purity")

	def test_zevar_purity_allow_rename(self):
		meta = frappe.get_meta("Zevar Purity")
		self.assertTrue(meta.allow_rename)
