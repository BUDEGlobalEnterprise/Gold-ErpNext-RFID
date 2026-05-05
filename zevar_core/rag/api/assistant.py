"""
RAG Assistant API - Natural language search, Q&A, and recommendations.

Provides the main user-facing API for the RAG system:
- search_products: Natural language product search via vector similarity
- ask: General RAG Q&A with LLM-generated answers and source attribution
- get_recommendations: Customer-aware product recommendations
"""

import time

import frappe
from frappe.rate_limiter import rate_limit

from zevar_core.rag.generation.response_builder import ResponseBuilder
from zevar_core.rag.retrieval.recommender import get_customer_profile, recommend_for_customer
from zevar_core.rag.retrieval.vector_search import search_products as _search_products


def _check_rag_rate_limit():
	"""Rate limit RAG queries: 30 per minute per user."""
	key = f"rag_rate_limit:{frappe.session.user}"
	current = frappe.cache().get_value(key) or 0
	if current >= 30:
		frappe.throw("Rate limit exceeded. Please wait a moment before trying again.")
	frappe.cache().set_value(key, current + 1, expires_in_sec=60)


def _log_query(query: str, query_type: str, answer: str | None, sources: list, confidence: float | None = None, latency_ms: int | None = None, provider: str | None = None):
	"""Log a RAG query to the audit DocType."""
	try:
		log = frappe.get_doc(
			{
				"doctype": "RAG Query Log",
				"query": query[:500],
				"query_type": query_type,
				"user": frappe.session.user,
				"answer": (answer or "")[:2000],
				"sources": frappe.as_json(sources[:5]),
				"confidence_score": confidence,
				"latency_ms": latency_ms,
				"llm_provider": provider or "",
			}
		)
		log.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error("RAG Query Log Error")


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60)
def search_products(query: str, limit: int = 20) -> dict:
	"""Natural language product search.

	Uses vector similarity to find products matching the query description.

	Args:
		query: Natural language search (e.g., "gold necklaces under $500")
		limit: Max results to return

	Returns:
		Dict with results, total count, and latency.
	"""
	if not query or len(query.strip()) < 2:
		return {"results": [], "total": 0}

	query = query.strip()[:200]
	limit = min(int(limit), 50)

	start = time.time()
	results = _search_products(query, top_k=limit)
	latency = int((time.time() - start) * 1000)

	# Enrich results with live data from MariaDB
	enriched = []
	for r in results:
		item = _enrich_product_result(r)
		if item:
			enriched.append(item)

	return {
		"results": enriched,
		"total": len(enriched),
		"query": query,
		"latency_ms": latency,
	}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=20, seconds=60)
def ask(question: str, context_type: str | None = None, customer: str | None = None) -> dict:
	"""General RAG Q&A endpoint with LLM-generated answers.

	Retrieves relevant context, generates an answer using the LLM
	(GLM or Qwen based on domain), and returns with source attribution.

	Optionally includes customer context for personalized responses.

	Args:
		question: Natural language question
		context_type: Optional domain hint (product/customer/policy/repair/general)
		customer: Optional customer ID to add customer context

	Returns:
		Dict with answer, sources, query_id, domain, confidence, provider.
	"""
	if not question or len(question.strip()) < 3:
		frappe.throw("Question is too short. Please provide more detail.")

	question = question.strip()[:500]

	# Add customer context to the question if provided
	customer_context = None
	if customer:
		customer_context = _get_customer_context(customer)
		if customer_context:
			question = f"{question}\n\nCustomer context: {customer_context}"
			if not context_type:
				context_type = "customer"

	# Use ResponseBuilder which handles: classify -> retrieve -> generate
	builder = ResponseBuilder()
	response = builder.build(question, context_type=context_type, mask_pii=bool(customer))

	# Log the query
	query_id = None
	try:
		_log_query(
			query=question[:500],
			query_type=response["domain"],
			answer=response["answer"],
			sources=response.get("sources", []),
			confidence=response.get("confidence"),
			latency_ms=response.get("latency_ms"),
			provider=response.get("provider"),
		)
		query_id = frappe.db.get_value(
			"RAG Query Log", {"user": frappe.session.user}, ["name"], order_by="creation desc"
		)
	except Exception:
		pass

	return {
		"answer": response["answer"],
		"sources": response.get("sources", []),
		"query_id": query_id,
		"domain": response["domain"],
		"confidence": response.get("confidence", 0),
		"provider": response.get("provider", ""),
		"latency_ms": response.get("latency_ms", 0),
	}


@frappe.whitelist()
@rate_limit(limit=20, seconds=60)
def get_recommendations(customer: str, occasion: str | None = None, limit: int = 5) -> dict:
	"""Get personalized product recommendations for a customer.

	Uses the customer's purchase history and preferences to find
	matching products via vector similarity.

	Args:
		customer: Customer ID
		occasion: Optional occasion (anniversary, birthday, wedding, engagement, etc.)
		limit: Max recommendations (default 5)

	Returns:
		Dict with recommendations, profile summary, and reasoning.
	"""
	# Verify customer access
	from zevar_core.api.customer import _check_pos_customer_role

	_check_pos_customer_role()

	if not frappe.db.exists("Customer", customer):
		frappe.throw(f"Customer '{customer}' not found.")

	limit = min(int(limit), 10)

	start = time.time()
	profile = get_customer_profile(customer)
	recommendations = recommend_for_customer(customer, occasion=occasion, limit=limit)
	latency = int((time.time() - start) * 1000)

	# Log the recommendation query
	try:
		_log_query(
			query=f"Recommendations for {customer}" + (f" ({occasion})" if occasion else ""),
			query_type="customer",
			answer=f"{len(recommendations)} recommendations",
			sources=[],
			latency_ms=latency,
			provider="recommender",
		)
	except Exception:
		pass

	return {
		"customer": customer,
		"customer_name": profile.get("customer_name", ""),
		"occasion": occasion,
		"recommendations": recommendations,
		"profile_summary": {
			"preferences": profile.get("preferences", {}),
			"purchase_summary": {
				"jewelry_types": profile.get("purchase_summary", {}).get("jewelry_types", {}),
				"metals": profile.get("purchase_summary", {}).get("metals", {}),
				"orders": profile.get("purchase_summary", {}).get("spending", {}).get("orders", 0),
			},
		},
		"latency_ms": latency,
	}


def _get_customer_context(customer_id: str) -> str | None:
	"""Build a brief customer context string for the LLM.

	Returns non-PII summary suitable for inclusion in the prompt.
	"""
	try:
		profile = get_customer_profile(customer_id)
	except Exception:
		return None

	prefs = profile.get("preferences", {})
	purchase = profile.get("purchase_summary", {})

	parts = [f"Customer: {profile.get('customer_name', customer_id)}"]

	if prefs.get("preferred_metal"):
		parts.append(f"Preferred metal: {prefs['preferred_metal']}")
	if prefs.get("preferred_purity"):
		parts.append(f"Preferred purity: {prefs['preferred_purity']}")
	if prefs.get("preferred_jewelry_type"):
		parts.append(f"Preferred type: {prefs['preferred_jewelry_type']}")
	if prefs.get("ring_size"):
		parts.append(f"Ring size: {prefs['ring_size']}")

	spending = purchase.get("spending", {})
	if spending:
		parts.append(f"Total orders: {spending.get('orders', 0)}")
		parts.append(f"Average spend: ${spending.get('avg', 0):,.2f}")

	jewelry_types = purchase.get("jewelry_types", {})
	if jewelry_types:
		top_types = list(jewelry_types.keys())[:3]
		parts.append(f"Most bought: {', '.join(top_types)}")

	return ". ".join(parts)


def _enrich_product_result(result: dict) -> dict | None:
	"""Enrich a vector search result with live product data from MariaDB."""
	item_code = result.get("id") or result.get("metadata", {}).get("item_code")
	if not item_code:
		return result

	try:
		item = frappe.db.get_value(
			"Item",
			item_code,
			[
				"name",
				"item_name",
				"image",
				"custom_metal_type",
				"custom_purity",
				"custom_jewelry_type",
				"custom_msrp",
				"custom_gender",
				"custom_source",
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
			"similarity": result.get("similarity", 0),
			"matched_text": result.get("text", ""),
		}
	except Exception:
		return result
