"""
Query Classifier - Detects the domain of a user query.

Uses keyword matching to determine whether a query is about
products, customers, repairs, policies, or is general.
"""

from zevar_core.rag.config import QUERY_DOMAINS


def classify(query: str) -> str:
	"""Classify a query into a domain.

	Args:
		query: Natural language query string.

	Returns:
		Domain string: "product", "customer", "repair", "policy", or "general"
	"""
	query_lower = query.lower()

	# Score each domain by keyword matches
	scores = {}
	for domain, keywords in QUERY_DOMAINS.items():
		if domain == "general":
			continue
		score = sum(1 for kw in keywords if kw in query_lower)
		if score > 0:
			scores[domain] = score

	if not scores:
		return "general"

	# Return the domain with the highest score
	return max(scores, key=scores.get)


def get_search_collections(domain: str) -> list[str]:
	"""Map a classified domain to the ChromaDB collections to search.

	Args:
		domain: Query domain from classify().

	Returns:
		List of collection names to search.
	"""
	from zevar_core.rag.config import (
		COLLECTION_CUSTOMERS,
		COLLECTION_KNOWLEDGE,
		COLLECTION_PRODUCTS,
	)

	mapping = {
		"product": [COLLECTION_PRODUCTS],
		"customer": [COLLECTION_CUSTOMERS, COLLECTION_PRODUCTS],
		"repair": [COLLECTION_KNOWLEDGE, COLLECTION_PRODUCTS],
		"policy": [COLLECTION_KNOWLEDGE],
		"general": [COLLECTION_PRODUCTS, COLLECTION_KNOWLEDGE, COLLECTION_CUSTOMERS],
	}

	return mapping.get(domain, mapping["general"])
