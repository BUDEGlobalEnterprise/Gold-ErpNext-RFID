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
