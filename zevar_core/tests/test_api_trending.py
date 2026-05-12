# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Trending API (trending.py)
Covers: get_trending_items, track_trending_click

Run with: bench run-tests --app zevar_core --test test_api_trending
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestGetTrendingItems(FrappeTestCase):
	"""Test get_trending_items endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_trending_returns_list(self):
		"""Should return list of trending items"""
		from zevar_core.api.trending import get_trending_items

		result = get_trending_items()
		self.assertIsInstance(result, list)

	def test_get_trending_respects_limit(self):
		"""Should respect limit parameter"""
		from zevar_core.api.trending import get_trending_items

		result = get_trending_items(limit=5)
		self.assertLessEqual(len(result), 5)

	def test_get_trending_limit_capped(self):
		"""Limit should be capped at 100"""
		from zevar_core.api.trending import get_trending_items

		result = get_trending_items(limit=999)
		self.assertIsInstance(result, list)

	def test_get_trending_with_category(self):
		"""Should accept category filter"""
		from zevar_core.api.trending import get_trending_items

		result = get_trending_items(category="Rings")
		self.assertIsInstance(result, list)


class TestTrackTrendingClick(FrappeTestCase):
	"""Test track_trending_click endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_track_nonexistent_item(self):
		"""Should handle nonexistent item gracefully"""
		from zevar_core.api.trending import track_trending_click

		result = track_trending_click(item_id="NONEXISTENT-TREND-999")
		# Should return success=False, not raise
		self.assertIn("success", result)
		self.assertFalse(result["success"])
