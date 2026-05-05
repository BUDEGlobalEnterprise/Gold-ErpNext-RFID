"""
Hybrid Search - Combines vector similarity search with keyword text search.

Uses Reciprocal Rank Fusion (RRF) to merge results from:
1. ChromaDB vector similarity search (semantic)
2. Frappe global search (keyword/lexical)

This produces better results than either method alone, especially for
queries that mix specific terms with semantic intent.
"""

import logging

import frappe

from zevar_core.rag.retrieval.vector_search import search as vector_search

log = logging.getLogger(__name__)


def hybrid_search(
	query: str,
	collections: list[str] | None = None,
	top_k: int = 10,
	rrf_k: int = 60,
) -> list[dict]:
	"""Run a hybrid search combining vector and keyword results.

	Args:
		query: Natural language query string.
		collections: Collections to search (defaults to all).
		top_k: Number of final results to return.
		rrf_k: RRF constant (default 60, lower = more weight on top ranks).

	Returns:
		List of result dicts sorted by RRF score.
	"""
	# Run both searches in parallel
	vector_results = vector_search(query, collections=collections, top_k=top_k)
	keyword_results = _keyword_search(query, top_k=top_k)

	if not keyword_results:
		return vector_results[:top_k]

	if not vector_results:
		return keyword_results[:top_k]

	# Merge using Reciprocal Rank Fusion
	rrf_scores = {}

	# Score vector results by rank
	for rank, result in enumerate(vector_results):
		doc_id = result.get("id", "")
		rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (rrf_k + rank + 1)
		# Store the result object
		if doc_id not in rrf_scores:
			rrf_scores[f"_obj_{doc_id}"] = result

	# Score keyword results by rank
	for rank, result in enumerate(keyword_results):
		doc_id = result.get("id", "")
		rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (rrf_k + rank + 1)
		if f"_obj_{doc_id}" not in rrf_scores:
			rrf_scores[f"_obj_{doc_id}"] = result

	# Build merged results
	merged = {}
	for doc_id, score in rrf_scores.items():
		if doc_id.startswith("_obj_"):
			continue
		obj = rrf_scores.get(f"_obj_{doc_id}", {})
		obj["rrf_score"] = round(score, 6)
		merged[doc_id] = obj

	# Sort by RRF score descending
	sorted_results = sorted(merged.values(), key=lambda r: r.get("rrf_score", 0), reverse=True)
	return sorted_results[:top_k]


def _keyword_search(query: str, top_k: int = 10) -> list[dict]:
	"""Run a Frappe global search for keyword matching.

	Returns results in the same format as vector search.
	"""
	results = []
	try:
		# Use Frappe's built-in global search
		from frappe.utils.global_search import search as global_search

		search_results = global_search(query, limit=top_k * 2)

		for rank, r in enumerate(search_results):
			results.append(
				{
					"id": r.get("name", ""),
					"text": r.get("content", "")[:500],
					"metadata": {
						"doctype": r.get("doctype", ""),
						"title": r.get("title", ""),
						"source": "keyword",
					},
					"similarity": 0.5,  # Default for keyword matches
					"domain": "general",
					"collection": "keyword",
					"keyword_rank": rank,
				}
			)
	except Exception:
		log.debug("Keyword search unavailable, using vector-only results")

	return results
