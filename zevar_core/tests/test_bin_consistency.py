import frappe
from frappe.tests.utils import FrappeTestCase


class TestBinConsistency(FrappeTestCase):
	def test_no_direct_bin_mutation_in_inventory_api(self):
		import inspect

		from zevar_core.api import inventory as inv_module

		source = inspect.getsource(inv_module)
		forbidden_patterns = [
			'frappe.db.set_value("Bin"',
			"frappe.db.set_value('Bin'",
			"frappe.db.sql.*UPDATE.*tabBin",
		]
		import re

		for pattern in forbidden_patterns:
			matches = re.findall(pattern, source, re.IGNORECASE)
			self.assertEqual(
				len(matches),
				0,
				f"Forbidden pattern found in inventory API: {pattern}",
			)

	def test_no_direct_bin_mutation_in_inventory_events(self):
		import inspect

		from zevar_core.services import inventory_events as events_module

		source = inspect.getsource(events_module)
		forbidden_patterns = [
			'frappe.db.set_value("Bin"',
			"frappe.db.set_value('Bin'",
		]
		import re

		for pattern in forbidden_patterns:
			matches = re.findall(pattern, source, re.IGNORECASE)
			self.assertEqual(
				len(matches),
				0,
				f"Forbidden pattern found in inventory events service: {pattern}",
			)

	def test_no_direct_bin_mutation_in_stock_reservation(self):
		import inspect

		from zevar_core.unified_retail_management_system.doctype.stock_reservation import (
			stock_reservation as sr_module,
		)

		source = inspect.getsource(sr_module)
		forbidden_patterns = [
			'frappe.db.set_value("Bin"',
			"frappe.db.set_value('Bin'",
		]
		import re

		for pattern in forbidden_patterns:
			matches = re.findall(pattern, source, re.IGNORECASE)
			self.assertEqual(
				len(matches),
				0,
				f"Forbidden pattern found in Stock Reservation controller: {pattern}",
			)

	def test_bin_matches_serial_count(self):
		warehouses = frappe.get_all(
			"Warehouse",
			filters={
				"is_group": 0,
				"company": frappe.defaults.get_global_default("company") or "Zevar Jewelers",
			},
			pluck="name",
			limit=50,
		)
		for wh in warehouses:
			bin_items = frappe.get_all(
				"Bin",
				filters={"warehouse": wh, "actual_qty": [">", 0]},
				fields=["item_code", "actual_qty"],
			)
			for b in bin_items:
				serial_count = frappe.db.count(
					"Serial No",
					filters={"item_code": b.item_code, "warehouse": wh},
				)
				item_has_serial = frappe.db.get_value("Item", b.item_code, "has_serial_no")
				if item_has_serial:
					self.assertEqual(
						b.actual_qty,
						serial_count,
						f"Bin qty mismatch for {b.item_code} in {wh}: bin={b.actual_qty}, serials={serial_count}",
					)


def flt(val):
	try:
		return float(val or 0)
	except (ValueError, TypeError):
		return 0.0
