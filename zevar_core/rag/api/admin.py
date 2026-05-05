"""
RAG Admin API - Index management and monitoring endpoints.

System Manager only endpoints for managing the RAG index.
"""

import time

import frappe

from zevar_core.rag.indexing.pipeline import IndexingPipeline
from zevar_core.rag.indexing.store import VectorStore


@frappe.whitelist(methods=["POST"])
def rebuild_index(collection: str = "all") -> dict:
	"""Rebuild a vector index from scratch.

	Args:
		collection: Collection name or "all" to rebuild everything.
			Options: "products", "customers", "knowledge", "all"

	Returns:
		Dict with rebuild status and counts.
	"""
	frappe.only_for("System Manager")

	pipeline = IndexingPipeline()
	collection_map = {
		"products": "Item",
		"customers": "Customer",
		"knowledge": "RAG Knowledge Article",
	}

	if collection == "all":
		results = pipeline.rebuild_all()
		return {"status": "success", "rebuilt": results}

	doctype = collection_map.get(collection)
	if not doctype:
		frappe.throw(f"Unknown collection '{collection}'. Use: products, customers, knowledge, or all.")

	count = pipeline.rebuild_collection(doctype)
	return {"status": "success", "collection": collection, "documents_indexed": count}


@frappe.whitelist()
def get_index_stats() -> dict:
	"""Get statistics for all RAG collections.

	Returns:
		Dict with collection stats.
	"""
	frappe.only_for("System Manager")

	store = VectorStore()
	stats = store.get_all_collection_stats()

	# Add database counts for comparison
	db_counts = {
		"Item": frappe.db.count("Item", filters={"disabled": 0, "has_variants": 0}),
		"Customer": frappe.db.count("Customer"),
		"RAG Knowledge Article": frappe.db.count("RAG Knowledge Article", filters={"is_active": 1}),
	}

	return {
		"collections": stats,
		"database_counts": db_counts,
		"status": "ok",
	}


@frappe.whitelist(methods=["POST"])
def index_document(doctype: str, name: str) -> dict:
	"""Manually index or re-index a single document.

	Args:
		doctype: DocType name (Item, Customer, RAG Knowledge Article)
		name: Document name/ID

	Returns:
		Dict with indexing status.
	"""
	frappe.only_for("System Manager")

	if doctype not in ("Item", "Customer", "RAG Knowledge Article"):
		frappe.throw(f"RAG indexing not supported for '{doctype}'.")

	# Verify document exists
	if not frappe.db.exists(doctype, name):
		frappe.throw(f"{doctype} '{name}' not found.")

	start = time.time()
	pipeline = IndexingPipeline()
	pipeline.index_document(doctype, name)
	latency = int((time.time() - start) * 1000)

	return {"status": "indexed", "doctype": doctype, "name": name, "latency_ms": latency}


@frappe.whitelist(methods=["POST"])
def reconcile() -> dict:
	"""Manually trigger index reconciliation.

	Compares ChromaDB counts with MariaDB counts and re-indexes mismatches.

	Returns:
		Dict with reconciliation results.
	"""
	frappe.only_for("System Manager")

	from zevar_core.rag.hooks.scheduler import reconcile_indexes

	reconcile_indexes()
	return {"status": "reconciliation_complete"}
