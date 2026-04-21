"""
Pricing API - Price calculations and gold rates
"""

import frappe

from zevar_core.constants import PURITY_VALUES


@frappe.whitelist()
def get_item_price(item_code: str) -> dict:
	"""
	Calculate item price using hierarchy: MSRP > Calculated > Standard Rate.

	Args:
	    item_code: Item code to get price for

	Returns:
	    Dictionary with pricing details
	"""
	item = frappe.get_doc("Item", item_code)

	# Priority 1: MSRP
	if item.custom_msrp and item.custom_msrp > 0:
		return _build_price_response(item, item.custom_msrp, "MSRP")

	# Priority 2: Calculated (Gold Value + Gemstone Value)
	gold_value = _calculate_gold_value(item)
	gemstone_value = _calculate_gemstone_value(item)
	calculated_price = gold_value + gemstone_value

	if calculated_price > 0:
		gold_rate = _get_gold_rate(item.custom_metal_type, item.custom_purity)
		return _build_price_response(
			item,
			calculated_price,
			"Calculated",
			gold_value=gold_value,
			gemstone_value=gemstone_value,
			gold_rate=gold_rate,
		)

	# Priority 3: Fallback to Standard Rate
	standard_rate = item.standard_rate or 0
	return _build_price_response(item, standard_rate, "Standard Rate")


@frappe.whitelist()
def get_live_metal_rates():
	"""
	Get current live metal rates for all metals and purities.
	Accessible to all logged-in users (employees, POS users, etc).

	Returns:
		dict: Current rates grouped by metal type with metadata.
	"""
	from frappe.utils import now_datetime, time_diff_in_seconds

	rates = frappe.get_all(
		"Gold Rate Log",
		fields=["metal", "purity", "rate_per_gram", "source", "timestamp"],
		filters={"docstatus": 0},
		order_by="metal, purity",
		ignore_permissions=True,
	)

	if not rates:
		# No rates in DB yet — try fetching live
		from zevar_core.tasks import fetch_live_metal_rates

		fetch_result = fetch_live_metal_rates()
		return {
			"success": True,
			"rates": _format_rates_from_fetch(fetch_result),
			"last_updated": now_datetime().isoformat(),
			"source": fetch_result.get("source", "live"),
		}

	# Group rates by metal
	grouped = {}
	for r in rates:
		metal = r["metal"]
		if metal not in grouped:
			grouped[metal] = []
		grouped[metal].append(
			{
				"purity": r["purity"],
				"rate_per_gram": r["rate_per_gram"],
			}
		)

	# Get the most recent timestamp
	latest_ts = max(r["timestamp"] for r in rates if r.get("timestamp"))

	# Calculate how long ago the rates were updated
	age_seconds = time_diff_in_seconds(now_datetime(), latest_ts) if latest_ts else 0
	is_stale = age_seconds > 900  # older than 15 minutes

	return {
		"success": True,
		"rates": grouped,
		"last_updated": latest_ts.isoformat() if latest_ts else None,
		"source": rates[0]["source"] if rates else "unknown",
		"is_stale": is_stale,
	}


@frappe.whitelist()
def get_live_rate_history(metal="Yellow Gold", days=7):
	"""
	Get historical rate data for a specific metal.
	Accessible to all logged-in users.

	Args:
	    metal: Metal type to get history for (default: Yellow Gold)
	    days: Number of days of history (default: 7)

	Returns:
	    dict: Historical rates with timestamps for charting.
	"""
	from frappe.utils import add_days, now_datetime

	since = add_days(now_datetime(), -int(days))

	logs = frappe.get_all(
		"Gold Rate Log",
		fields=["purity", "rate_per_gram", "timestamp"],
		filters={"metal": metal, "timestamp": [">=", since]},
		order_by="timestamp asc",
	)

	# Group by purity
	series = {}
	for log in logs:
		p = log["purity"]
		if p not in series:
			series[p] = []
		series[p].append(
			{
				"rate": log["rate_per_gram"],
				"timestamp": log["timestamp"].isoformat() if log["timestamp"] else None,
			}
		)

	return {
		"success": True,
		"metal": metal,
		"days": int(days),
		"series": series,
	}


@frappe.whitelist()
def refresh_gold_rates():
	"""Manually trigger gold rate refresh."""
	from zevar_core.tasks import fetch_live_metal_rates

	try:
		result = fetch_live_metal_rates()
		return {"success": True, "message": "Gold rates refreshed successfully", "rates": result}
	except Exception as e:
		frappe.log_error(f"Gold rate refresh failed: {e!s}")
		return {"success": False, "message": f"Failed to refresh rates: {e!s}"}


def _format_rates_from_fetch(fetch_result):
	"""Convert fetch result dict to grouped format matching DB structure."""
	grouped = {}

	for purity, rate in fetch_result.get("gold", {}).items():
		if "Yellow Gold" not in grouped:
			grouped["Yellow Gold"] = []
		grouped["Yellow Gold"].append({"purity": purity, "rate_per_gram": rate})

	for purity, rate in fetch_result.get("silver", {}).items():
		if "Silver" not in grouped:
			grouped["Silver"] = []
		grouped["Silver"].append({"purity": purity, "rate_per_gram": rate})

	return grouped


def _calculate_gold_value(item) -> float:
	"""Calculate gold value based on weight and rate."""
	if not item.custom_net_weight_g or not item.custom_metal_type or not item.custom_purity:
		return 0.0

	rate_per_gram = _get_gold_rate(item.custom_metal_type, item.custom_purity)
	if rate_per_gram <= 0:
		return 0.0

	return float(item.custom_net_weight_g) * rate_per_gram


def _calculate_gemstone_value(item) -> float:
	"""Calculate total gemstone value from child table."""
	if not hasattr(item, "gemstones") or not item.gemstones:
		return 0.0

	total = sum(float(gem.amount or 0) for gem in item.gemstones)
	return total


def _get_gold_rate(metal: str, purity: str) -> float:
	"""Get current gold rate for metal and purity."""
	if not metal or not purity:
		return 0.0

	# Handle Rose Gold / White Gold -> Use Yellow Gold rate
	if metal in ["Rose Gold", "White Gold"]:
		metal = "Yellow Gold"

	# Fetch latest rate from Gold Rate Log
	rate_log = frappe.db.get_value(
		"Gold Rate Log",
		filters={"metal": metal, "purity": purity},
		fieldname="rate_per_gram",
		order_by="timestamp desc",
	)  # db.get_value bypasses permissions

	return float(rate_log) if rate_log else 0.0


def _build_price_response(item, final_price: float, source: str, **kwargs) -> dict:
	"""Build standardized price response."""
	response = {
		"item_code": item.name,
		"item_name": item.item_name,
		"final_price": final_price,
		"price_source": source,
		"metal": item.custom_metal_type,
		"purity": item.custom_purity,
		"gross_weight": item.custom_gross_weight_g,
		"stone_weight": item.custom_stone_weight_g,
		"net_weight": item.custom_net_weight_g,
		"image": item.image,
	}

	# Add optional fields
	response.update(kwargs)

	# Add gemstones if available
	if hasattr(item, "gemstones") and item.gemstones:
		response["gemstones"] = [
			{
				"gem_type": g.gem_type,
				"carat": g.carat,
				"count": g.count,
				"cut": g.cut,
				"color": g.color,
				"clarity": g.clarity,
				"rate": g.rate,
				"amount": g.amount,
			}
			for g in item.gemstones
		]

	return response
