"""
Scheduler Events for RAG System

Nightly reconciliation and maintenance tasks.
"""

import frappe


def reconcile_indexes():
	"""Nightly job: verify ChromaDB counts match MariaDB counts and re-index discrepancies."""
	from zevar_core.rag.indexing.pipeline import IndexingPipeline
	from zevar_core.rag.indexing.store import VectorStore
	from zevar_core.rag.config import DOCTYPE_COLLECTION_MAP

	store = VectorStore()
	pipeline = IndexingPipeline()

	for doctype, collection in DOCTYPE_COLLECTION_MAP.items():
		# Get count from MariaDB
		filters = {}
		if doctype == "Item":
			filters = {"disabled": 0, "has_variants": 0}

		db_count = frappe.db.count(doctype, filters=filters)
		chroma_count = store.get_collection_count(collection)

		if db_count != chroma_count:
			frappe.logger().info(
				"RAG Reconciliation: %s count mismatch (DB=%d, Chroma=%d). Re-indexing.",
				doctype,
				db_count,
				chroma_count,
			)
			pipeline.rebuild_collection(doctype)
		else:
			frappe.logger().info("RAG Reconciliation: %s counts match (%d). OK.", doctype, db_count)
