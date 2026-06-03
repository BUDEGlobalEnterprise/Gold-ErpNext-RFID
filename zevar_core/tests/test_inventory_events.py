import frappe
from frappe.tests.utils import FrappeTestCase


class TestInventoryEvents(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
		if not frappe.db.exists("Company", cls.company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Zevar Jewelers",
					"abbr": "Z",
					"default_currency": "USD",
					"country": "United States",
				}
			).insert(ignore_permissions=True)

		cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr") or "Z"

		from zevar_core.patches.v1_1.seed_warehouse_zones import execute as seed_warehouses

		seed_warehouses()

	def _create_test_item(self, item_code=None):
		code = item_code or f"TEST-ITEM-{frappe.generate_hash(length=6)}"
		if not frappe.db.exists("Item", code):
			item = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": code,
					"item_name": f"Test Item {code}",
					"item_group": "All Item Groups",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"has_serial_no": 1,
					"company": self.company,
				}
			)
			item.insert(ignore_permissions=True)
		return code

	def _create_serial_no(self, item_code, warehouse):
		sn = f"SN-{frappe.generate_hash(length=8)}"
		if not frappe.db.exists("Serial No", sn):
			doc = frappe.get_doc(
				{
					"doctype": "Serial No",
					"serial_no": sn,
					"item_code": item_code,
					"company": self.company,
				}
			)
			doc.insert(ignore_permissions=True)
			# Set warehouse via db.set_value to bypass ERPNext validation
			frappe.db.set_value("Serial No", sn, "warehouse", warehouse)
		return sn

	def _get_back_stock_wh(self, store_code="NY-01"):
		wh = f"Back Stock {store_code} - {self.abbr}"
		if frappe.db.exists("Warehouse", wh):
			return wh
		return f"Stores - {self.abbr}"

	def _get_showcase_wh(self, store_code="NY-01"):
		wh = f"Showcase {store_code} - {self.abbr}"
		if frappe.db.exists("Warehouse", wh):
			return wh
		return f"Stores - {self.abbr}"

	def _get_shrinkage_wh(self, store_code="NY-01"):
		wh = f"Shrinkage {store_code} - {self.abbr}"
		if frappe.db.exists("Warehouse", wh):
			return wh
		wh = frappe.db.get_value("Warehouse", {"warehouse_name": ["like", "%Shrinkage%"]}, "name")
		return wh

	def test_01_material_receipt(self):
		from zevar_core.services.inventory_events import material_receipt

		item_code = self._create_test_item()
		back_stock = self._get_back_stock_wh()
		sn = self._create_serial_no(item_code, back_stock)

		se = material_receipt(item_code, back_stock, qty=1, serial_no=sn)
		self.assertTrue(se.name)
		self.assertEqual(se.stock_entry_type, "Material Receipt")
		self.assertEqual(len(se.items), 1)

	def test_02_move_to_showcase(self):
		from zevar_core.services.inventory_events import move_to_showcase

		item_code = self._create_test_item()
		back_stock = self._get_back_stock_wh()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, back_stock)

		se = move_to_showcase(sn, item_code, back_stock, showcase)
		self.assertTrue(se.name)
		self.assertEqual(se.items[0].s_warehouse, back_stock)
		self.assertEqual(se.items[0].t_warehouse, showcase)

	def test_03_damage_write_off(self):
		from zevar_core.services.inventory_events import damage_write_off

		item_code = self._create_test_item()
		showcase = self._get_showcase_wh()
		shrinkage = self._get_shrinkage_wh()
		sn = self._create_serial_no(item_code, showcase)

		se = damage_write_off(sn, item_code, showcase, shrinkage, reason="Scratched")
		self.assertTrue(se.name)

	def test_04_gift_out(self):
		from zevar_core.services.inventory_events import gift_out

		item_code = self._create_test_item()
		back_stock = self._get_back_stock_wh()
		sn = self._create_serial_no(item_code, back_stock)

		se = gift_out(sn, item_code, back_stock, reason="Promotional")
		self.assertTrue(se.name)
		self.assertEqual(se.stock_entry_type, "Material Issue")

	def test_05_trade_in_accept(self):
		from zevar_core.services.inventory_events import trade_in_accept

		item_code = self._create_test_item()
		back_stock = self._get_back_stock_wh()

		se = trade_in_accept(item_code, back_stock, valuation_rate=500.0)
		self.assertTrue(se.name)

	def test_06_vendor_return(self):
		from zevar_core.services.inventory_events import vendor_return

		item_code = self._create_test_item()
		back_stock = self._get_back_stock_wh()
		sn = self._create_serial_no(item_code, back_stock)

		se = vendor_return(sn, item_code, back_stock, reason="RMA")
		self.assertTrue(se.name)

	def test_07_recover_found_piece(self):
		from zevar_core.services.inventory_events import recover_found_piece

		item_code = self._create_test_item()
		showcase = self._get_showcase_wh()

		se = recover_found_piece("SN-FOUND-001", item_code, showcase, "SHRINKAGE-001")
		self.assertTrue(se.name)

	def test_08_repair_in_out(self):
		from zevar_core.services.inventory_events import repair_in

		item_code = self._create_test_item()
		repair_bench = f"Repair Bench NY-01 - {self.abbr}"
		if not frappe.db.exists("Warehouse", repair_bench):
			repair_bench = self._get_back_stock_wh()

		sn = self._create_serial_no(item_code, repair_bench)
		se_in = repair_in(item_code, repair_bench, serial_no=sn)
		self.assertTrue(se_in.name)

	def test_09_audit_log_written(self):
		from zevar_core.services.inventory_events import _log_inventory_event

		before = frappe.db.count("POS Audit Log")
		_log_inventory_event("test_event", "Test", "REF-001", "Test details")
		after = frappe.db.count("POS Audit Log")
		self.assertEqual(after, before + 1)

	def test_10_serial_last_seen_updated(self):
		from zevar_core.services.inventory_events import _update_serial_last_seen

		item_code = self._create_test_item()
		back_stock = self._get_back_stock_wh()
		sn = self._create_serial_no(item_code, back_stock)

		_update_serial_last_seen(sn)
		last_seen = frappe.db.get_value("Serial No", sn, "custom_last_seen_at")
		self.assertIsNotNone(last_seen)
