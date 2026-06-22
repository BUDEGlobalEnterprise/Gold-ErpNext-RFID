"""
Catalog API - Item retrieval and filtering
"""

import re

import frappe
from frappe.rate_limiter import rate_limit

from zevar_core.constants import DEFAULT_PAGE_LENGTH, PARTNER_SOURCES, PURITY_ALIASES, PURITY_VALUES


def _sanitize_search(term):
	"""Strip potentially dangerous characters from search input."""
	if not term:
		return term
	return re.sub(r'[%_\\;\'"]', "", str(term).strip())[:100]


def _resolve_display_case_warehouse(term: str) -> str | None:
	"""Return the warehouse for an active Display Case whose code/name matches `term`.

	Used by `get_pos_items` so that scanning or typing a Display Case identifier
	(e.g. "CASE-A1") in the search box automatically scopes the catalog to that
	case's warehouse. Returns None if no active case matches exactly.

	Match is case-insensitive against `case_code` first, then the document `name`
	(which equals `case_name` per the DocType's autoname rule).
	"""
	if not term:
		return None

	# Try case_code first — that is what is typically printed on the physical
	# case label and most likely to be scanned.
	case = frappe.db.get_value(
		"Display Case",
		{"case_code": term, "is_active": 1},
		["warehouse"],
		as_dict=True,
	)
	if not case:
		case = frappe.db.get_value(
			"Display Case",
			{"name": term, "is_active": 1},
			["warehouse"],
			as_dict=True,
		)
	return case.warehouse if case else None


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def get_pos_items(
	start: int = 0,
	page_length: int = DEFAULT_PAGE_LENGTH,
	warehouse: str | None = None,
	display_case: str | None = None,
	search_term: str | None = None,
	filters: str | None = None,
	sort_by: str | None = None,
	in_stock_only: bool | str = False,
	out_of_stock_only: bool | str = False,
	source_filter: str | None = None,
	min_price: float | None = None,
	max_price: float | None = None,
	inventory_only: bool | str = False,
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
	    inventory_only: Only return items that have a Bin record in the given warehouse

	Returns:
	    List of item dictionaries with stock and price information
	"""
	from zevar_core.api.permissions import assert_pos_warehouse_access
	from zevar_core.api.pricing import get_item_price

	if display_case:
		case_wh = frappe.db.get_value("Display Case", display_case, "warehouse")
		if case_wh:
			warehouse = case_wh

	# Multi-store enforcement: if the caller pinned a warehouse, verify the
	# user is actually allowed to read from it. Manager-class roles bypass.
	# This runs before the omni-search so we fail fast on cross-store access
	# attempts and never leak Bin counts from another store.
	if warehouse:
		assert_pos_warehouse_access(warehouse)

	# Convert string booleans from frontend
	in_stock_only = in_stock_only in (True, "true", "1", 1)
	out_of_stock_only = out_of_stock_only in (True, "true", "1", 1)
	inventory_only = inventory_only in (True, "true", "1", 1)

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
	or_filters = None

	if search_term:
		search_term = _sanitize_search(search_term)
		if search_term:
			# Omni-search: match item_code (name), item_name, or vendor SKU.
			# We use or_filters so this is OR'd internally but AND'd with the
			# disabled/has_variants/source/etc filters above.
			like = f"%{search_term}%"
			or_filters = [
				["name", "like", like],
				["item_name", "like", like],
				["custom_vendor_sku", "like", like],
			]

			# If the search term matches a Display Case identifier, auto-scope
			# the catalog to that case's warehouse so a cashier can scan a case
			# label (e.g. "CASE-A1") and see only its contents. We only do this
			# when the caller hasn't already pinned a warehouse/case to avoid
			# silently overriding explicit context.
			if not warehouse and not display_case:
				case_wh = _resolve_display_case_warehouse(search_term)
				if case_wh:
					warehouse = case_wh
					# Newly-resolved warehouse must also pass the multi-store
					# check — a cashier scanning another store's case label
					# should not see that store's catalog.
					assert_pos_warehouse_access(warehouse)

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

	# Resolve child warehouses once so both inventory_only pre-filter and
	# the stock aggregation below include Showcase, Back Stock, Safe, etc.
	_warehouse_list = None
	if warehouse:
		_roots = frappe.get_all("Warehouse", filters={"name": warehouse}, pluck="name")
		_children = frappe.get_all(
			"Warehouse",
			filters={"parent_warehouse": warehouse, "is_group": 0},
			pluck="name",
		)
		_warehouse_list = list(set(_roots + _children)) or [warehouse]

	# When inventory_only is True and a warehouse is specified, pre-filter
	# item codes by Bin at the SQL level so we never fetch thousands of
	# irrelevant items from the Item table. Each store typically has ~1000
	# items while the total catalog is 5000+.
	if inventory_only and warehouse:
		warehouse_item_codes = frappe.db.get_all(
			"Bin",
			filters={"warehouse": ["in", _warehouse_list or [warehouse]]},
			pluck="item_code",
		)
		if not warehouse_item_codes:
			return []
		query_filters.append(["name", "in", warehouse_item_codes])

	# Fetch items
	items = frappe.get_list(
		"Item",
		filters=query_filters,
		or_filters=or_filters,
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
		# _warehouse_list already resolved above (includes child warehouses)
		bin_entries = frappe.db.get_all(
			"Bin",
			filters={"item_code": ["in", item_codes], "warehouse": ["in", _warehouse_list or [warehouse]]},
			fields=["item_code", "actual_qty"],
		)
		stock_map = {}
		for b in bin_entries:
			stock_map[b.item_code] = stock_map.get(b.item_code, 0) + b.actual_qty
	else:
		# Sum stock across all warehouses
		bin_entries = (
			frappe.db.sql(  # nosemgrep
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
		gemstones = frappe.db.sql(  # nosemgrep
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
	gold_rate_logs = frappe.db.sql(  # nosemgrep
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
			purity = item.custom_purity or ""
			# Normalize purity for lookup (e.g. "18K" → "18Kt")
			purity_lower = purity.lower().strip()
			normalized_purity = PURITY_ALIASES.get(purity_lower, purity)
			# Try normalized first, then original
			rate_per_gram = float(
				gold_rate_map.get((metal_search, normalized_purity), 0.0)
				or gold_rate_map.get((metal_search, purity), 0.0)
			)
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
def get_display_cases(store_location: str | None = None) -> list:
	"""Return list of all active display cases for a store."""
	filters = {"is_active": 1}
	if store_location:
		filters["store_location"] = store_location

	cases = frappe.get_all(
		"Display Case",
		filters=filters,
		fields=["name", "case_code", "case_name", "zone_type", "warehouse", "item_count", "total_value"],
		order_by="zone_type desc, case_code asc",
	)
	return cases


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def get_catalog_filters(store_location: str | None = None) -> dict:
	"""Return available filter options for catalog UI."""
	filters = {}

	# Display Cases
	filters["display_cases"] = get_display_cases(store_location)

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
	filters["purities"] = purities or ["14Kt", "18Kt"]

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
	price_range = frappe.db.sql(  # nosemgrep
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


# ─── VENDOR CATALOGS ─────────────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
@rate_limit(limit=100, seconds=60)
def get_catalog_vendors(
	page: int = 1,
	page_size: int = 50,
	search: str | None = None,
	source: str | None = None,
) -> dict:
	"""Group items by their `custom_vendor` (Supplier link) and return per-vendor
	summary stats: item count, total stock value, source breakdown, last update.

	Used by the "Catalogs" dashboard page to show a vendor → catalog index.
	No new DocType is introduced — Items are the source of truth.
	"""
	frappe.has_permission("Item", ptype="read", throw=True)

	page = max(1, int(page or 1))
	page_size = min(100, max(1, int(page_size or 50)))
	limit_start = (page - 1) * page_size

	# Build SQL filter clause once, reuse for both grouping queries.
	filter_clauses = ["disabled = 0"]
	filter_params = []
	if source:
		filter_clauses.append("custom_source = %s")
		filter_params.append(source)
	if search:
		search = _sanitize_search(search)
		if search:
			filter_clauses.append("item_name LIKE %s")
			filter_params.append(f"%{search}%")
	filter_sql = " AND ".join(filter_clauses)

	# (1) Per-vendor totals in a single grouped query.
	vendor_rows = frappe.db.sql(
		f"""
		SELECT
			COALESCE(custom_vendor, '(Unassigned)') AS vendor,
			COUNT(name) AS item_count,
			COALESCE(SUM(COALESCE(custom_msrp, standard_rate, 0)), 0) AS total_value,
			COALESCE(MIN(COALESCE(custom_msrp, standard_rate, 0)), 0) AS min_price,
			COALESCE(MAX(COALESCE(custom_msrp, standard_rate, 0)), 0) AS max_price,
			MAX(modified) AS latest_modified
		FROM `tabItem`
		WHERE {filter_sql}
		GROUP BY custom_vendor
		""",
		filter_params,
		as_dict=True,
	)

	# (2) Per-(vendor, source) counts to build the sources breakdown.
	source_rows = frappe.db.sql(
		f"""
		SELECT
			COALESCE(custom_vendor, '(Unassigned)') AS vendor,
			COALESCE(custom_source, 'Other') AS source,
			COUNT(name) AS source_count
		FROM `tabItem`
		WHERE {filter_sql}
		GROUP BY custom_vendor, custom_source
		""",
		filter_params,
		as_dict=True,
	)

	# Merge sources into the vendor rows.
	sources_by_vendor: dict[str, dict[str, int]] = {}
	for row in source_rows:
		sources_by_vendor.setdefault(row.vendor, {})[row.source] = int(row.source_count)

	vendor_map: dict[str, dict] = {}
	for row in vendor_rows:
		vendor = row.vendor
		vendor_map[vendor] = {
			"vendor": vendor,
			"vendor_name": vendor,
			"item_count": int(row.item_count),
			"total_value": float(row.total_value or 0),
			"min_price": float(row.min_price or 0),
			"max_price": float(row.max_price or 0),
			"sources": sources_by_vendor.get(vendor, {}),
			"latest_modified": row.latest_modified,
		}

	# Resolve Supplier display names
	vendor_names = frappe.get_all(
		"Supplier",
		filters={"name": ["in", [k for k in vendor_map if k != "(Unassigned)"]]},
		fields=["name", "supplier_name"],
	)
	name_lookup = {s.name: s.supplier_name for s in vendor_names}
	for vname, v in vendor_map.items():
		if vname != "(Unassigned)":
			v["vendor_name"] = name_lookup.get(vname, vname)

	# Sort: real vendors first (alpha by display name), then unassigned
	ordered = sorted(
		vendor_map.values(),
		key=lambda v: (v["vendor"] == "(Unassigned)", (v["vendor_name"] or "").casefold()),
	)
	total = len(ordered)
	page_slice = ordered[limit_start : limit_start + page_size]

	# Coerce numerics for JSON
	for v in page_slice:
		v["total_value"] = round(v["total_value"], 2)
		v["min_price"] = round(v["min_price"] or 0, 2)
		v["max_price"] = round(v["max_price"] or 0, 2)

	return {
		"success": True,
		"vendors": page_slice,
		"total": total,
		"page": page,
		"page_size": page_size,
	}


@frappe.whitelist(allow_guest=False)
@rate_limit(limit=100, seconds=60)
def get_catalog_items(
	vendor: str | None = None,
	source: str | None = None,
	page: int = 1,
	page_size: int = 50,
	search: str | None = None,
) -> dict:
	"""List items belonging to a specific vendor (or source).

	Used by the Catalogs page drill-down modal.
	"""
	frappe.has_permission("Item", ptype="read", throw=True)

	page = max(1, int(page or 1))
	page_size = min(200, max(1, int(page_size or 50)))
	limit_start = (page - 1) * page_size

	if not vendor and not source:
		frappe.throw(frappe._("Either vendor or source is required"))

	filters = [["Item", "disabled", "=", 0]]
	if vendor and vendor != "(Unassigned)":
		filters.append(["Item", "custom_vendor", "=", vendor])
	if source:
		filters.append(["Item", "custom_source", "=", source])
	if search:
		search = _sanitize_search(search)
		if search:
			filters.append(["Item", "item_name", "like", f"%{search}%"])

	items = frappe.get_all(
		"Item",
		filters=filters,
		fields=[
			"name",
			"item_name",
			"item_group",
			"brand",
			"image",
			"custom_vendor",
			"custom_source",
			"custom_metal_type",
			"custom_purity",
			"custom_msrp",
			"standard_rate",
		],
		order_by="item_name asc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Item", filters=filters)

	for it in items:
		it["price"] = float(it.custom_msrp or it.standard_rate or 0)

	return {
		"success": True,
		"items": items,
		"total": total,
		"page": page,
		"page_size": page_size,
		"vendor": vendor,
		"source": source,
	}


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
	price_data = {}
	try:
		price_data = get_item_price(item_code) or {}
	except Exception:
		price_data = {}
	price = price_data.get("final_price") or item.custom_msrp or item.standard_rate or 0

	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"item_group": item.item_group,
		"category": item.item_group,
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
		"vendor": item.custom_vendor,
		"vendor_sku": item.custom_vendor_sku,
		"gemstones": gemstones,
		"custom_source": item.custom_source,
		"price": price,
		"final_price": price,
		"price_source": price_data.get("price_source") or ("MSRP" if item.custom_msrp else "Standard Rate"),
		"gold_rate": price_data.get("gold_rate", 0),
		"gold_value": price_data.get("gold_value", 0),
		"gemstone_value": price_data.get("gemstone_value", 0),
		"msrp": item.custom_msrp,
		"standard_rate": item.standard_rate,
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


@frappe.whitelist()
def get_warehouse_list() -> list:
	"""Return non-group warehouses for the POS store selector.

	Uses ``ignore_permissions`` so that Employees (who may not have Warehouse
	read permission at the DocType level) can still populate the store
	selector in the app shell.
	"""
	warehouses = frappe.get_all(
		"Warehouse",
		filters={"is_group": 0, "parent_warehouse": ["like", "%ZFJ"]},
		fields=["name", "warehouse_name", "parent_warehouse"],
		order_by="name",
		ignore_permissions=True,
	)

	if not warehouses:
		# Fallback: any non-group warehouse whose name ends with the company suffix
		warehouses = frappe.get_all(
			"Warehouse",
			filters={"is_group": 0, "name": ["like", "%- ZFJ"]},
			fields=["name", "warehouse_name", "parent_warehouse"],
			order_by="name",
			limit_page_length=50,
			ignore_permissions=True,
		)

	return warehouses
