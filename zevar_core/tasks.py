"""Scheduled tasks for Zevar Core"""

import frappe
import requests

from zevar_core.constants import TROY_OZ_TO_GRAMS


def fetch_live_metal_rates():
	"""
	Fetches live gold and silver rates from configured API.
	Falls back to goldprice.org if no API configured.
	Called by scheduler every 15 minutes.

	Returns:
		dict: Current rates with metals, purities, and metadata.
	"""
	gold_purities = {
		"24K": 0.999,
		"22K": 0.916,
		"18Kt": 0.750,
		"14Kt": 0.585,
		"10k": 0.417,
	}

	silver_purities = {
		"999 Fine": 0.999,
		"925 Sterling": 0.925,
	}

	rates = {"gold": {}, "silver": {}, "source": "live", "error": None}

	try:
		api_url = "https://data-asg.goldprice.org/dbXRates/USD"  # Default

		if frappe.db.exists("Gold Settings", "Gold Settings"):
			settings = frappe.get_single("Gold Settings")
			if settings.api_endpoint:
				api_url = settings.api_endpoint

		# Fetch live rates
		response = requests.get(
			api_url,
			headers={"User-Agent": "Zevar-POS/1.0 (Zevar Jewelers; gold-rate-sync)"},
			timeout=10,
		)
		response.raise_for_status()
		data = response.json()

		# Extract prices (USD per troy ounce)
		gold_price_per_oz = data["items"][0]["xauPrice"]
		silver_price_per_oz = data["items"][0]["xagPrice"]

		# Convert to per gram
		gold_per_gram = gold_price_per_oz / TROY_OZ_TO_GRAMS
		silver_per_gram = silver_price_per_oz / TROY_OZ_TO_GRAMS

		# Update Gold rates
		for purity, multiplier in gold_purities.items():
			rate = round(gold_per_gram * multiplier, 2)
			_update_rate("Yellow Gold", purity, rate)
			rates["gold"][purity] = rate

		# Update Silver rates
		for purity, multiplier in silver_purities.items():
			rate = round(silver_per_gram * multiplier, 2)
			_update_rate("Silver", purity, rate)
			rates["silver"][purity] = rate

		frappe.db.commit()  # nosemgrep: frappe-semgrep-rules/rules.frappe-manual-commit
		frappe.logger().info(
			f"Metal rates updated: Gold 24K=${gold_per_gram:.2f}/g, Silver 999=${silver_per_gram:.2f}/g"
		)

		rates["gold_per_gram_raw"] = round(gold_per_gram, 2)
		rates["silver_per_gram_raw"] = round(silver_per_gram, 2)

	except Exception as e:
		frappe.logger().error(f"Metal rate fetch failed: {e!s}")
		frappe.logger().info("Using fallback metal rates due to API failure.")

		rates["source"] = "fallback"
		rates["error"] = str(e)

		# Fallback to static rates if API is down/blocking
		gold_per_gram = 2450.0 / TROY_OZ_TO_GRAMS  # fallback $2450/oz
		silver_per_gram = 30.0 / TROY_OZ_TO_GRAMS  # fallback $30/oz

		for purity, multiplier in gold_purities.items():
			rate = round(gold_per_gram * multiplier, 2)
			_update_rate("Yellow Gold", purity, rate)
			rates["gold"][purity] = rate

		for purity, multiplier in silver_purities.items():
			rate = round(silver_per_gram * multiplier, 2)
			_update_rate("Silver", purity, rate)
			rates["silver"][purity] = rate

		rates["gold_per_gram_raw"] = round(gold_per_gram, 2)
		rates["silver_per_gram_raw"] = round(silver_per_gram, 2)

		frappe.db.commit()

	return rates


def _update_rate(metal, purity, rate):
	"""Helper to update or create a rate entry."""
	from frappe.utils import now_datetime

	existing = frappe.db.exists("Gold Rate Log", {"metal": metal, "purity": purity})

	if existing:
		frappe.db.set_value(
			"Gold Rate Log",
			existing,
			{"rate_per_gram": rate, "source": "goldprice.org", "timestamp": now_datetime()},
		)
	else:
		frappe.get_doc(
			{
				"doctype": "Gold Rate Log",
				"metal": metal,
				"purity": purity,
				"rate_per_gram": rate,
				"source": "goldprice.org",
			}
		).insert(ignore_permissions=True)


# Keep the old function name for backward compatibility
def fetch_live_gold_rate():
	"""Alias for backward compatibility."""
	fetch_live_metal_rates()
