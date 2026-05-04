from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.constants import TROY_OZ_TO_GRAMS


class TestGoldRateFetch(FrappeTestCase):
	def setUp(self):
		self.ensure_test_metal_and_purity()
		self.cleanup_rate_logs()

	def tearDown(self):
		self.cleanup_rate_logs()

	def ensure_test_metal_and_purity(self):
		metals = ["Yellow Gold", "Silver"]
		for metal in metals:
			if not frappe.db.exists("Zevar Metal", metal):
				frappe.get_doc({"doctype": "Zevar Metal", "__newname": metal}).insert(ignore_permissions=True)

		purities = {
			"24Kt": 0.999,
			"22Kt": 0.916,
			"18Kt": 0.750,
			"14Kt": 0.585,
			"10Kt": 0.417,
			"999 Fine": 0.999,
			"925 Sterling": 0.925,
		}
		for name, content in purities.items():
			if not frappe.db.exists("Zevar Purity", name):
				frappe.get_doc(
					{"doctype": "Zevar Purity", "__newname": name, "fine_metal_content": content}
				).insert(ignore_permissions=True)
		frappe.db.commit()  # nosemgrep

	def cleanup_rate_logs(self):
		for name in frappe.get_all(
			"Gold Rate Log",
			filters={
				"source": ["in", ["test-mock", "gold-api.com", "metals.live", "goldprice.org", "fallback"]]
			},
			pluck="name",
		):
			frappe.delete_doc("Gold Rate Log", name, ignore_permissions=True, force=True)

		# Disable custom api endpoint so tests hit the fallbacks properly
		settings = frappe.get_doc("Gold Settings", "Gold Settings")
		settings.api_endpoint = ""
		settings.save(ignore_permissions=True)

	def _mock_gold_api_response(self, gold_price, silver_price):
		gold_mock = MagicMock()
		gold_mock.json.return_value = {"price": gold_price, "symbol": "XAU"}
		gold_mock.raise_for_status = MagicMock()

		silver_mock = MagicMock()
		silver_mock.json.return_value = {"price": silver_price, "symbol": "XAG"}
		silver_mock.raise_for_status = MagicMock()

		def side_effect(url, **kwargs):
			if "XAU" in url:
				return gold_mock
			if "XAG" in url:
				return silver_mock
			if "metals.live" in url:
				raise Exception("not used")
			if "goldprice" in url:
				raise Exception("not used")
			return gold_mock

		return side_effect

	def _mock_metals_live_response(self, gold_price, silver_price):
		mock_response = MagicMock()
		mock_response.json.return_value = [
			{"metal": "gold", "price": gold_price},
			{"metal": "silver", "price": silver_price},
		]
		mock_response.raise_for_status = MagicMock()

		def side_effect(url, **kwargs):
			if "gold-api" in url:
				raise Exception("gold-api down")
			return mock_response

		return side_effect

	def _mock_goldprice_response(self, gold_price, silver_price):
		mock_response = MagicMock()
		mock_response.json.return_value = {"items": [{"xauPrice": gold_price, "xagPrice": silver_price}]}
		mock_response.raise_for_status = MagicMock()

		def side_effect(url, **kwargs):
			if "gold-api" in url or "metals.live" in url:
				raise Exception("down")
			return mock_response

		return side_effect

	def _mock_all_down(self):
		def side_effect(url, **kwargs):
			raise Exception("Network error")

		return side_effect

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_from_gold_api_primary(self, mock_get):
		from zevar_core.tasks import fetch_live_metal_rates

		mock_get.side_effect = self._mock_gold_api_response(4712.60, 75.89)
		fetch_live_metal_rates()

		gold_22kt_rate = 4712.60 / TROY_OZ_TO_GRAMS * 0.916
		gold_entry = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["rate_per_gram", "source"],
			order_by="creation desc",
			limit=1,
		)
		self.assertTrue(len(gold_entry) > 0)
		self.assertAlmostEqual(float(gold_entry[0].rate_per_gram), round(gold_22kt_rate, 2), places=1)
		self.assertEqual(gold_entry[0].source, "gold-api.com")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_fallback_to_metals_live(self, mock_get):
		from zevar_core.tasks import fetch_live_metal_rates

		mock_get.side_effect = self._mock_metals_live_response(2600.0, 30.0)
		fetch_live_metal_rates()

		gold_entry = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["source"],
			order_by="creation desc",
			limit=1,
		)
		self.assertTrue(len(gold_entry) > 0)
		self.assertEqual(gold_entry[0].source, "metals.live")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_fallback_to_goldprice_org(self, mock_get):
		from zevar_core.tasks import fetch_live_metal_rates

		mock_get.side_effect = self._mock_goldprice_response(2600.0, 30.0)
		fetch_live_metal_rates()

		gold_entry = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["source"],
			order_by="creation desc",
			limit=1,
		)
		self.assertTrue(len(gold_entry) > 0)
		self.assertEqual(gold_entry[0].source, "goldprice.org")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_rates_creates_gold_purity_entries(self, mock_get):
		mock_get.side_effect = self._mock_gold_api_response(2600.0, 30.0)

		from zevar_core.tasks import fetch_live_metal_rates

		fetch_live_metal_rates()

		canonical_purities = ["24Kt", "22Kt", "18Kt", "14Kt", "10Kt"]
		for purity in canonical_purities:
			exists = frappe.db.exists("Gold Rate Log", {"metal": "Yellow Gold", "purity": purity})
			self.assertTrue(exists, f"Gold Rate Log missing for Yellow Gold {purity}")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_rates_creates_silver_purity_entries(self, mock_get):
		mock_get.side_effect = self._mock_gold_api_response(2600.0, 30.0)

		from zevar_core.tasks import fetch_live_metal_rates

		fetch_live_metal_rates()

		silver_purities = ["999 Fine", "925 Sterling"]
		for purity in silver_purities:
			exists = frappe.db.exists("Gold Rate Log", {"metal": "Silver", "purity": purity})
			self.assertTrue(exists, f"Gold Rate Log missing for Silver {purity}")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_rates_fallback_on_all_errors(self, mock_get):
		mock_get.side_effect = self._mock_all_down()

		from zevar_core.tasks import fetch_live_metal_rates

		fetch_live_metal_rates()

		fallback_gold = 4400.0 / TROY_OZ_TO_GRAMS * 0.916
		gold_entry = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["rate_per_gram", "source"],
			order_by="creation desc",
			limit=1,
		)
		self.assertTrue(len(gold_entry) > 0)
		self.assertAlmostEqual(float(gold_entry[0].rate_per_gram), round(fallback_gold, 2), places=1)
		self.assertEqual(gold_entry[0].source, "fallback")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_rates_updates_existing_entry(self, mock_get):
		from zevar_core.tasks import fetch_live_metal_rates

		mock_get.side_effect = self._mock_gold_api_response(2600.0, 30.0)
		fetch_live_metal_rates()

		first_rate = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["rate_per_gram"],
			order_by="creation desc",
			limit=1,
		)[0].rate_per_gram

		mock_get.side_effect = self._mock_gold_api_response(2700.0, 31.0)
		fetch_live_metal_rates()

		second_rate = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["rate_per_gram"],
			order_by="creation desc",
			limit=1,
		)[0].rate_per_gram

		self.assertNotEqual(float(first_rate), float(second_rate))

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_rates_sends_correct_user_agent(self, mock_get):
		mock_get.side_effect = self._mock_gold_api_response(2600.0, 30.0)

		from zevar_core.tasks import fetch_live_metal_rates

		fetch_live_metal_rates()

		call_args = mock_get.call_args
		self.assertIn("headers", call_args.kwargs or {})
		headers = (call_args.kwargs or {}).get("headers", {})
		self.assertEqual(headers.get("User-Agent"), "Zevar-POS/1.0 (Zevar Jewelers; gold-rate-sync)")

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_rates_purity_calculation_accuracy(self, mock_get):
		mock_get.side_effect = self._mock_gold_api_response(3103.5, 31.1035)

		from zevar_core.tasks import fetch_live_metal_rates

		fetch_live_metal_rates()

		expected_22kt = round(3103.5 / TROY_OZ_TO_GRAMS * 0.916, 2)
		expected_18kt = round(3103.5 / TROY_OZ_TO_GRAMS * 0.750, 2)
		expected_14kt = round(3103.5 / TROY_OZ_TO_GRAMS * 0.585, 2)

		rate_22kt = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			fields=["rate_per_gram"],
			order_by="creation desc",
			limit=1,
		)[0].rate_per_gram
		self.assertEqual(float(rate_22kt), expected_22kt)

		rate_18kt = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "18Kt"},
			fields=["rate_per_gram"],
			order_by="creation desc",
			limit=1,
		)[0].rate_per_gram
		self.assertEqual(float(rate_18kt), expected_18kt)

		rate_14kt = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "14Kt"},
			fields=["rate_per_gram"],
			order_by="creation desc",
			limit=1,
		)[0].rate_per_gram
		self.assertEqual(float(rate_14kt), expected_14kt)

		self.assertGreater(float(rate_22kt), float(rate_18kt))
		self.assertGreater(float(rate_18kt), float(rate_14kt))

	def test_troy_oz_to_grams_constant(self):
		self.assertAlmostEqual(TROY_OZ_TO_GRAMS, 31.1035, places=4)

	@patch("zevar_core.tasks.requests.get")
	def test_fetch_live_gold_rate_alias(self, mock_get):
		mock_get.side_effect = self._mock_gold_api_response(2600.0, 30.0)

		from zevar_core.tasks import fetch_live_gold_rate

		fetch_live_gold_rate()

		entry = frappe.get_all(
			"Gold Rate Log",
			filters={"metal": "Yellow Gold", "purity": "22Kt"},
			pluck="name",
			limit=1,
		)
		self.assertTrue(len(entry) > 0)
