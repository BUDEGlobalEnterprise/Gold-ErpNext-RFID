"""Scheduled tasks for Zevar Core"""

import frappe
import requests

from zevar_core.constants import (
	GOLD_PURITY_RATES,
	SILVER_PURITY_RATES,
	TROY_OZ_TO_GRAMS,
)

GOLD_API_BASE = "https://api.gold-api.com/price"
METALS_LIVE_SPOT_URL = "https://api.metals.live/v1/spot"
GOLDPRICE_ORG_URL = "https://data-asg.goldprice.org/dbXRates/USD"

_UA = {"User-Agent": "Zevar-POS/1.0 (Zevar Jewelers; gold-rate-sync)"}


def _try_gold_api():
	"""Fetch spot prices from gold-api.com (free, no key, reliable).

	Returns (gold_per_oz, silver_per_oz) or None.
	"""
	gold_resp = requests.get(f"{GOLD_API_BASE}/XAU", headers=_UA, timeout=10)
	gold_resp.raise_for_status()
	gold_data = gold_resp.json()
	gold = gold_data.get("price")

	silver_resp = requests.get(f"{GOLD_API_BASE}/XAG", headers=_UA, timeout=10)
	silver_resp.raise_for_status()
	silver_data = silver_resp.json()
	silver = silver_data.get("price")

	if gold and silver:
		return float(gold), float(silver)
	return None


def _try_metals_live():
	"""Fetch spot prices from metals.live (free, no key).

	Returns (gold_per_oz, silver_per_oz) or None.
	"""
	resp = requests.get(METALS_LIVE_SPOT_URL, headers=_UA, timeout=10)
	resp.raise_for_status()
	data = resp.json()
	gold = silver = None
	for item in data:
		if item.get("metal") == "gold":
			gold = item.get("price")
		elif item.get("metal") == "silver":
			silver = item.get("price")
	if gold and silver:
		return float(gold), float(silver)
	return None


def _try_goldprice_org():
	"""Fetch spot prices from goldprice.org.

	Returns (gold_per_oz, silver_per_oz) or None.
	"""
	resp = requests.get(GOLDPRICE_ORG_URL, headers=_UA, timeout=10)
	resp.raise_for_status()
	data = resp.json()
	gold = data.get("items", [{}])[0].get("xauPrice")
	silver = data.get("items", [{}])[0].get("xagPrice")
	if gold and silver:
		return float(gold), float(silver)
	return None


_API_SOURCES = [
	("gold-api.com", _try_gold_api),
	("metals.live", _try_metals_live),
	("goldprice.org", _try_goldprice_org),
]


def fetch_live_metal_rates():
	"""
	Fetches live gold and silver rates from free APIs with automatic fallback.

	API priority:
	  1. gold-api.com (free, no key, most reliable)
	  2. metals.live (free, no key)
	  3. goldprice.org (original source)
	  4. Custom endpoint from Gold Settings (if configured)
	  5. Hardcoded fallback rates

	Stores rates under canonical Kt names (22Kt, 18Kt, etc.) only.
	Old K-form entries are cleaned up automatically.

	Returns:
		dict: Current rates with metals, purities, and metadata.
	"""
	rates = {"gold": {}, "silver": {}, "source": "live", "error": None}
	prices = None
	source_label = "gold-api.com"

	try:
		if frappe.db.exists("Gold Settings", "Gold Settings"):
			settings = frappe.get_single("Gold Settings")
			if settings.api_endpoint:
				resp = requests.get(settings.api_endpoint, headers=_UA, timeout=10)
				resp.raise_for_status()
				prices = _parse_custom_api(resp.json())
				source_label = "custom"

		if not prices:
			for name, fn in _API_SOURCES:
				try:
					prices = fn()
					if prices:
						source_label = name
						break
				except Exception:
					frappe.logger().info(f"{name} unreachable, trying next source")

		if prices:
			gold_per_gram = prices[0] / TROY_OZ_TO_GRAMS
			silver_per_gram = prices[1] / TROY_OZ_TO_GRAMS
			rates["source"] = source_label

			_update_all_rates(gold_per_gram, silver_per_gram, rates)

			frappe.db.commit()  # nosemgrep: frappe-semgrep-rules/rules.frappe-manual-commit
			_cleanup_legacy_k_entries()
			frappe.logger().info(
				f"Metal rates updated from {source_label}: Gold 22Kt=${gold_per_gram * 0.916:.2f}/g, Silver 925=${silver_per_gram * 0.925:.2f}/g"
			)
			return rates

	except Exception as e:
		frappe.logger().error(f"Metal rate fetch failed: {e!s}")

	rates["source"] = "fallback"
	rates["error"] = "All APIs unreachable"

	_update_all_rates(
		4400.0 / TROY_OZ_TO_GRAMS,
		33.0 / TROY_OZ_TO_GRAMS,
		rates,
	)
	frappe.db.commit()

	return rates


def _parse_custom_api(data):
	"""Try to extract (gold_oz, silver_oz) from a custom API response."""
	if isinstance(data, list):
		gold = silver = None
		for item in data:
			if item.get("metal") == "gold":
				gold = item.get("price") or item.get("xauPrice")
			elif item.get("metal") == "silver":
				silver = item.get("price") or item.get("xagPrice")
		if gold and silver:
			return float(gold), float(silver)
	if isinstance(data, dict):
		items = data.get("items", [data])
		g = items[0].get("xauPrice") or items[0].get("gold_price")
		s = items[0].get("xagPrice") or items[0].get("silver_price")
		if g and s:
			return float(g), float(s)
	return None


def _update_all_rates(gold_per_gram, silver_per_gram, rates):
	"""Update Gold Rate Log for all purities (canonical + alias entries)."""
	source = rates.get("source", "live")

	for purity, multiplier in GOLD_PURITY_RATES.items():
		rate = round(gold_per_gram * multiplier, 2)
		_update_rate("Yellow Gold", purity, rate, source)
		rates["gold"][purity] = rate

	for purity, multiplier in SILVER_PURITY_RATES.items():
		rate = round(silver_per_gram * multiplier, 2)
		_update_rate("Silver", purity, rate, source)
		rates["silver"][purity] = rate

	rates["gold_per_gram_raw"] = round(gold_per_gram, 2)
	rates["silver_per_gram_raw"] = round(silver_per_gram, 2)


def _update_rate(metal, purity, rate, source="live"):
	"""Helper to update or create a rate entry."""
	from frappe.utils import now_datetime

	existing = frappe.db.exists("Gold Rate Log", {"metal": metal, "purity": purity})

	if existing:
		frappe.db.set_value(
			"Gold Rate Log",
			existing,
			{"rate_per_gram": rate, "source": source, "timestamp": now_datetime()},
		)
	else:
		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": metal,
				"purity": purity,
				"rate_per_gram": rate,
				"source": source,
			}
		).insert(ignore_permissions=True)


# Keep the old function name for backward compatibility
def fetch_live_gold_rate():
	"""Alias for backward compatibility."""
	fetch_live_metal_rates()


def _cleanup_legacy_k_entries():
	"""Remove old K-form Gold Rate Log entries that are superseded by Kt canonical entries."""
	for old_purity in ["24K", "22K", "18K", "14K", "10K"]:
		for name in frappe.get_all(
			"Gold Rate Log",
			filters={"purity": old_purity},
			pluck="name",
		):
			frappe.delete_doc("Gold Rate Log", name, ignore_permissions=True, force=True)
	frappe.db.commit()
