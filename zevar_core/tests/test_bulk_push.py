import frappe
from frappe.tests.utils import FrappeTestCase


class TestBulkPush(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
		cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr") or "Z"

		from zevar_core.patches.v1_1.seed_warehouse_zones import execute as seed_warehouses

		seed_warehouses()

	def _create_test_item(self):
		code = f"TEST-PUSH-{frappe.generate_hash(length=6)}"
		if not frappe.db.exists("Item", code):
			item = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": code,
					"item_name": f"Test Push Item {code}",
					"item_group": "All Item Groups",
					"stock_uom": "Nos",
					"is_stock_item": 1,
				}
			)
			item.insert(ignore_permissions=True)
		return code

	def test_bulk_push_creates_stock_entries(self):
		from zevar_core.api.inventory import bulk_push_to_stores

		item_code = self._create_test_item()
		allocation = [
			{"store_code": "NY-01", "qty": 3},
			{"store_code": "Miami-01", "qty": 2},
			{"store_code": "LA-01", "qty": 2},
			{"store_code": "Houston-01", "qty": 2},
			{"store_code": "Chicago-01", "qty": 1},
		]

		result = bulk_push_to_stores(item_code=item_code, allocation=allocation)
		self.assertTrue(result["success"])
		self.assertEqual(len(result["results"]), 5)

		total_qty = sum(r["qty"] for r in result["results"])
		self.assertEqual(total_qty, 10)

		for r in result["results"]:
			self.assertTrue(r["stock_entry"])

	def test_bulk_push_zero_qty_skipped(self):
		from zevar_core.api.inventory import bulk_push_to_stores

		item_code = self._create_test_item()
		allocation = [
			{"store_code": "NY-01", "qty": 1},
			{"store_code": "Miami-01", "qty": 0},
		]

		result = bulk_push_to_stores(item_code=item_code, allocation=allocation)
		self.assertTrue(result["success"])
		self.assertEqual(len(result["results"]), 1)
