"""
Pricing Retriever - Specialized retrieval functions for the pricing domain.

Provides functions to find similar pricing events, analyze elasticity,
detect seasonal patterns, and correlate gold rate changes with margins.
"""

import frappe
from frappe.utils import add_days, flt, getdate, today

from zevar_core.rag.config import COLLECTION_SALES_PRICING


def find_similar_pricing_events(
	jewelry_type: str,
	metal_type: str = "",
	purity: str = "",
	price_range: tuple | None = None,
	top_k: int = 10,
) -> list[dict]:
	"""Find historical sales of similar jewelry at similar prices from ChromaDB.

	Args:
		jewelry_type: e.g., "Ring", "Necklace", "Chain"
		metal_type: e.g., "Yellow Gold", "Silver"
		purity: e.g., "14Kt", "18Kt", "22Kt"
		price_range: Optional (min_price, max_price) tuple
		top_k: Number of results to return

	Returns:
		List of dicts with price, margin, gold_rate, date, jewelry_type
	"""
	from zevar_core.rag.retrieval.vector_search import VectorSearch

	search = VectorSearch()

	# Build a descriptive query string for vector search
	query_parts = [f"{jewelry_type}"]
	if metal_type:
		query_parts.append(metal_type)
	if purity:
		query_parts.append(purity)
	query_parts.append("sale margin pricing")
	query_text = " ".join(query_parts)

	results = search.search(
		collection_name=COLLECTION_SALES_PRICING,
		query_text=query_text,
		top_k=top_k,
	)

	# Filter by metadata if provided
	filtered = []
	for r in results:
		meta = r.get("metadata", {})
		# Check jewelry type match
		jt_list = meta.get("jewelry_types", [])
		if jewelry_type and jt_list and jewelry_type not in str(jt_list):
			continue
		# Check metal type match
		mt_list = meta.get("metal_types", [])
		if metal_type and mt_list and metal_type not in str(mt_list):
			continue
		# Check price range
		if price_range:
			rev = flt(meta.get("revenue", 0))
			if rev < price_range[0] or rev > price_range[1]:
				continue

		filtered.append(
			{
				"id": r.get("id"),
				"date": meta.get("posting_date", ""),
				"revenue": flt(meta.get("revenue")),
				"total_cost": flt(meta.get("total_cost")),
				"margin_pct": flt(meta.get("margin_pct")),
				"gold_rate": flt(meta.get("gold_rate")),
				"jewelry_types": meta.get("jewelry_types", []),
				"metal_types": meta.get("metal_types", []),
				"similarity": r.get("similarity", 0),
			}
		)

	return filtered


def get_elasticity_signals(jewelry_type: str, months: int = 12) -> list[dict]:
	"""Analyze how discount levels affect margins for a jewelry type.

	Uses direct SQL (not vector search) for precise numerical analysis.

	Returns:
		List of dicts with discount_pct, avg_margin, volume, revenue
	"""
	since = add_days(today(), -int(months) * 30)

	results = frappe.db.sql(
		"""SELECT
			CASE
				WHEN si.discount_amount = 0 THEN 0
				WHEN si.base_net_total + si.discount_amount > 0
					THEN ROUND((si.discount_amount / (si.base_net_total + si.discount_amount)) * 100 / 5) * 5
				ELSE 0
			END as discount_bucket,
			AVG(scb.gross_margin_pct) as avg_margin,
			COUNT(*) as volume,
			SUM(scb.total_revenue) as total_revenue
		FROM `tabSale Cost Breakdown` scb
		JOIN `tabSales Invoice` si ON scb.sales_invoice = si.name
		JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		JOIN `tabItem` i ON i.name = sii.item_code
		WHERE scb.posting_date >= %s
		AND i.custom_jewelry_type = %s
		GROUP BY discount_bucket
		ORDER BY discount_bucket""",
		(since, jewelry_type),
		as_dict=True,
	)

	return [
		{
			"discount_pct": flt(r.discount_bucket),
			"avg_margin": flt(r.avg_margin, 2),
			"volume": r.volume,
			"revenue": flt(r.total_revenue),
		}
		for r in results
	]


def get_seasonal_patterns(jewelry_type: str | None = None) -> list[dict]:
	"""Detect seasonal pricing patterns from historical data.

	Returns:
		List of dicts with month, avg_margin, volume, avg_revenue
	"""
	filters_sql = ""
	params = []

	if jewelry_type:
		filters_sql = """JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
			JOIN `tabItem` i ON i.name = sii.item_code
			WHERE i.custom_jewelry_type = %s AND"""
		params = [jewelry_type]
	else:
		filters_sql = "WHERE"

	results = frappe.db.sql(
		f"""SELECT
			MONTH(scb.posting_date) as month,
			MONTHNAME(scb.posting_date) as month_name,
			AVG(scb.gross_margin_pct) as avg_margin,
			COUNT(*) as volume,
			AVG(scb.total_revenue) as avg_revenue
		FROM `tabSale Cost Breakdown` scb
		JOIN `tabSales Invoice` si ON scb.sales_invoice = si.name
		{filters_sql} scb.docstatus = 1
		GROUP BY MONTH(scb.posting_date)
		ORDER BY MONTH(scb.posting_date)""",
		params,
		as_dict=True,
	)

	return [
		{
			"month": r.month,
			"month_name": r.month_name,
			"avg_margin": flt(r.avg_margin, 2),
			"volume": r.volume,
			"avg_revenue": flt(r.avg_revenue, 2),
		}
		for r in results
	]


def get_gold_rate_correlation(months: int = 6) -> list[dict]:
	"""Correlate gold rate changes with margin changes over time.

	Returns:
		List of dicts with period, avg_gold_rate, avg_margin, margin_change, revenue
	"""
	since = add_days(today(), -int(months) * 30)

	results = frappe.db.sql(
		"""SELECT
			DATE_FORMAT(scb.posting_date, '%%Y-%%m') as period,
			AVG(scb.gold_rate_at_sale) as avg_gold_rate,
			AVG(scb.gross_margin_pct) as avg_margin,
			SUM(scb.total_revenue) as revenue,
			COUNT(*) as invoice_count
		FROM `tabSale Cost Breakdown` scb
		WHERE scb.posting_date >= %s AND scb.gold_rate_at_sale > 0
		GROUP BY period
		ORDER BY period""",
		(since,),
		as_dict=True,
	)

	# Calculate period-over-period margin change
	enriched = []
	for i, r in enumerate(results):
		prev_margin = flt(results[i - 1]["avg_margin"]) if i > 0 else flt(r.avg_margin)
		enriched.append(
			{
				"period": r.period,
				"avg_gold_rate": flt(r.avg_gold_rate, 2),
				"avg_margin": flt(r.avg_margin, 2),
				"margin_change": flt(flt(r.avg_margin) - prev_margin, 2),
				"revenue": flt(r.revenue),
				"invoice_count": r.invoice_count,
			}
		)

	return enriched
