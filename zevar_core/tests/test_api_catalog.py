# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Catalog API (catalog.py)
Covers: get_pos_items, get_display_cases, get_catalog_filters, get_item_details

Run with: bench run-tests --app zevar_core --test test_api_catalog
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.tests.utils import ensure_item, ensure_item_group


class TestGetPOSItems(FrappeTestCase):
	"""Test get_pos_items endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_pos_items_returns_list(self):
		"""Should return list of items"""
		from zevar_core.api.catalog import get_pos_items

		result = get_pos_items(start=0, page_length=20)
		self.assertIsInstance(result, list)

	def test_get_pos_items_with_search(self):
		"""Should filter by search term"""
		from zevar_core.api.catalog import get_pos_items

		result = get_pos_items(search_term="Gold Ring")
		self.assertIsInstance(result, list)

	def test_get_pos_items_pagination(self):
		"""Should respect pagination params"""
		from zevar_core.api.catalog import get_pos_items

		result = get_pos_items(start=0, page_length=5)
		self.assertIsInstance(result, list)
		self.assertLessEqual(len(result), 5)

	def test_sanitize_search_strips_dangerous_chars(self):
		"""Should sanitize search input"""
		from zevar_core.api.catalog import _sanitize_search

		self.assertEqual(_sanitize_search("test%;DROP TABLE--"), "testDROP TABLE--")
		self.assertEqual(_sanitize_search(""), "")
		self.assertEqual(_sanitize_search(None), None)

	def test_sanitize_search_length_limit(self):
		"""Should truncate to 100 chars"""
		from zevar_core.api.catalog import _sanitize_search

		long_string = "a" * 200
		result = _sanitize_search(long_string)
		self.assertLessEqual(len(result), 100)


class TestGetDisplayCases(FrappeTestCase):
	"""Test get_display_cases endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_display_cases_returns_list(self):
		"""Should return list of display cases"""
		from zevar_core.api.catalog import get_display_cases

		result = get_display_cases()
		self.assertIsInstance(result, list)


class TestGetCatalogFilters(FrappeTestCase):
	"""Test get_catalog_filters endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_catalog_filters_returns_dict(self):
		"""Should return filter options"""
		from zevar_core.api.catalog import get_catalog_filters

		result = get_catalog_filters()
		self.assertIsInstance(result, dict)
		self.assertIn("display_cases", result)
		self.assertIn("jewelry_types", result)
		self.assertIn("metals", result)
		self.assertIn("purities", result)
		self.assertIn("gemstones", result)


class TestGetItemDetails(FrappeTestCase):
	"""Test get_item_details endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_item_details_nonexistent_raises(self):
		"""Should raise for nonexistent item"""
		from zevar_core.api.catalog import get_item_details

		with self.assertRaises(frappe.DoesNotExistError):
			get_item_details("NONEXISTENT-ITEM-99999")


class TestGetPOSItemsOmniSearch(FrappeTestCase):
	"""Verify omni-search across item_code, item_name, vendor_sku, and Display Case.

	The catalog must let a cashier punch in any of the printed identifiers on the
	tag/case/POS screen and find the right item — this regression-tests that.
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")

		# Three items, each uniquely identifiable by exactly one search axis so
		# we can prove each axis is wired up independently.
		cls.item_code = "ZEVAR-OMNI-CODE-001"
		ensure_item(cls.item_code, "Generic Pendant Alpha")

		cls.item_by_name = ensure_item("ZEVAR-OMNI-NAMEONLY-001", "Unicorn Sparkle Choker XYZ")
		cls.item_by_vsku_code = "ZEVAR-OMNI-VSKU-001"
		ensure_item(cls.item_by_vsku_code, "Plain Vendor Item")
		cls.unique_vendor_sku = "VND-OMNI-SKU-9999"
		# custom_vendor_sku is added via fixtures; if missing, set_value still
		# stores the value because Frappe stores non-stale custom fields via the
		# generic value path.
		try:
			frappe.db.set_value(
				"Item", cls.item_by_vsku_code, "custom_vendor_sku", cls.unique_vendor_sku
			)
		except Exception:  # custom field not present on this site
			cls.unique_vendor_sku = None
		frappe.db.commit()

	def _search(self, term):
		from zevar_core.api.catalog import get_pos_items

		return get_pos_items(search_term=term, page_length=50)

	def test_search_by_item_code_finds_item(self):
		"""Searching by exact item_code returns the matching item."""
		results = self._search(self.item_code)
		codes = {r["item_code"] for r in results}
		self.assertIn(self.item_code, codes)

	def test_search_by_item_name_substring_finds_item(self):
		"""Searching by a unique substring of item_name returns the item."""
		results = self._search("Unicorn Sparkle Choker")
		codes = {r["item_code"] for r in results}
		self.assertIn(self.item_by_name, codes)

	def test_search_by_vendor_sku_finds_item(self):
		"""Searching by custom_vendor_sku returns the item."""
		if not self.unique_vendor_sku:
			self.skipTest("custom_vendor_sku field not present on this site")
		results = self._search(self.unique_vendor_sku)
		codes = {r["item_code"] for r in results}
		self.assertIn(self.item_by_vsku_code, codes)

	def test_search_unknown_term_returns_empty(self):
		"""Searching for nonsense returns empty list, not all items."""
		results = self._search("THIS-TERM-MATCHES-NOTHING-zzz-12345")
		self.assertEqual(results, [])


class TestResolveDisplayCaseWarehouse(FrappeTestCase):
	"""Verify Display Case identifiers auto-scope the catalog to a warehouse."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")

		from zevar_core.tests.utils import ensure_warehouse

		cls.case_warehouse = ensure_warehouse("Zevar Test Case Warehouse")
		cls.case_code = "ZEVAR-OMNI-CASE-A1"
		cls.case_name = "Zevar Omni Test Case"

		if not frappe.db.exists("Display Case", cls.case_name):
			# Display Case requires a Store Location. Re-use any existing one
			# or create a minimal one for the test.
			store_loc = frappe.db.get_value("Store Location", {}, "name")
			if not store_loc:
				try:
					sl = frappe.new_doc("Store Location")
					sl.store_name = "Zevar Test Store"
					sl.insert(ignore_permissions=True, ignore_mandatory=True)
					store_loc = sl.name
				except Exception:
					store_loc = None

			doc = frappe.new_doc("Display Case")
			doc.case_name = cls.case_name
			doc.case_code = cls.case_code
			doc.warehouse = cls.case_warehouse
			doc.is_active = 1
			if store_loc:
				doc.store_location = store_loc
			doc.insert(ignore_permissions=True, ignore_mandatory=True)
			frappe.db.commit()

	def test_resolves_warehouse_by_case_code(self):
		from zevar_core.api.catalog import _resolve_display_case_warehouse

		self.assertEqual(_resolve_display_case_warehouse(self.case_code), self.case_warehouse)

	def test_resolves_warehouse_by_case_name(self):
		from zevar_core.api.catalog import _resolve_display_case_warehouse

		self.assertEqual(_resolve_display_case_warehouse(self.case_name), self.case_warehouse)

	def test_unknown_term_returns_none(self):
		from zevar_core.api.catalog import _resolve_display_case_warehouse

		self.assertIsNone(_resolve_display_case_warehouse("NO-SUCH-CASE-zzz"))
