"""
Sales Pricing Indexer - Serializes Sale Cost Breakdown records for ChromaDB.

Converts cost breakdown data into searchable text documents with rich metadata
for the RAG pricing recommendation engine.
"""

import frappe
from frappe.utils import flt


def serialize_sale_cost_breakdown(breakdown_name: str) -> dict:
	"""Serialize a Sale Cost Breakdown into searchable text + metadata for vector embedding.

	Returns:
		Dict with keys: id, text, metadata
	"""
	bd = frappe.get_doc("Sale Cost Breakdown", breakdown_name)

	# Enrich with item-level details from the linked Sales Invoice
	items_info = []
	jewelry_types = set()
	metal_types = set()
	purities = set()

	if bd.sales_invoice:
		invoice_items = frappe.get_all(
			"Sales Invoice Item",
			filters={"parent": bd.sales_invoice},
			fields=["item_code", "item_name", "qty", "rate", "amount"],
		)
		for inv_item in invoice_items:
			item_meta = frappe.get_cached_value(
				"Item",
				inv_item.item_code,
				[
					"custom_jewelry_type",
					"custom_metal_type",
					"custom_purity",
					"custom_net_weight_g",
					"custom_jewelry_subtype",
				],
				as_dict=True,
			)
			info = {
				"item_code": inv_item.item_code,
				"item_name": inv_item.item_name,
				"qty": flt(inv_item.qty),
				"rate": flt(inv_item.rate),
				"amount": flt(inv_item.amount),
			}
			if item_meta:
				info["jewelry_type"] = item_meta.custom_jewelry_type or ""
				info["metal_type"] = item_meta.custom_metal_type or ""
				info["purity"] = item_meta.custom_purity or ""
				info["net_weight_g"] = flt(item_meta.custom_net_weight_g)
				info["subtype"] = item_meta.custom_jewelry_subtype or ""

				if item_meta.custom_jewelry_type:
					jewelry_types.add(item_meta.custom_jewelry_type)
				if item_meta.custom_metal_type:
					metal_types.add(item_meta.custom_metal_type)
				if item_meta.custom_purity:
					purities.add(item_meta.custom_purity)

			items_info.append(info)

	# Build searchable text
	parts = [
		f"Sale {bd.sales_invoice}",
		f"Date: {bd.posting_date}",
		f"Revenue: ${flt(bd.total_revenue):,.2f}",
		f"Total Cost: ${flt(bd.total_cost):,.2f}",
		f"Gross Profit: ${flt(bd.gross_profit):,.2f}",
		f"Margin: {flt(bd.gross_margin_pct):.1f}%",
	]

	if bd.gold_rate_at_sale:
		parts.append(f"Gold Rate at Sale: ${flt(bd.gold_rate_at_sale):.2f}/g")
	if flt(bd.total_metal_cogs):
		parts.append(f"Metal COGS: ${flt(bd.total_metal_cogs):,.2f}")
	if flt(bd.total_gemstone_cogs):
		parts.append(f"Gemstone COGS: ${flt(bd.total_gemstone_cogs):,.2f}")
	if flt(bd.total_labor_cost):
		parts.append(f"Labor Cost: ${flt(bd.total_labor_cost):,.2f}")
	if flt(bd.total_commission):
		parts.append(f"Commission: ${flt(bd.total_commission):,.2f}")
	if flt(bd.total_payment_cost):
		parts.append(f"Payment Cost: ${flt(bd.total_payment_cost):,.2f}")
	if flt(bd.overhead_per_invoice):
		parts.append(f"Overhead: ${flt(bd.overhead_per_invoice):,.2f} ({bd.overhead_method})")

	if jewelry_types:
		parts.append(f"Jewelry Types: {', '.join(jewelry_types)}")
	if metal_types:
		parts.append(f"Metals: {', '.join(metal_types)}")
	if purities:
		parts.append(f"Purities: {', '.join(purities)}")

	# Add item summary
	for item in items_info[:5]:  # Top 5 items
		desc = f"Item: {item.get('item_name', '')} - ${flt(item.get('amount', 0)):,.2f}"
		if item.get("jewelry_type"):
			desc += f" ({item['jewelry_type']}"
			if item.get("metal_type"):
				desc += f", {item['metal_type']}"
			desc += ")"
		parts.append(desc)

	text = ". ".join(parts)

	metadata = {
		"doctype": "Sale Cost Breakdown",
		"source": "sales_pricing",
		"posting_date": str(bd.posting_date) if bd.posting_date else "",
		"revenue": flt(bd.total_revenue),
		"total_cost": flt(bd.total_cost),
		"margin_pct": flt(bd.gross_margin_pct),
		"gold_rate": flt(bd.gold_rate_at_sale) if bd.gold_rate_at_sale else 0,
		"jewelry_types": list(jewelry_types),
		"metal_types": list(metal_types),
		"purities": list(purities),
		"item_count": len(items_info),
	}

	return {"id": bd.name, "text": text, "metadata": metadata}
