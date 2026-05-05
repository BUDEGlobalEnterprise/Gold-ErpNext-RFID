"""
Doc Event Hooks for RAG Indexing

These handlers are called by Frappe's doc_events system whenever
a document is created, updated, or deleted. They keep the ChromaDB
vector store in sync with the MariaDB data.
"""

import frappe


def on_item_update(doc, method=None):
	"""Re-index an Item when it's updated."""
	_enqueue_index("Item", doc.name)


def on_item_trash(doc, method=None):
	"""Remove an Item from the vector store when it's deleted."""
	_enqueue_remove("Item", doc.name)


def on_customer_update(doc, method=None):
	"""Re-index a Customer when updated."""
	_enqueue_index("Customer", doc.name)


def on_repair_update(doc, method=None):
	"""Re-index a Repair Order when updated."""
	_enqueue_index("Repair Order", doc.name)


def on_repair_submit(doc, method=None):
	"""Re-index a Repair Order when submitted."""
	_enqueue_index("Repair Order", doc.name)


def on_article_update(doc, method=None):
	"""Re-index a Knowledge Article when updated."""
	_enqueue_index("RAG Knowledge Article", doc.name)


def on_article_trash(doc, method=None):
	"""Remove a Knowledge Article from the vector store."""
	_enqueue_remove("RAG Knowledge Article", doc.name)


def _enqueue_index(doctype, name):
	"""Queue a document for indexing on the long worker."""
	frappe.enqueue(
		"zevar_core.rag.indexing.pipeline.IndexingPipeline.index_document",
		doctype=doctype,
		name=name,
		queue="long",
		timeout=300,
	)


def _enqueue_remove(doctype, name):
	"""Queue a document for removal from the vector store."""
	frappe.enqueue(
		"zevar_core.rag.indexing.pipeline.IndexingPipeline.remove_document",
		doctype=doctype,
		name=name,
		queue="long",
		timeout=60,
	)
