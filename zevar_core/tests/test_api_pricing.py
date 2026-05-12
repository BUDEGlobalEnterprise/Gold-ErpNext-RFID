# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Pricing API (pricing.py)
Covers: get_item_price, get_live_metal_rates, get_live_rate_history, refresh_gold_rates

Run with: bench run-tests --app zevar_core --test test_api_pricing
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.tests.utils import ensure_item, ensure_item_group


class TestGetItemPrice(FrappeTestCase):
	"""Test get_item_price endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.item_code = ensure_item("PRICE-TEST-001", "Price Test Item", rate=999.99)

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_item_price_returns_dict(self):
		"""Should return price details dict"""
		from zevar_core.api.pricing import get_item_price

		result = get_item_price(self.item_code)
		self.assertIsInstance(result, dict)
		self.assertIn("item_code", result)
		self.assertIn("final_price", result)
		self.assertIn("price_source", result)
		self.assertEqual(result["item_code"], self.item_code)

	def test_get_item_price_nonexistent_raises(self):
		"""Should raise for nonexistent item"""
		from zevar_core.api.pricing import get_item_price

		with self.assertRaises(frappe.DoesNotExistError):
			get_item_price("NONEXISTENT-PRICE-99999")


class TestGetLiveMetalRates(FrappeTestCase):
	"""Test get_live_metal_rates endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_rates_returns_dict(self):
		"""Should return rates dict"""
		from zevar_core.api.pricing import get_live_metal_rates

		result = get_live_metal_rates()
		self.assertIsInstance(result, dict)
		self.assertIn("success", result)
		self.assertIn("rates", result)

	def test_rates_has_metadata(self):
		"""Should include metadata"""
		from zevar_core.api.pricing import get_live_metal_rates

		result = get_live_metal_rates()
		self.assertIn("source", result)
		self.assertIn("is_stale", result)


class TestGetLiveRateHistory(FrappeTestCase):
	"""Test get_live_rate_history endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_history_returns_dict(self):
		"""Should return history dict"""
		from zevar_core.api.pricing import get_live_rate_history

		result = get_live_rate_history(metal="Yellow Gold", days=7)
		self.assertIsInstance(result, dict)
		self.assertIn("success", result)
		self.assertIn("series", result)
		self.assertEqual(result["metal"], "Yellow Gold")
		self.assertEqual(result["days"], 7)


class TestRefreshGoldRates(FrappeTestCase):
	"""Test refresh_gold_rates endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_refresh_returns_result(self):
		"""Should return success or failure"""
		from zevar_core.api.pricing import refresh_gold_rates

		result = refresh_gold_rates()
		self.assertIsInstance(result, dict)
		self.assertIn("success", result)
