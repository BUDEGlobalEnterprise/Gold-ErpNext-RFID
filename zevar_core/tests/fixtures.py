"""
Test fixtures for Zevar Core

Creates minimal test data needed for tests to

Run with: bench --site zevar.localhost console
>>> from zevar_core.tests.fixtures import create_test_fixtures
>>> create_test_fixtures()
>>> frappe.db.commit()  # nosemgrep
"""

import frappe


def create_test_fixtures():
	"""Create test fixtures for Zevar Core tests"""

	# 1. Create test warehouse first (needed by other records)
	warehouse_name = "Test POS Warehouse - T"
	if not frappe.db.exists("Warehouse", warehouse_name):
		try:
			wh = frappe.new_doc("Warehouse")
			wh.warehouse_name = "Test POS Warehouse"
			wh.company = "_Test Company"
			wh.insert(ignore_permissions=True, ignore_mandatory=True)
		except Exception:
			pass  # Warehouse might already exist with different name format

	# 2. Create test items
	test_items = [
		{"item_code": "TEST-ITEM-001", "item_name": "Test Gold Ring", "standard_rate": 1000},
		{"item_code": "TEST-ITEM-002", "item_name": "Test Silver Necklace", "standard_rate": 500},
		{"item_code": "TEST-ITEM-003", "item_name": "Test Diamond Earrings", "standard_rate": 2000},
		{"item_code": "LAYAWAY-TEST-001", "item_name": "Layaway Test Item", "standard_rate": 1000},
		{"item_code": "RETURN-TEST-001", "item_name": "Return Test Item", "standard_rate": 100},
		{"item_code": "HISTORY-TEST-001", "item_name": "History Test Item", "standard_rate": 100},
	]

	for item_data in test_items:
		if not frappe.db.exists("Item", item_data["item_code"]):
			try:
				item = frappe.new_doc("Item")
				item.item_code = item_data["item_code"]
				item.item_name = item_data["item_name"]
				item.item_group = "Products"
				item.stock_uom = "Nos"
				item.is_stock_item = 0  # Non-stock item to avoid stock entry issues
				item.standard_rate = item_data["standard_rate"]
				item.insert(ignore_permissions=True, ignore_mandatory=True)
			except Exception:
				pass

	# 3. Create test customer
	if not frappe.db.exists("Customer", "Test Customer"):
		try:
			customer = frappe.new_doc("Customer")
			customer.customer_name = "Test Customer"
			customer.customer_type = "Individual"
			customer.insert(ignore_permissions=True, ignore_mandatory=True)
		except Exception:
			pass

	# 4. Create test POS Profile (warehouse must exist)
	if not frappe.db.exists("POS Profile", "Test POS Profile"):
		try:
			profile = frappe.new_doc("POS Profile")
			profile.name = "Test POS Profile"
			profile.company = "_Test Company"
			profile.currency = "USD"
			profile.insert(ignore_permissions=True, ignore_mandatory=True)
		except Exception:
			pass

	return True
