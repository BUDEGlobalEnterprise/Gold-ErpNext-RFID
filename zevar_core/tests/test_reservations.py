import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime


class TestReservations(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_global_default("company") or "Zevar Jewelers"
		cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr") or "Z"

		from zevar_core.patches.v1_1.seed_warehouse_zones import execute as seed_warehouses

		seed_warehouses()

	def _create_test_item(self):
		code = f"TEST-RES-{frappe.generate_hash(length=6)}"
		if not frappe.db.exists("Item", code):
			item = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": code,
					"item_name": f"Test Res Item {code}",
					"item_group": "All Item Groups",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"has_serial_no": 1,
				}
			)
			item.insert(ignore_permissions=True)
		return code

	def _create_customer(self):
		name = f"CUST-RES-{frappe.generate_hash(length=6)}"
		if not frappe.db.exists("Customer", name):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": name,
					"customer_group": "Individual",
					"territory": "All Territories",
				}
			).insert(ignore_permissions=True)
		return name

	def _create_serial_no(self, item_code, warehouse):
		sn = f"SN-RES-{frappe.generate_hash(length=8)}".upper()
		from zevar_core.services.inventory_events import material_receipt

		material_receipt(
			item_code=item_code,
			to_warehouse=warehouse,
			qty=1,
			serial_no=sn,
			valuation_rate=100.0,
		)
		return sn

	def _get_showcase_wh(self):
		wh = f"Showcase NY-01 - {self.abbr}"
		return wh if frappe.db.exists("Warehouse", wh) else f"Stores - {self.abbr}"

	def test_create_and_cancel_reservation(self):
		from zevar_core.api.inventory import release_reservation, reserve_for_customer

		item_code = self._create_test_item()
		customer = self._create_customer()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, showcase)

		result = reserve_for_customer(
			serial_no=sn,
			customer=customer,
			hold_until=add_to_date(now_datetime(), hours=48),
		)
		self.assertTrue(result["success"])
		res_name = result["reservation"]
		self.assertTrue(frappe.db.exists("Stock Reservation", res_name))

		res = frappe.get_doc("Stock Reservation", res_name)
		self.assertEqual(res.status, "Active")

		cancel_result = release_reservation(reservation_name=res_name)
		self.assertTrue(cancel_result["success"])

	def test_expire_stale_reservations(self):
		from zevar_core.api.inventory import reserve_for_customer
		from zevar_core.tasks import expire_stale_reservations

		item_code = self._create_test_item()
		customer = self._create_customer()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, showcase)

		result = reserve_for_customer(
			serial_no=sn,
			customer=customer,
			hold_until=add_to_date(now_datetime(), hours=-1),
		)
		self.assertTrue(result["success"])

		expire_stale_reservations()

		res = frappe.get_doc("Stock Reservation", result["reservation"])
		self.assertIn(res.status, ["Cancelled", "Expired"])

	def test_double_reservation_rejected(self):
		from zevar_core.api.inventory import reserve_for_customer

		item_code = self._create_test_item()
		customer = self._create_customer()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, showcase)

		result1 = reserve_for_customer(
			serial_no=sn,
			customer=customer,
			hold_until=add_to_date(now_datetime(), hours=48),
		)
		self.assertTrue(result1["success"])

		with self.assertRaises(frappe.exceptions.ValidationError):
			reserve_for_customer(
				serial_no=sn,
				customer=customer,
				hold_until=add_to_date(now_datetime(), hours=48),
			)

	def test_held_cart_reserves_and_releases_stock(self):
		from zevar_core.api.pos import hold_cart, recall_cart

		item_code = self._create_test_item()
		customer = self._create_customer()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, showcase)

		items = [{"item_code": item_code, "qty": 1, "rate": 100, "amount": 100, "serial_no": sn}]

		# 1. Hold cart should reserve serial number
		hold_res = hold_cart(items=frappe.as_json(items), customer=customer, warehouse=showcase)
		self.assertTrue(hold_res["success"])
		cart_id = hold_res["cart_id"]

		# Check that Stock Reservation is active and serial number is reserved
		res_exists = frappe.db.exists("Stock Reservation", {"serial_no": sn, "status": "Active"})
		self.assertTrue(res_exists)

		# 2. Recall cart should cancel stock reservation
		recall_res = recall_cart(cart_id=cart_id)
		self.assertTrue(recall_res["success"])

		res_doc = frappe.get_doc("Stock Reservation", res_exists)
		self.assertEqual(res_doc.status, "Cancelled")

	def test_held_cart_discard_releases_stock(self):
		from zevar_core.api.pos import discard_held_cart, hold_cart

		item_code = self._create_test_item()
		customer = self._create_customer()
		showcase = self._get_showcase_wh()
		sn = self._create_serial_no(item_code, showcase)

		items = [{"item_code": item_code, "qty": 1, "rate": 100, "amount": 100, "serial_no": sn}]

		hold_res = hold_cart(items=frappe.as_json(items), customer=customer, warehouse=showcase)
		cart_id = hold_res["cart_id"]
		res_exists = frappe.db.exists("Stock Reservation", {"serial_no": sn, "status": "Active"})
		self.assertTrue(res_exists)

		discard_res = discard_held_cart(cart_id=cart_id)
		self.assertTrue(discard_res["success"])

		res_doc = frappe.get_doc("Stock Reservation", res_exists)
		self.assertEqual(res_doc.status, "Cancelled")
