import frappe
from frappe.tests.utils import FrappeTestCase


class TestInterStoreTransfer(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
		cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr") or "Z"

		from zevar_core.patches.v1_1.seed_warehouse_zones import execute as seed_warehouses
		seed_warehouses()

	def _create_test_item(self):
		code = f"TEST-XFR-{frappe.generate_hash(length=6)}"
		if not frappe.db.exists("Item", code):
			frappe.get_doc({
				"doctype": "Item",
				"item_code": code,
				"item_name": f"Test Transfer Item {code}",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"has_serial_no": 1,
			}).insert(ignore_permissions=True)
		return code

	def _create_serial_no(self, item_code, warehouse):
		sn = f"SN-XFR-{frappe.generate_hash(length=8)}"
		if not frappe.db.exists("Serial No", sn):
			frappe.get_doc({
				"doctype": "Serial No",
				"serial_no": sn,
				"item_code": item_code,
				"warehouse": warehouse,
				"company": self.company,
			}).insert(ignore_permissions=True)
		return sn

	def test_dispatch_creates_transit_entries(self):
		from zevar_core.services.inventory_events import dispatch_inter_store_transfer

		item_code = self._create_test_item()
		back_stock = f"Back Stock NY-01 - {self.abbr}"
		transit_out = f"Transit Out NY-01 - {self.abbr}"

		if not frappe.db.exists("Warehouse", back_stock):
			self.skipTest("Warehouse not seeded")
			return

		serials = [self._create_serial_no(item_code, back_stock) for _ in range(3)]
		item_codes = [item_code] * 3

		entries = dispatch_inter_store_transfer(serials, item_codes, back_stock, transit_out)
		self.assertEqual(len(entries), 3)

		for sn in serials:
			sn_wh = frappe.db.get_value("Serial No", sn, "warehouse")
			self.assertEqual(sn_wh, transit_out)

	def test_receive_transfers_serials(self):
		from zevar_core.services.inventory_events import receive_inter_store_transfer

		item_code = self._create_test_item()
		transit_out = f"Transit Out NY-01 - {self.abbr}"
		dest_back_stock = f"Back Stock Miami-01 - {self.abbr}"

		if not frappe.db.exists("Warehouse", transit_out):
			self.skipTest("Warehouse not seeded")
			return

		serials = [self._create_serial_no(item_code, transit_out) for _ in range(3)]
		item_codes = [item_code] * 3

		entries = receive_inter_store_transfer(serials, item_codes, transit_out, dest_back_stock)
		self.assertEqual(len(entries), 3)

	def test_variance_detected_on_missing_serial(self):
		from zevar_core.api.inventory import receive_inter_store_transfer as api_receive

		result = api_receive(
			transfer_name=None,
			scanned_serials=["NONEXISTENT-SN-001"],
		)
		self.assertEqual(result["variance"], 1)
