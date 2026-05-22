"""
Tests for auto stock reduction detection and CLI stock management.
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, flt, now_datetime

from zevar_core.services.inventory_events import (
	_get_abbr,
	_get_company,
	_get_cost_center,
	material_issue,
	material_receipt,
	transfer_serial,
)
from zevar_core.services.stock_reduction import (
	detect_stock_reduction,
	get_recent_reductions,
)


class TestStockReductionDetection(FrappeTestCase):
	def setUp(self):
		self.item_code = "TEST-STOCK-RED-ITEM"
		self.warehouse = None
		self.serial_no = None

		if not frappe.db.exists("Item", self.item_code):
			doc = frappe.new_doc("Item")
			doc.item_code = self.item_code
			doc.item_name = "Test Stock Reduction Item"
			doc.item_group = "All Item Groups"
			doc.stock_uom = "Nos"
			doc.is_stock_item = 1
			doc.has_serial_no = 1
			doc.insert(ignore_permissions=True)

		abbr = _get_abbr()
		store_code = "NY-01"
		self.warehouse = f"Back Stock {store_code} - {abbr}"

		if not frappe.db.exists("Warehouse", self.warehouse):
			parent = f"{store_code} - {abbr}"
			if not frappe.db.exists("Warehouse", parent):
				frappe.get_doc(
					{
						"doctype": "Warehouse",
						"warehouse_name": store_code,
						"is_group": 1,
						"company": _get_company(),
					}
				).insert(ignore_permissions=True)
			frappe.get_doc(
				{
					"doctype": "Warehouse",
					"warehouse_name": f"Back Stock {store_code}",
					"parent_warehouse": parent,
					"company": _get_company(),
					"is_group": 0,
				}
			).insert(ignore_permissions=True)

	def _create_serial_no(self, item_code=None, warehouse=None):
		sn_name = frappe.generate_hash("SRN", 10).upper()
		return sn_name

	def _create_test_stock(self, qty=1):
		serials = []
		for _ in range(qty):
			sn = self._create_serial_no()
			serials.append(sn)
		material_receipt(
			self.item_code,
			self.warehouse,
			qty=qty,
			serial_no="\n".join(serials),
			valuation_rate=100.0,
		)
		return serials

	def test_detect_stock_reduction_with_serial_no(self):
		serials = self._create_test_stock(qty=1)

		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = frappe.db.get_value("Customer", {}, "name") or "Customer"
		invoice.update_stock = 1
		invoice.company = _get_company()

		if not frappe.db.exists("Customer", invoice.customer):
			cust = frappe.new_doc("Customer")
			cust.customer_name = invoice.customer
			cust.customer_group = "Individual"
			cust.territory = "All Territories"
			cust.insert(ignore_permissions=True)
			invoice.customer = cust.name

		invoice.append(
			"items",
			{
				"item_code": self.item_code,
				"qty": 1,
				"rate": 100,
				"warehouse": self.warehouse,
				"serial_no": serials[0],
			},
		)

		detect_stock_reduction(invoice, method="on_submit")

		logs = frappe.get_all(
			"POS Audit Log",
			filters={
				"event_type": "stock_auto_reduced",
				"reference_type": "Sales Invoice",
			},
			fields=["details"],
			order_by="creation desc",
			limit=1,
		)

		self.assertTrue(len(logs) > 0, "Expected at least one audit log entry")
		details = json.loads(logs[0].details) if isinstance(logs[0].details, str) else logs[0].details
		self.assertEqual(details.get("serial_no"), serials[0])
		self.assertEqual(details.get("item_code"), self.item_code)

	def test_detect_stock_reduction_skip_no_update_stock(self):
		invoice = frappe.new_doc("Sales Invoice")
		invoice.update_stock = 0

		detect_stock_reduction(invoice, method="on_submit")

		logs = frappe.get_all(
			"POS Audit Log",
			filters={"event_type": "stock_auto_reduced"},
		)
		for log in logs:
			self.assertNotEqual(log.reference_type, "Sales Invoice")

	def test_get_recent_reductions_api(self):
		result = get_recent_reductions(hours=24, limit=10)
		self.assertIn("success", result)
		self.assertTrue(result["success"])
		self.assertIn("reductions", result)


class TestStockCLICommands(FrappeTestCase):
	def setUp(self):
		self.item_code = "TEST-CLI-STOCK-ITEM"
		abbr = _get_abbr()
		store_code = "NY-01"
		self.warehouse = f"Back Stock {store_code} - {abbr}"

		if not frappe.db.exists("Item", self.item_code):
			doc = frappe.new_doc("Item")
			doc.item_code = self.item_code
			doc.item_name = "Test CLI Stock Item"
			doc.item_group = "All Item Groups"
			doc.stock_uom = "Nos"
			doc.is_stock_item = 1
			doc.insert(ignore_permissions=True)

		if not frappe.db.exists("Warehouse", self.warehouse):
			parent = f"{store_code} - {abbr}"
			if not frappe.db.exists("Warehouse", parent):
				frappe.get_doc(
					{
						"doctype": "Warehouse",
						"warehouse_name": store_code,
						"is_group": 1,
						"company": _get_company(),
					}
				).insert(ignore_permissions=True)
			frappe.get_doc(
				{
					"doctype": "Warehouse",
					"warehouse_name": f"Back Stock {store_code}",
					"parent_warehouse": parent,
					"company": _get_company(),
					"is_group": 0,
				}
			).insert(ignore_permissions=True)

		self.showcase_wh = f"Showcase {store_code} - {abbr}"
		if not frappe.db.exists("Warehouse", self.showcase_wh):
			parent = f"{store_code} - {abbr}"
			frappe.get_doc(
				{
					"doctype": "Warehouse",
					"warehouse_name": f"Showcase {store_code}",
					"parent_warehouse": parent,
					"company": _get_company(),
					"is_group": 0,
				}
			).insert(ignore_permissions=True)

	def test_add_stock_via_service(self):
		from zevar_core.services.inventory_events import material_receipt

		se = material_receipt(self.item_code, self.warehouse, qty=3)
		self.assertTrue(se.name)
		self.assertEqual(se.stock_entry_type, "Material Receipt")

		bin_qty = frappe.db.get_value(
			"Bin", {"item_code": self.item_code, "warehouse": self.warehouse}, "actual_qty"
		)
		self.assertGreaterEqual(flt(bin_qty), 3)

	def test_remove_stock_via_service(self):
		from zevar_core.services.inventory_events import material_receipt

		material_receipt(self.item_code, self.warehouse, qty=2)

		se = material_issue(self.item_code, self.warehouse, qty=1)
		self.assertTrue(se.name)
		self.assertEqual(se.stock_entry_type, "Material Issue")

	def test_move_stock_via_service(self):
		from zevar_core.services.inventory_events import material_receipt

		material_receipt(self.item_code, self.warehouse, qty=1)

		se = transfer_serial(None, self.item_code, self.warehouse, self.showcase_wh)
		self.assertTrue(se.name)
		self.assertEqual(se.stock_entry_type, "Material Transfer")

	def test_cli_lookup_function(self):
		from zevar_core.stock_cli import _do_lookup

		result = _do_lookup(self.item_code)
		self.assertTrue(result.get("found"))
		self.assertEqual(result.get("type"), "item")
		self.assertEqual(result.get("item_code"), self.item_code)

	def test_cli_lookup_not_found(self):
		from zevar_core.stock_cli import _do_lookup

		result = _do_lookup("NONEXISTENT-ITEM-CODE-12345")
		self.assertFalse(result.get("found"))

	def test_cli_action_logged(self):
		from zevar_core.stock_cli import _log_cli_action

		_log_cli_action("test_action", {"item": self.item_code, "test": True})

		log = frappe.get_all(
			"POS Audit Log",
			filters={"event_type": "stock_cli_adjustment", "details": ["like", "%test_action%"]},
			limit=1,
		)
		self.assertTrue(len(log) > 0)
