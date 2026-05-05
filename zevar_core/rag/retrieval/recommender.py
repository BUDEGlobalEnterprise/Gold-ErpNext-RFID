"""
Customer Recommendation Engine.

Generates product recommendations by:
1. Building a customer profile from purchase history and preferences
2. Extracting the customer's style/price/metal preferences
3. Vector-searching for matching products
4. Ranking results by fit score and occasion relevance
"""

import logging

import frappe

from zevar_core.rag.retrieval.vector_search import search_products

log = logging.getLogger(__name__)

# Occasion -> search hints for product matching
OCCASION_HINTS = {
	"anniversary": "anniversary romantic elegant pendant necklace diamond",
	"birthday": "birthday gift stylish trendy",
	"wedding": "wedding band ring bridal elegant",
	"engagement": "engagement ring diamond proposal",
	"valentine": "heart romantic love valentine red rose",
	"christmas": "holiday gift festive sparkly",
	"mothers_day": "mother family elegant classic",
	"graduation": "graduate modern minimalist simple",
	"just_because": "trendy stylish unique",
}


def get_customer_profile(customer_id: str) -> dict:
	"""Build a customer profile for recommendations.

	Extracts non-PII preferences and purchase patterns.

	Returns:
		Dict with preferences, purchase_summary, and search_query.
	"""
	customer = frappe.get_doc("Customer", customer_id)
	profile = {
		"customer_id": customer_id,
		"customer_name": customer.customer_name,
		"preferences": {},
		"purchase_summary": {},
	}

	# Extract preferences (non-PII)
	for field, key in [
		("custom_preferred_metal", "preferred_metal"),
		("custom_preferred_purity", "preferred_purity"),
		("custom_preferred_jewelry_type", "preferred_jewelry_type"),
		("custom_ring_size", "ring_size"),
		("custom_gender", "gender"),
	]:
		val = getattr(customer, field, None)
		if val:
			profile["preferences"][key] = val

	# Purchase summary from Sales Invoice items
	try:
		# Get purchased item types/metals
		purchased_items = frappe.db.sql(
			"""SELECT
				i.custom_jewelry_type,
				i.custom_metal_type,
				i.custom_purity,
				i.custom_gender,
				COUNT(*) as count
			FROM `tabSales Invoice Item` sii
			JOIN `tabItem` i ON i.name = sii.item_code
			JOIN `tabSales Invoice` si ON si.name = sii.parent
			WHERE si.customer = %s AND si.docstatus = 1
			GROUP BY i.custom_jewelry_type, i.custom_metal_type, i.custom_purity
			ORDER BY count DESC
			LIMIT 10""",
			(customer_id,),
			as_dict=True,
		)

		if purchased_items:
			# Most bought jewelry type
			jewelry_types = {}
			metals = {}
			for row in purchased_items:
				if row.custom_jewelry_type:
					jewelry_types[row.custom_jewelry_type] = jewelry_types.get(row.custom_jewelry_type, 0) + row.count
				if row.custom_metal_type:
					metals[row.custom_metal_type] = metals.get(row.custom_metal_type, 0) + row.count

			profile["purchase_summary"]["jewelry_types"] = dict(sorted(jewelry_types.items(), key=lambda x: -x[1]))
			profile["purchase_summary"]["metals"] = dict(sorted(metals.items(), key=lambda x: -x[1]))

		# Spending range
		spending = frappe.db.sql(
			"""SELECT
				MIN(si.grand_total) as min_order,
				MAX(si.grand_total) as max_order,
				AVG(si.grand_total) as avg_order,
				COUNT(*) as total_orders
			FROM `tabSales Invoice`
			WHERE customer = %s AND docstatus = 1""",
			(customer_id,),
			as_dict=True,
		)
		if spending and spending[0].total_orders:
			profile["purchase_summary"]["spending"] = {
				"min": float(spending[0].min_order or 0),
				"max": float(spending[0].max_order or 0),
				"avg": float(spending[0].avg_order or 0),
				"orders": spending[0].total_orders,
			}
	except Exception:
		log.exception("Error fetching purchase summary for %s", customer_id)

	# Build search query from profile
	profile["search_query"] = _build_search_query(profile)

	return profile


def recommend_for_customer(
	customer_id: str,
	occasion: str | None = None,
	limit: int = 5,
) -> list[dict]:
	"""Get product recommendations for a customer.

	Args:
		customer_id: Customer ID
		occasion: Optional occasion hint (anniversary, birthday, etc.)
		limit: Max recommendations

	Returns:
		List of recommendation dicts with product info + reasoning.
	"""
	profile = get_customer_profile(customer_id)

	# Build the search query from profile + occasion
	search_query = profile["search_query"]
	if occasion and occasion in OCCASION_HINTS:
		search_query = f"{OCCASION_HINTS[occasion]} {search_query}"

	if not search_query.strip():
		return []

	# Search products
	results = search_products(search_query, top_k=limit * 2)

	# Filter and enrich recommendations
	recommendations = []
	for r in results[:limit * 2]:
		item_code = r.get("id") or r.get("metadata", {}).get("item_code")
		if not item_code:
			continue

		reasoning = _build_reasoning(r, profile, occasion)

		# Fetch live product data
		product = _get_product_details(item_code)
		if not product:
			continue

		product["similarity"] = r.get("similarity", 0)
		product["reasoning"] = reasoning
		recommendations.append(product)

		if len(recommendations) >= limit:
			break

	return recommendations


def _build_search_query(profile: dict) -> str:
	"""Build a natural language search query from the customer profile."""
	parts = []

	prefs = profile.get("preferences", {})
	if prefs.get("preferred_jewelry_type"):
		parts.append(prefs["preferred_jewelry_type"])
	if prefs.get("preferred_metal"):
		parts.append(prefs["preferred_metal"])
	if prefs.get("preferred_purity"):
		parts.append(prefs["preferred_purity"])
	if prefs.get("gender"):
		parts.append(f"for {prefs['gender']}")

	# From purchase history
	purchase = profile.get("purchase_summary", {})
	jewelry_types = purchase.get("jewelry_types", {})
	if jewelry_types and not prefs.get("preferred_jewelry_type"):
		top_type = list(jewelry_types.keys())[0]
		parts.append(top_type)

	metals = purchase.get("metals", {})
	if metals and not prefs.get("preferred_metal"):
		top_metal = list(metals.keys())[0]
		parts.append(top_metal)

	return " ".join(parts) if parts else "jewelry"


def _build_reasoning(result: dict, profile: dict, occasion: str | None) -> str:
	"""Build a human-readable reasoning string for why this was recommended."""
	reasons = []
	prefs = profile.get("preferences", {})
	purchase = profile.get("purchase_summary", {})
	metadata = result.get("metadata", {})

	if prefs.get("preferred_metal") and metadata.get("metal_type") == prefs["preferred_metal"]:
		reasons.append(f"matches preferred metal ({prefs['preferred_metal']})")
	if prefs.get("preferred_purity") and metadata.get("purity") == prefs["preferred_purity"]:
		reasons.append(f"matches preferred purity ({prefs['preferred_purity']})")

	jewelry_types = purchase.get("jewelry_types", {})
	if jewelry_types:
		top_type = list(jewelry_types.keys())[0]
		if metadata.get("jewelry_type") == top_type:
			reasons.append(f"matches most-purchased type ({top_type})")

	if occasion:
		reasons.append(f"suitable for {occasion}")

	if not reasons:
		reasons.append(f"{result.get('similarity', 0):.0%} similarity match")

	return "; ".join(reasons)


def _get_product_details(item_code: str) -> dict | None:
	"""Fetch live product details for a recommendation card."""
	try:
		item = frappe.db.get_value(
			"Item",
			item_code,
			[
				"name", "item_name", "image",
				"custom_metal_type", "custom_purity",
				"custom_jewelry_type", "custom_msrp",
				"custom_gender", "custom_source",
			],
			as_dict=True,
		)
		if not item:
			return None

		stock_qty = frappe.db.sql(
			"SELECT COALESCE(SUM(actual_qty), 0) FROM `tabBin` WHERE item_code=%s",
			(item_code,),
		)[0][0]

		return {
			"item_code": item.name,
			"item_name": item.item_name,
			"image": item.image,
			"metal": item.custom_metal_type,
			"purity": item.custom_purity,
			"jewelry_type": item.custom_jewelry_type,
			"msrp": float(item.custom_msrp or 0),
			"gender": item.custom_gender,
			"source": item.custom_source,
			"stock_qty": float(stock_qty),
		}
	except Exception:
		return None
