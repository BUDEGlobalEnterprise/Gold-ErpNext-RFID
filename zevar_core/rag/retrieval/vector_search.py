"""
Vector Search - ChromaDB similarity search with filtering.

Wraps ChromaDB query operations with Zever-specific defaults
and result formatting.
"""

import logging

from zevar_core.rag.config import (
	COLLECTION_CUSTOMERS,
	COLLECTION_KNOWLEDGE,
	COLLECTION_PRODUCTS,
	DEFAULT_TOP_K,
	SIMILARITY_THRESHOLD,
)
from zevar_core.rag.embedding.manager import EmbeddingManager
from zevar_core.rag.indexing.store import VectorStore

log = logging.getLogger(__name__)

# Collection name → domain label
COLLECTION_DOMAINS = {
	COLLECTION_PRODUCTS: "product",
	COLLECTION_CUSTOMERS: "customer",
	COLLECTION_KNOWLEDGE: "policy",
}


def search(
	query: str,
	collections: list[str] | None = None,
	top_k: int = DEFAULT_TOP_K,
	filters: dict | None = None,
) -> list[dict]:
	"""Run a vector similarity search across one or more collections.

	Args:
		query: Natural language query string.
		collections: List of collection names to search. Defaults to all.
		top_k: Number of results per collection.
		filters: ChromaDB metadata filters (where clause).

	Returns:
		List of result dicts sorted by relevance (distance).
	"""
	embedding_mgr = EmbeddingManager()
	store = VectorStore()

	query_embedding = embedding_mgr.embed_single(query)
	if not query_embedding:
		return []

	if collections is None:
		collections = [COLLECTION_PRODUCTS, COLLECTION_CUSTOMERS, COLLECTION_KNOWLEDGE]

	all_results = []

	for coll_name in collections:
		try:
			raw = store.query(
				collection_name=coll_name,
				query_embedding=query_embedding,
				n_results=top_k,
				where=filters,
			)

			if not raw or not raw.get("ids") or not raw["ids"][0]:
				continue

			domain = COLLECTION_DOMAINS.get(coll_name, "general")
			for i, doc_id in enumerate(raw["ids"][0]):
				distance = raw["distances"][0][i]
				# ChromaDB cosine distance: 0 = identical, 2 = opposite
				# Convert to similarity score (0-1)
				similarity = 1.0 - (distance / 2.0)

				if similarity < SIMILARITY_THRESHOLD:
					continue

				metadata = raw["metadatas"][0][i] if raw.get("metadatas") else {}
				document = raw["documents"][0][i] if raw.get("documents") else ""

				all_results.append(
					{
						"id": doc_id,
						"text": document,
						"metadata": metadata,
						"similarity": round(similarity, 4),
						"distance": round(distance, 4),
						"domain": domain,
						"collection": coll_name,
					}
				)
		except Exception:
			log.exception("Vector search failed for collection '%s'", coll_name)
			continue

	# Sort by similarity descending
	all_results.sort(key=lambda r: r["similarity"], reverse=True)
	return all_results


def search_products(query: str, top_k: int = DEFAULT_TOP_K, filters: dict | None = None) -> list[dict]:
	"""Search only the products collection."""
	return search(query, collections=[COLLECTION_PRODUCTS], top_k=top_k, filters=filters)


def search_customers(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
	"""Search only the customers collection."""
	return search(query, collections=[COLLECTION_CUSTOMERS], top_k=top_k)


def search_knowledge(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
	"""Search only the knowledge base collection."""
	return search(query, collections=[COLLECTION_KNOWLEDGE], top_k=top_k)
