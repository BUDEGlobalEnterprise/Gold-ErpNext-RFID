"""
Pricing API - Price calculations and gold rates
"""

import frappe

from zevar_core.constants import PURITY_ALIASES


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
def refresh_gold_rates():
	"""Manually trigger gold rate refresh."""
	from zevar_core.tasks import fetch_live_metal_rates

	try:
		result = fetch_live_metal_rates()
		return {"success": True, "message": "Gold rates refreshed successfully", "rates": result}
	except Exception as e:
		frappe.log_error(f"Gold rate refresh failed: {e!s}")
		return {"success": False, "message": f"Failed to refresh rates: {e!s}"}


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
	"""Get current gold rate for metal and purity.

	Handles purity naming variants: items may use "14K" while the
	Gold Rate Log stores "14Kt".  Tries the given purity first, then
	falls back to the canonical alias.
	"""
	if not metal or not purity:
		return 0.0

	# Handle Rose Gold / White Gold -> Use Yellow Gold rate
	if metal in ["Rose Gold", "White Gold"]:
		metal = "Yellow Gold"

	# Try the purity name as-is first
	rate_log = frappe.db.get_value(
		"Gold Rate Log",
		filters={"metal": metal, "purity": purity},
		fieldname="rate_per_gram",
		order_by="timestamp desc",
	)

	# If not found, try the canonical alias (e.g. "14K" -> "14Kt")
	if rate_log is None and purity in PURITY_ALIASES:
		rate_log = frappe.db.get_value(
			"Gold Rate Log",
			filters={"metal": metal, "purity": PURITY_ALIASES[purity]},
			fieldname="rate_per_gram",
			order_by="timestamp desc",
		)

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
