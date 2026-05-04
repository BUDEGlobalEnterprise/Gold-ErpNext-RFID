import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime


class TestGoldRateLog(FrappeTestCase):
	def setUp(self):
		self.cleanup_test_data()
		self.ensure_test_metal_and_purity()

	def tearDown(self):
		self.cleanup_test_data()

	def ensure_test_metal_and_purity(self):
		if not frappe.db.exists("Zevar Metal", "Yellow Gold"):
			frappe.get_doc({"doctype": "Zevar Metal", "__newname": "Yellow Gold"}).insert(
				ignore_permissions=True
			)
		if not frappe.db.exists("Zevar Metal", "Silver"):
			frappe.get_doc({"doctype": "Zevar Metal", "__newname": "Silver"}).insert(ignore_permissions=True)
		if not frappe.db.exists("Zevar Purity", "22Kt"):
			frappe.get_doc(
				{"doctype": "Zevar Purity", "__newname": "22Kt", "fine_metal_content": 0.916}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("Zevar Purity", "18Kt"):
			frappe.get_doc(
				{"doctype": "Zevar Purity", "__newname": "18Kt", "fine_metal_content": 0.750}
			).insert(ignore_permissions=True)
		frappe.db.commit()  # nosemgrep

	def cleanup_test_data(self):
		for name in frappe.get_all("Gold Rate Log", filters={"source": "test"}, pluck="name"):
			frappe.delete_doc("Gold Rate Log", name, ignore_permissions=True, force=True)
		frappe.db.commit()  # nosemgrep

	def test_create_gold_rate_log(self):
		doc = frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 78.50,
				"source": "test",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(doc.name)
		self.assertEqual(doc.metal, "Yellow Gold")
		self.assertEqual(doc.purity, "22Kt")
		self.assertEqual(float(doc.rate_per_gram), 78.50)

	def test_gold_rate_log_autoname_format(self):
		doc = frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 75.00,
				"source": "test",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(doc.name.startswith("GR-"))

	def test_gold_rate_log_metal_is_required(self):
		doc = frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"purity": "22Kt",
				"rate_per_gram": 75.00,
				"source": "test",
			}
		)
		self.assertRaises(frappe.exceptions.MandatoryError, doc.insert)

	def test_gold_rate_log_rate_is_required(self):
		doc = frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"source": "test",
			}
		)
		self.assertRaises(frappe.exceptions.MandatoryError, doc.insert)

	def test_gold_rate_log_update_rate(self):
		doc = frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 75.00,
				"source": "test",
			}
		).insert(ignore_permissions=True)

		frappe.db.set_value("Gold Rate Log", doc.name, "rate_per_gram", 80.00)
		updated = frappe.get_doc("Gold Rate Log", doc.name)
		self.assertEqual(float(updated.rate_per_gram), 80.00)

	def test_gold_rate_log_multiple_entries(self):
		for _i, rate in enumerate([75.0, 76.5, 78.0]):
			frappe.get_doc(
				{
					"doctype": "Gold Rate Log",
					"metal": "Yellow Gold",
					"purity": "22Kt",
					"rate_per_gram": rate,
					"source": "test",
				}
			).insert(ignore_permissions=True)

		entries = frappe.get_all(
			"Gold Rate Log",
			filters={"source": "test", "metal": "Yellow Gold", "purity": "22Kt"},
			pluck="rate_per_gram",
		)
		self.assertEqual(len(entries), 3)

	def test_gold_rate_log_different_metals(self):
		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 78.50,
				"source": "test",
			}
		).insert(ignore_permissions=True)

		if frappe.db.exists("Zevar Purity", "999 Fine"):
			purity = "999 Fine"
		else:
			purity = "22Kt"

		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Silver",
				"purity": purity,
				"rate_per_gram": 0.95,
				"source": "test",
			}
		).insert(ignore_permissions=True)

		gold_entries = frappe.get_all(
			"Gold Rate Log", filters={"metal": "Yellow Gold", "source": "test"}, pluck="name"
		)
		silver_entries = frappe.get_all(
			"Gold Rate Log", filters={"metal": "Silver", "source": "test"}, pluck="name"
		)
		self.assertEqual(len(gold_entries), 1)
		self.assertEqual(len(silver_entries), 1)

	def test_gold_rate_log_timestamp_default(self):
		doc = frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 78.50,
				"source": "test",
			}
		).insert(ignore_permissions=True)
		self.assertIsNotNone(doc.timestamp)

	def test_gold_rate_log_query_latest_rate(self):
		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 75.00,
				"source": "test",
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": "Yellow Gold",
				"purity": "22Kt",
				"rate_per_gram": 80.00,
				"source": "test",
			}
		).insert(ignore_permissions=True)

		latest = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["rate_per_gram"],
			order_by="creation desc",
			limit=1,
		)
		self.assertEqual(len(latest), 1)
		self.assertEqual(float(latest[0].rate_per_gram), 80.00)
