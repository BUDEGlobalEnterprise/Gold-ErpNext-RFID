"""
Catalog API - Item retrieval and filtering
"""

import re

import frappe
from frappe.rate_limiter import rate_limit

from zevar_core.constants import DEFAULT_PAGE_LENGTH, PARTNER_SOURCES


def _sanitize_search(term):
	"""Strip potentially dangerous characters from search input."""
	if not term:
		return term
	return re.sub(r'[%_\\;\'"]', "", str(term).strip())[:100]


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def get_pos_items(
	start: int = 0,
	page_length: int = DEFAULT_PAGE_LENGTH,
	warehouse: str | None = None,
	search_term: str | None = None,
	filters: str | None = None,
	sort_by: str | None = None,
	in_stock_only: bool | str = False,
	out_of_stock_only: bool | str = False,
	source_filter: str | None = None,
	min_price: float | None = None,
	max_price: float | None = None,
) -> list:
	"""
	Fetch items for POS catalog with filtering, search, and pagination.

	Args:
	    start: Starting index for pagination
	    page_length: Number of items to return
	    warehouse: Warehouse to check stock levels
	    search_term: Search term to filter item names
	    filters: JSON string of additional filters
	    sort_by: Sort key (price_asc, price_desc, weight_asc, weight_desc, newest, name_asc)
	    in_stock_only: Only return items with stock_qty > 0
	    out_of_stock_only: Only return items with stock_qty <= 0
	    source_filter: Filter by custom_source
	    min_price: Minimum price filter
	    max_price: Maximum price filter

	Returns:
	    List of item dictionaries with stock and price information
	"""
	from zevar_core.api.pricing import get_item_price

	# Convert string booleans from frontend
	in_stock_only = in_stock_only in (True, "true", "1", 1)
	out_of_stock_only = out_of_stock_only in (True, "true", "1", 1)

	# Convert price filters from string to float
	if min_price is not None and min_price != "":
		min_price = float(min_price)
	else:
		min_price = None

	if max_price is not None and max_price != "":
		max_price = float(max_price)
	else:
		max_price = None

	# Build filters
	query_filters = [["disabled", "=", 0], ["has_variants", "=", 0]]

	if search_term:
		search_term = _sanitize_search(search_term)
		query_filters.append(["item_name", "like", f"%{search_term}%"])

	if source_filter:
		query_filters.append(["custom_source", "=", source_filter])

	# Parse additional filters from JSON
	if filters:
		try:
			filters_dict = frappe.parse_json(filters)
			if isinstance(filters_dict, dict):
				# Handle jewelry type filter
				jewelry_type = filters_dict.pop("custom_jewelry_type", None)
				if jewelry_type:
					query_filters.append(["custom_jewelry_type", "=", jewelry_type])

				# Handle metal filter
				metal_type = filters_dict.pop("custom_metal_type", None)
				if metal_type:
					query_filters.append(["custom_metal_type", "=", metal_type])

				# Handle purity filter
				purity = filters_dict.pop("custom_purity", None)
				if purity:
					query_filters.append(["custom_purity", "=", purity])

				# Handle gemstone filter
				gem_filter = filters_dict.pop("custom_gemstone", None)
				if gem_filter:
					if gem_filter == "No Stone":
						items_with_stones = frappe.get_all("Zevar Gemstone Detail", pluck="parent")
						# Filter out any empty/None values
						items_with_stones = [item for item in items_with_stones if item]
						if items_with_stones:
							query_filters.append(["name", "not in", items_with_stones])
					else:
						matching_items = frappe.get_all(
							"Zevar Gemstone Detail", filters={"gem_type": gem_filter}, pluck="parent"
						)
						# Filter out any empty/None values
						matching_items = [item for item in matching_items if item]
						if not matching_items:
							return []
						query_filters.append(["name", "in", matching_items])

				# Handle price filters from JSON (fallback if not passed as direct params)
				if not min_price:
					min_price = filters_dict.pop("min_price", None)
					if min_price is not None and min_price != "":
						min_price = float(min_price)

				if not max_price:
					max_price = filters_dict.pop("max_price", None)
					if max_price is not None and max_price != "":
						max_price = float(max_price)

				# Apply any remaining custom filters
				for key, value in filters_dict.items():
					if value:
						if isinstance(value, list) and len(value) == 2 and value[0] == "like":
							# Handle 'like' operator: ["like", "%Gold%"]
							query_filters.append([key, "like", value[1]])
						elif isinstance(value, list):
							# Handle array of values: ["14K", "18K"] -> IN filter
							query_filters.append([key, "in", value])
						else:
							query_filters.append([key, "=", value])
		except Exception:
			# If JSON parsing fails, continue without additional filters
			pass

	# When stock or price filters are active, overfetch to compensate for post-query filtering
	page_length = int(page_length)
	has_post_filters = in_stock_only or out_of_stock_only or min_price or max_price
	fetch_length = page_length * 5 if has_post_filters else page_length

	# Fetch items
	items = frappe.get_list(
		"Item",
		filters=query_filters,
		fields=_get_item_fields(),
		order_by="custom_is_featured desc, custom_is_trending desc, custom_jewelry_type asc, item_name asc",
		start=int(start),
		page_length=fetch_length,
		ignore_permissions=True,
	)

	if not items:
		return []

	# Fetch stock (aggregate across all warehouses if none specified)
	item_codes = [item.name for item in items]
	stock_map = {}

	if warehouse:
		bin_entries = frappe.db.get_all(
			"Bin",
			filters={"item_code": ["in", item_codes], "warehouse": warehouse},
			fields=["item_code", "actual_qty"],
		)
		stock_map = {b.item_code: b.actual_qty for b in bin_entries}
	else:
		# Sum stock across all warehouses
		bin_entries = (
			frappe.db.sql(
				"""
            SELECT item_code, SUM(actual_qty) as total_qty
            FROM `tabBin`
            WHERE item_code IN %s AND actual_qty > 0
            GROUP BY item_code
        """,
				(item_codes,),
				as_dict=True,
			)
			if item_codes
			else []
		)
		stock_map = {b.item_code: b.total_qty for b in bin_entries}

	# Pre-fetch all standard rates
	std_rate_map = {}
	if item_codes:
		item_std_rates = frappe.get_all(
			"Item", filters={"name": ("in", item_codes)}, fields=["name", "standard_rate"]
		)
		std_rate_map = {r.name: r.standard_rate for r in item_std_rates}

	# Pre-fetch gemstone sums
	gem_sum_map = {}
	if item_codes:
		gemstones = frappe.db.sql(
			"""
			SELECT parent, sum(amount) as total_amount
			FROM `tabZevar Gemstone Detail`
			WHERE parenttype='Item' AND parent IN %s
			GROUP BY parent
		""",
			(tuple(item_codes),),
			as_dict=True,
		)
		gem_sum_map = {g.parent: g.total_amount for g in gemstones}

	# Pre-fetch all latest gold rates
	gold_rate_logs = frappe.db.sql(
		"""
		SELECT r.metal, r.purity, r.rate_per_gram
		FROM `tabGold Rate Log` r
		INNER JOIN (
			SELECT metal, purity, MAX(timestamp) as max_var
			FROM `tabGold Rate Log`
			GROUP BY metal, purity
		) grouped
		ON r.metal = grouped.metal AND r.purity = grouped.purity AND r.timestamp = grouped.max_var
	""",
		as_dict=True,
	)
	gold_rate_map = {(r.metal, r.purity): r.rate_per_gram for r in gold_rate_logs}

	# Build response
	pos_items = []
	for item in items:
		qty = stock_map.get(item.name, 0)

		# Compute price directly without expensive get_doc loop
		if item.custom_msrp and item.custom_msrp > 0:
			final_price = float(item.custom_msrp)
		else:
			metal_search = (
				"Yellow Gold"
				if item.custom_metal_type in ["Rose Gold", "White Gold"]
				else item.custom_metal_type
			)
			rate_per_gram = float(gold_rate_map.get((metal_search, item.custom_purity), 0.0))
			gold_value = float(item.custom_net_weight_g or 0) * rate_per_gram
			gemstone_value = float(gem_sum_map.get(item.name, 0.0))
			calculated_price = gold_value + gemstone_value

			if calculated_price > 0:
				final_price = calculated_price
			else:
				final_price = float(std_rate_map.get(item.name, 0.0))

			if final_price <= 0:
				final_price = float(item.custom_msrp or 0.0)

		# Apply price filter
		if min_price and final_price < float(min_price):
			continue
		if max_price and final_price > float(max_price):
			continue

		# Apply stock filters
		if in_stock_only and qty <= 0:
			continue
		if out_of_stock_only and qty > 0:
			continue

		pos_items.append(_build_item_dict(item, qty, final_price))

	# Keep the default catalog view sale-friendly: in-stock first, then featured groups.
	if sort_by:
		pos_items.sort(key=lambda item: _get_custom_sort_key(item, sort_by))
	else:
		pos_items.sort(key=_get_pos_sort_key)

	return pos_items[:page_length]


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def get_catalog_filters() -> dict:
	"""Return available filter options for catalog UI."""
	filters = {}

	# Jewelry Types
	jewelry_types = frappe.db.sql_list("""
        SELECT DISTINCT custom_jewelry_type FROM `tabItem`
        WHERE custom_jewelry_type IS NOT NULL AND custom_jewelry_type != ''
        ORDER BY custom_jewelry_type
    """)
	filters["jewelry_types"] = jewelry_types or ["Rings", "Chains", "Necklaces"]

	# Metals
	metals = frappe.db.sql_list("""
        SELECT DISTINCT custom_metal_type FROM `tabItem`
        WHERE custom_metal_type IS NOT NULL
        ORDER BY custom_metal_type
    """)
	filters["metals"] = metals or ["Yellow Gold", "White Gold"]

	# Purities
	purities = frappe.db.sql_list("""
        SELECT DISTINCT custom_purity FROM `tabItem`
        WHERE custom_purity IS NOT NULL
        ORDER BY custom_purity
    """)
	filters["purities"] = purities or ["14K", "18K"]

	# Gemstones
	gemstones = frappe.db.sql_list("""
        SELECT DISTINCT gem_type FROM `tabZevar Gemstone Detail`
        ORDER BY gem_type
    """)
	gemstones.insert(0, "No Stone")
	filters["gemstones"] = gemstones

	# Gender
	filters["genders"] = ["Unisex", "Men's", "Women's"]

	# Price range
	price_range = frappe.db.sql(
		"""
        SELECT MIN(custom_msrp) as min_price, MAX(custom_msrp) as max_price
        FROM `tabItem`
        WHERE custom_msrp > 0
    """,
		as_dict=True,
	)

	if price_range:
		filters["price_range"] = {
			"min": price_range[0].min_price or 0,
			"max": price_range[0].max_price or 10000,
		}

	return filters


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def get_item_details(item_code: str) -> dict:
	"""Fetch full item details including gemstones and all product attributes."""
	from zevar_core.api.pricing import get_item_price

	item = frappe.get_doc("Item", item_code)

	# Get gemstones
	gemstones = []
	if hasattr(item, "gemstones"):
		for gem in item.gemstones:
			gemstones.append(
				{
					"gem_type": gem.gem_type,
					"carat": gem.carat,
					"count": gem.count,
					"cut": gem.cut,
					"color": gem.color,
					"clarity": gem.clarity,
					"rate": gem.rate,
					"amount": gem.amount,
				}
			)

	# Get price
	try:
		price_data = get_item_price(item_code)
		price = price_data.get("final_price", item.custom_msrp or 0)
	except Exception:
		price = item.custom_msrp or 0

	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"description": item.description,
		"image": item.image,
		"metal": item.custom_metal_type,
		"purity": item.custom_purity,
		"gross_weight": item.custom_gross_weight_g,
		"stone_weight": item.custom_stone_weight_g,
		"net_weight": item.custom_net_weight_g,
		"product_type": item.custom_product_type,
		"jewelry_type": item.custom_jewelry_type,
		"jewelry_subtype": item.custom_jewelry_subtype,
		"material_color": item.custom_material_color,
		"finish": item.custom_finish,
		"plating": item.custom_plating,
		"length": f"{item.custom_length_value} {item.custom_length_unit}"
		if item.custom_length_value
		else None,
		"width": f"{item.custom_width_value} {item.custom_width_unit}" if item.custom_width_value else None,
		"size": item.custom_size,
		"chain_type": item.custom_chain_type,
		"clasp_type": item.custom_clasp_type,
		"gender": item.custom_gender,
		"completeness": "Complete (all stones included)" if item.custom_product_type else None,
		"country_of_origin": item.custom_country_of_origin,
		"gemstones": gemstones,
		"custom_source": item.custom_source,
		"price": price,
		"msrp": item.custom_msrp,
	}


def _get_item_fields():
	"""Return list of fields to fetch for items."""
	return [
		"name",
		"item_name",
		"item_group",
		"image",
		"description",
		"custom_metal_type",
		"custom_purity",
		"custom_gross_weight_g",
		"custom_stone_weight_g",
		"custom_net_weight_g",
		"custom_product_type",
		"custom_jewelry_type",
		"custom_jewelry_subtype",
		"custom_material_color",
		"custom_finish",
		"custom_plating",
		"custom_length_value",
		"custom_length_unit",
		"custom_width_value",
		"custom_width_unit",
		"custom_size",
		"custom_chain_type",
		"custom_clasp_type",
		"custom_vendor_sku",
		"custom_vendor",
		"custom_country_of_origin",
		"custom_msrp",
		"custom_source",
		"custom_gender",
		"custom_is_featured",
		"custom_is_trending",
	]


def _build_item_dict(item, qty, final_price):
	"""Build item dictionary for API response."""
	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"item_group": item.item_group,
		"image": item.image,
		"description": item.description,
		"stock_qty": qty,
		"price": final_price,
		"msrp": item.custom_msrp,
		"metal": item.custom_metal_type,
		"purity": item.custom_purity,
		"material_color": item.custom_material_color,
		"finish": item.custom_finish,
		"plating": item.custom_plating,
		"gross_weight": item.custom_gross_weight_g,
		"stone_weight": item.custom_stone_weight_g,
		"net_weight": item.custom_net_weight_g,
		"product_type": item.custom_product_type,
		"jewelry_type": item.custom_jewelry_type,
		"jewelry_subtype": item.custom_jewelry_subtype,
		"length": f"{item.custom_length_value} {item.custom_length_unit}"
		if item.custom_length_value
		else None,
		"width": f"{item.custom_width_value} {item.custom_width_unit}" if item.custom_width_value else None,
		"size": item.custom_size,
		"chain_type": item.custom_chain_type,
		"clasp_type": item.custom_clasp_type,
		"vendor_sku": item.custom_vendor_sku,
		"vendor": item.custom_vendor,
		"country_of_origin": item.custom_country_of_origin,
		"custom_source": item.custom_source,
		"gender": item.custom_gender,
		"is_featured": item.custom_is_featured,
		"is_trending": item.custom_is_trending,
	}


def _get_pos_sort_key(item: dict) -> tuple:
	"""Sort sellable items ahead of unavailable ones, then group by jewelry type and name."""
	return (
		item["stock_qty"] <= 0,
		0 if item.get("is_featured") else 1,
		0 if item.get("is_trending") else 1,
		(item.get("jewelry_type") or item.get("item_group") or "").casefold(),
		(item.get("item_name") or "").casefold(),
	)


def _get_custom_sort_key(item: dict, sort_by: str):
	"""Return sort key based on user-selected sort option."""
	price = float(item.get("price") or 0)
	weight = float(item.get("gross_weight") or 0)
	name = (item.get("item_name") or "").casefold()

	if sort_by == "price_asc":
		return (price, name)
	elif sort_by == "price_desc":
		return (-price, name)
	elif sort_by == "weight_asc":
		return (weight, name)
	elif sort_by == "weight_desc":
		return (-weight, name)
	elif sort_by == "newest":
		return name
	elif sort_by == "name_asc":
		return name
	return (0, name)
