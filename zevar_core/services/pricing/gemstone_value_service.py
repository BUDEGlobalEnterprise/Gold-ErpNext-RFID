"""
Gemstone Value Service — Per-cert valuation reference for gemstones.

Provides gemstone valuation utilities, cert-based lookups,
and price-per-carat estimation for the Zevar inventory system.
"""

import frappe
from frappe import _
from frappe.utils import flt

# ─── Main API ──────────────────────────────────────────────────────


def get_gemstone_value(gemstone_name: str) -> dict:
	"""
	Return the current valuation for a Zevar Gemstone record.

	Args:
	    gemstone_name: The Zevar Gemstone document name

	Returns:
	    dict with cost_basis, estimated_retail, price_per_carat
	"""
	gem = frappe.get_doc("Zevar Gemstone", gemstone_name)

	cost = flt(gem.cost_basis, 2)
	ppc = flt(cost / gem.carat_weight, 2) if gem.carat_weight else 0
	estimated_retail = _estimate_retail(gem)

	return {
		"gemstone": gemstone_name,
		"gemstone_type": gem.gemstone_type,
		"carat_weight": gem.carat_weight,
		"cost_basis": cost,
		"price_per_carat": ppc,
		"estimated_retail": estimated_retail,
		"lab": gem.lab,
		"cert_number": gem.cert_number,
		"color_grade": gem.color_grade,
		"clarity_grade": gem.clarity_grade,
	}


def estimate_value_from_specs(
	gemstone_type: str,
	carat_weight: float,
	color_grade: str | None = None,
	clarity_grade: str | None = None,
	cut_grade: str | None = None,
	lab: str | None = None,
) -> dict:
	"""
	Estimate a gemstone's value based on specs without a specific record.
	Uses historical data from existing Zevar Gemstone records.

	Returns:
	    dict with estimated_cost, price_per_carat, comparable_count
	"""
	filters = {
		"gemstone_type": gemstone_type,
		"status": ["in", ["In Stock", "Sold"]],
		"cost_basis": [">", 0],
	}
	if color_grade:
		filters["color_grade"] = color_grade
	if clarity_grade:
		filters["clarity_grade"] = clarity_grade

	comparables = frappe.get_all(
		"Zevar Gemstone",
		filters=filters,
		fields=["carat_weight", "cost_basis"],
		order_by="creation desc",
		limit=50,
	)

	if not comparables:
		return {
			"estimated_cost": 0,
			"price_per_carat": 0,
			"comparable_count": 0,
			"confidence": "none",
		}

	# Calculate average price per carat from comparables
	total_cost = sum(flt(c["cost_basis"]) for c in comparables)
	total_carats = sum(flt(c["carat_weight"]) for c in comparables)
	avg_ppc = flt(total_cost / total_carats, 2) if total_carats > 0 else 0

	estimated = flt(avg_ppc * carat_weight, 2)
	confidence = "high" if len(comparables) >= 20 else "medium" if len(comparables) >= 5 else "low"

	return {
		"estimated_cost": estimated,
		"price_per_carat": avg_ppc,
		"comparable_count": len(comparables),
		"confidence": confidence,
	}


def get_melee_parcel_value(parcel_name: str) -> dict:
	"""
	Valuate a melee diamond parcel.

	Args:
	    parcel_name: The Zevar Melee Parcel document name

	Returns:
	    dict with total_value, cost_per_carat, selling_price_per_carat
	"""
	parcel = frappe.get_doc("Zevar Melee Parcel", parcel_name)

	cost_total = flt(parcel.cost_per_carat * parcel.total_carats, 2)
	sell_total = flt(parcel.selling_price_per_carat * parcel.total_carats, 2)

	return {
		"parcel": parcel_name,
		"total_carats": parcel.total_carats,
		"stone_count": parcel.stone_count,
		"cost_per_carat": parcel.cost_per_carat,
		"selling_price_per_carat": parcel.selling_price_per_carat,
		"total_cost": cost_total,
		"total_retail": sell_total,
		"margin_pct": flt((sell_total - cost_total) / cost_total * 100, 1) if cost_total else 0,
	}


def get_cert_lookup_url(lab: str, cert_number: str) -> str | None:
	"""
	Return the public verification URL for a gemstone certificate.

	Args:
	    lab: Certificate lab (GIA, IGI, HRD, AGS)
	    cert_number: The certificate number

	Returns:
	    URL string or None if lab not supported
	"""
	urls = {
		"GIA": f"https://www.gia.edu/report-check?reportno={cert_number}",
		"IGI": f"https://www.igi.org/verify-your-report?r={cert_number}",
		"HRD": f"https://my.hrdantwerp.com/?record_number={cert_number}",
		"AGS": f"https://www.agslab.com/report/{cert_number}",
	}
	return urls.get(lab)


def bulk_valuate(gemstone_names: list[str]) -> list[dict]:
	"""
	Valuate multiple gemstones in batch.
	More efficient than calling get_gemstone_value in a loop.
	"""
	if not gemstone_names:
		return []

	gems = frappe.get_all(
		"Zevar Gemstone",
		filters={"name": ["in", gemstone_names]},
		fields=[
			"name",
			"gemstone_type",
			"carat_weight",
			"cost_basis",
			"lab",
			"cert_number",
			"color_grade",
			"clarity_grade",
			"shape",
			"status",
		],
	)

	result = []
	for gem in gems:
		cost = flt(gem["cost_basis"], 2)
		ppc = flt(cost / gem["carat_weight"], 2) if gem["carat_weight"] else 0
		result.append(
			{
				"gemstone": gem["name"],
				"gemstone_type": gem["gemstone_type"],
				"carat_weight": gem["carat_weight"],
				"cost_basis": cost,
				"price_per_carat": ppc,
				"lab": gem["lab"],
				"cert_number": gem["cert_number"],
				"status": gem["status"],
			}
		)

	return result


# ─── Internal helpers ──────────────────────────────────────────────


def _estimate_retail(gem) -> float:
	"""
	Estimate retail value based on cost basis and typical markup.
	Diamond markup: 2.0-3.0x depending on size
	Colored stone markup: 2.5-4.0x
	"""
	cost = flt(gem.cost_basis, 2)
	if not cost:
		return 0

	gem_type = (gem.gemstone_type or "").lower()
	carat = flt(gem.carat_weight)

	if "diamond" in gem_type:
		# Larger diamonds have lower markup percentage
		if carat >= 2.0:
			markup = 2.0
		elif carat >= 1.0:
			markup = 2.2
		elif carat >= 0.5:
			markup = 2.5
		else:
			markup = 3.0
	elif gem_type in ("ruby", "sapphire", "emerald"):
		markup = 3.0
	else:
		markup = 2.5

	# Premium for certified stones
	if gem.lab in ("GIA", "AGS"):
		markup *= 1.05

	return flt(cost * markup, 2)
