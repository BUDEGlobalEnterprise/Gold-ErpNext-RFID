"""
DocType-to-Text Serializers

Convert Frappe DocType records into natural language text suitable for
embedding. Each DocType has a dedicated serializer that extracts the most
searchable fields and formats them as readable descriptions.
"""

import frappe


def serialize_item(item_code: str) -> dict:
	"""Serialize an Item DocType into searchable text + metadata.

	Returns:
		Dict with keys: id, text, metadata
	"""
	item = frappe.get_doc("Item", item_code)

	# Fetch stock quantity (aggregate across all warehouses)
	stock_qty = 0.0
	bins = frappe.db.get_all("Bin", filters={"item_code": item_code}, fields=["actual_qty"])
	for b in bins:
		stock_qty += float(b.actual_qty or 0)

	# Fetch gemstone summary
	gemstones = []
	if hasattr(item, "gemstones"):
		for gem in item.gemstones:
			parts = []
			if gem.gem_type:
				parts.append(gem.gem_type)
			if gem.carat:
				parts.append(f"{gem.carat}ct")
			if gem.count:
				parts.append(f"x{gem.count}")
			if parts:
				gemstones.append(" ".join(parts))

	# Build searchable text
	parts = [item.item_name]

	if item.custom_jewelry_type:
		parts.append(f"Type: {item.custom_jewelry_type}")
	if item.custom_jewelry_subtype:
		parts.append(f"Subtype: {item.custom_jewelry_subtype}")

	metal_desc = []
	if item.custom_metal_type:
		metal_desc.append(item.custom_metal_type)
	if item.custom_purity:
		metal_desc.append(item.custom_purity)
	if metal_desc:
		parts.append(f"Metal: {' '.join(metal_desc)}")

	if item.custom_net_weight_g:
		parts.append(f"Weight: {item.custom_net_weight_g}g")
	if item.custom_msrp:
		parts.append(f"MSRP: ${float(item.custom_msrp):,.2f}")

	if gemstones:
		parts.append(f"Stones: {', '.join(gemstones)}")

	if item.description:
		# Truncate long descriptions
		desc = item.description.strip()[:300]
		parts.append(f"Description: {desc}")

	if item.custom_gender:
		parts.append(f"For: {item.custom_gender}")
	if item.custom_size:
		parts.append(f"Size: {item.custom_size}")
	if item.custom_finish:
		parts.append(f"Finish: {item.custom_finish}")
	if item.custom_source:
		parts.append(f"Source: {item.custom_source}")

	parts.append(f"In stock: {int(stock_qty)} units")

	text = ". ".join(parts)

	metadata = {
		"doctype": "Item",
		"item_code": item.name,
		"item_name": item.item_name or "",
		"jewelry_type": item.custom_jewelry_type or "",
		"metal_type": item.custom_metal_type or "",
		"purity": item.custom_purity or "",
		"has_gemstones": bool(gemstones),
		"in_stock": stock_qty > 0,
		"source": "item",
	}

	if item.custom_msrp:
		metadata["msrp"] = float(item.custom_msrp)
	if item.custom_gender:
		metadata["gender"] = item.custom_gender

	return {"id": item.name, "text": text, "metadata": metadata}


def serialize_customer(customer_id: str) -> dict:
	"""Serialize a Customer DocType into searchable text + metadata.

	NOTE: Excludes PII (phone, email, SSN) from embeddings.
	Only non-identifying preference data is embedded.

	Returns:
		Dict with keys: id, text, metadata
	"""
	customer = frappe.get_doc("Customer", customer_id)

	parts = [customer.customer_name]

	if customer.customer_type:
		parts.append(f"Type: {customer.customer_type}")

	if customer.customer_group:
		parts.append(f"Group: {customer.customer_group}")

	# Purchase summary (non-PII)
	si_count = frappe.db.count(
		"Sales Invoice",
		filters={"customer": customer_id, "docstatus": 1},
	)
	if si_count:
		parts.append(f"Total orders: {si_count}")

		total_spent = frappe.db.sql(
			"""SELECT COALESCE(SUM(grand_total), 0) FROM `tabSales Invoice`
			WHERE customer=%s AND docstatus=1""",
			(customer_id,),
		)[0][0]
		parts.append(f"Total spent: ${float(total_spent):,.2f}")

	# Preferences from custom fields (non-PII)
	for field, label in [
		("custom_preferred_metal", "Preferred metal"),
		("custom_preferred_purity", "Preferred purity"),
		("custom_preferred_jewelry_type", "Preferred jewelry type"),
		("custom_ring_size", "Ring size"),
		("custom_gender", "Gender"),
	]:
		val = getattr(customer, field, None)
		if val:
			parts.append(f"{label}: {val}")

	# Top purchased item types (non-PII behavioral signal)
	try:
		top_items = frappe.db.sql(
			"""SELECT i.custom_jewelry_type, COUNT(*) as cnt
			FROM `tabSales Invoice Item` sii
			JOIN `tabItem` i ON i.name = sii.item_code
			JOIN `tabSales Invoice` si ON si.name = sii.parent
			WHERE si.customer=%s AND si.docstatus=1 AND i.custom_jewelry_type IS NOT NULL
			GROUP BY i.custom_jewelry_type ORDER BY cnt DESC LIMIT 3""",
			(customer_id,),
			as_dict=True,
		)
		if top_items:
			types = ", ".join(r.custom_jewelry_type for r in top_items if r.custom_jewelry_type)
			if types:
				parts.append(f"Most purchased types: {types}")
	except Exception:
		pass

	text = ". ".join(parts)

	metadata = {
		"doctype": "Customer",
		"customer_id": customer.name,
		"customer_name": customer.customer_name or "",
		"customer_type": customer.customer_type or "",
		"source": "customer",
	}

	# Add preference metadata for filtering
	for field, key in [
		("custom_preferred_metal", "preferred_metal"),
		("custom_preferred_purity", "preferred_purity"),
		("custom_preferred_jewelry_type", "preferred_jewelry_type"),
		("custom_ring_size", "ring_size"),
	]:
		val = getattr(customer, field, None)
		if val:
			metadata[key] = val

	return {"id": customer.name, "text": text, "metadata": metadata}


def serialize_knowledge_article(article_id: str) -> dict:
	"""Serialize a RAG Knowledge Article into chunked text + metadata.

	Returns:
		Dict with keys: id, text, metadata
	"""
	article = frappe.get_doc("RAG Knowledge Article", article_id)

	# Title + category + content
	text_parts = [f"Title: {article.title}"]
	if article.category:
		text_parts.append(f"Category: {article.category}")
	text_parts.append(f"Content: {article.content}")

	text = ". ".join(text_parts)

	metadata = {
		"doctype": "RAG Knowledge Article",
		"article_id": article.name,
		"title": article.title,
		"category": article.category or "",
		"visibility": article.visibility or "Internal",
		"source": "knowledge",
	}

	if article.tags:
		metadata["tags"] = article.tags

	return {"id": article.name, "text": text, "metadata": metadata}


# Registry: DocType name -> serializer function
SERIALIZERS = {
	"Item": serialize_item,
	"Customer": serialize_customer,
	"RAG Knowledge Article": serialize_knowledge_article,
	"Sale Cost Breakdown": None,  # Registered below to avoid circular import
}

# Late import for sales pricing indexer (depends on Sale Cost Breakdown DocType)
try:
	from zevar_core.rag.indexing.sales_pricing_indexer import serialize_sale_cost_breakdown

	SERIALIZERS["Sale Cost Breakdown"] = serialize_sale_cost_breakdown
except ImportError:
	pass
