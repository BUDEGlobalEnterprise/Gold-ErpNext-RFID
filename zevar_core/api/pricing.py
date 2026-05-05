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
def get_live_metal_rates():
	"""
	Get current live metal rates for all metals and purities.
	Accessible to all logged-in users (employees, POS users, etc).

	Non-blocking: returns cached rates immediately, even if stale.
	Stale refresh is attempted inline with a short timeout, and falls
	back to cached/hardcoded data if external APIs are unreachable.

	Returns:
		dict: Current rates grouped by metal type with metadata.
	"""
	from frappe.utils import now_datetime, time_diff_in_seconds

	rates = frappe.get_all(
		"Gold Rate Log",
		fields=["metal", "purity", "rate_per_gram", "source", "timestamp"],
		filters={"docstatus": 0},
		order_by="timestamp desc",
		ignore_permissions=True,
	)

	if not rates:
		# No cached rates at all — attempt a quick fetch, but don't hang
		try:
			from zevar_core.tasks import fetch_live_metal_rates

			fetch_result = fetch_live_metal_rates()
			return {
				"success": True,
				"rates": _format_rates_from_fetch(fetch_result),
				"last_updated": now_datetime().isoformat(),
				"source": fetch_result.get("source", "live"),
			}
		except Exception:
			# External APIs unreachable — return hardcoded fallback rates
			fallback = _get_hardcoded_fallback_rates()
			return {
				"success": True,
				"rates": fallback,
				"last_updated": now_datetime().isoformat(),
				"source": "fallback",
				"is_stale": True,
			}

	latest_ts = max((r["timestamp"] for r in rates if r.get("timestamp")), default=None)

	if latest_ts:
		age_seconds = time_diff_in_seconds(now_datetime(), latest_ts)
		# Handle clock skew: negative age means DB time is ahead of app server
		if age_seconds < 0:
			age_seconds = 0
		is_stale = age_seconds > 900
	else:
		is_stale = True

	if is_stale:
		# Attempt a non-blocking refresh; if it fails, serve stale data
		try:
			from zevar_core.tasks import fetch_live_metal_rates

			fetch_live_metal_rates()
			rates = frappe.get_all(
				"Gold Rate Log",
				fields=["metal", "purity", "rate_per_gram", "source", "timestamp"],
				filters={"docstatus": 0},
				order_by="timestamp desc",
				ignore_permissions=True,
			)
			latest_ts = max((r["timestamp"] for r in rates if r.get("timestamp")), default=None)
			is_stale = False
		except Exception:
			# Keep serving stale cached rates
			pass

	latest_per_key = {}
	# Also track the second-most-recent rate per key for trend calculation
	prev_per_key = {}
	for r in rates:
		key = (r["metal"], r["purity"])
		if key not in latest_per_key:
			latest_per_key[key] = r
		elif key not in prev_per_key:
			prev_per_key[key] = r

	grouped = {}
	for r in latest_per_key.values():
		metal = r["metal"]
		purity = r["purity"]
		if metal not in grouped:
			grouped[metal] = []

		rate_per_gram = r["rate_per_gram"]
		prev = prev_per_key.get((metal, purity))
		prev_rate = prev["rate_per_gram"] if prev else None

		# Compute trend
		change_amount = 0
		if prev_rate and prev_rate > 0:
			change_amount = round(rate_per_gram - prev_rate, 4)
			change_pct = round((change_amount / prev_rate) * 100, 2)
			if change_pct > 0:
				trend = "up"
			elif change_pct < 0:
				trend = "down"
			else:
				trend = "flat"
		else:
			change_pct = 0
			trend = "none"

		grouped[metal].append(
			{
				"purity": purity,
				"rate_per_gram": rate_per_gram,
				"trend": trend,
				"change_pct": change_pct,
				"change_amount": change_amount,
			}
		)

	return {
		"success": True,
		"rates": grouped,
		"last_updated": latest_ts.isoformat() if latest_ts else None,
		"source": rates[0]["source"] if rates else "unknown",
		"is_stale": is_stale,
	}


def _get_hardcoded_fallback_rates():
	"""Return hardcoded fallback rates when no cached data and APIs are unreachable."""
	from zevar_core.constants import GOLD_PURITY_RATES, SILVER_PURITY_RATES, TROY_OZ_TO_GRAMS

	# Approximate spot prices (USD per troy oz) as of mid-2025
	gold_oz = 3300.0
	silver_oz = 33.0
	gold_per_gram = gold_oz / TROY_OZ_TO_GRAMS
	silver_per_gram = silver_oz / TROY_OZ_TO_GRAMS

	grouped = {"Yellow Gold": [], "Silver": []}
	for purity, multiplier in GOLD_PURITY_RATES.items():
		grouped["Yellow Gold"].append(
			{
				"purity": purity,
				"rate_per_gram": round(gold_per_gram * multiplier, 2),
				"trend": "flat",
				"change_pct": 0,
			}
		)
	for purity, multiplier in SILVER_PURITY_RATES.items():
		grouped["Silver"].append(
			{
				"purity": purity,
				"rate_per_gram": round(silver_per_gram * multiplier, 2),
				"trend": "flat",
				"change_pct": 0,
			}
		)
	return grouped


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
