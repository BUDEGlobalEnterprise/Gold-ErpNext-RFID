import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt


class TestDamageAndFound(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
		cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr") or "Z"

		from zevar_core.patches.v1_1.seed_warehouse_zones import execute as seed_warehouses

		seed_warehouses()

	def _create_test_item(self):
		code = f"TEST-DMG-{frappe.generate_hash(length=6)}"
		if not frappe.db.exists("Item", code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": code,
					"item_name": f"Test Damage Item {code}",
					"item_group": "All Item Groups",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"has_serial_no": 1,
				}
			).insert(ignore_permissions=True)
		return code

	def _create_serial_no(self, item_code, warehouse):
		sn = f"SN-DMG-{frappe.generate_hash(length=8)}"
		if not frappe.db.exists("Serial No", sn):
			frappe.get_doc(
				{
					"doctype": "Serial No",
					"serial_no": sn,
					"item_code": item_code,
					"warehouse": warehouse,
					"company": self.company,
				}
			).insert(ignore_permissions=True)
		return sn

	def _get_showcase_wh(self):
		wh = f"Showcase NY-01 - {self.abbr}"
		return wh if frappe.db.exists("Warehouse", wh) else f"Stores - {self.abbr}"

	def _get_shrinkage_wh(self):
		wh = f"Shrinkage NY-01 - {self.abbr}"
		return wh if frappe.db.exists("Warehouse", wh) else f"Stores - {self.abbr}"

	def test_damage_write_off_moves_to_shrinkage(self):
		from zevar_core.api.inventory import do_damage_write_off

		item_code = self._create_test_item()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, showcase)

		result = do_damage_write_off(serial_no=sn, reason="Broken clasp")
		self.assertTrue(result["success"])
		self.assertTrue(result["stock_entry"])

		sn_wh = frappe.db.get_value("Serial No", sn, "warehouse")
		self.assertIn("Shrinkage", sn_wh or "")

	def test_recover_found_piece(self):
		from zevar_core.api.inventory import do_recover_found_piece
		from zevar_core.services.inventory_events import material_issue

		item_code = self._create_test_item()
		shrinkage = self._get_shrinkage_wh()
		sn = self._create_serial_no(item_code, shrinkage)

		result = do_recover_found_piece(serial_no=sn, original_shrinkage_ref="SE-SHRINK-001")
		self.assertTrue(result["success"])

		audit_logs = frappe.get_all(
			"POS Audit Log",
			filters={"event_type": "piece_recovered", "reference_document": result["stock_entry"]},
		)
		self.assertTrue(len(audit_logs) > 0)

	def test_net_zero_after_damage_and_recovery(self):
		from zevar_core.services.inventory_events import damage_write_off, recover_found_piece

		item_code = self._create_test_item()
		showcase = self._get_showcase_wh()
		shrinkage = self._get_shrinkage_wh()
		sn = self._create_serial_no(item_code, showcase)

		damage_write_off(sn, item_code, showcase, shrinkage, reason="Test")
		recover_found_piece(sn, item_code, showcase, "SHRINK-REF")

		sles = frappe.get_all(
			"Stock Ledger Entry",
			filters={"serial_no": ["like", f"%{sn}%"], "item_code": item_code},
			fields=["actual_qty"],
		)
		net = sum(flt(sle.actual_qty) for sle in sles)
		self.assertEqual(net, 0)
