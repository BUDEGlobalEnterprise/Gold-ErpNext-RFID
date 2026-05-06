"""
Indexing Pipeline

Orchestrates the flow: DocType data -> serialize -> embed -> store in ChromaDB.
Supports single document updates (real-time) and bulk indexing (batch).
"""

import logging

import frappe

from zevar_core.rag.config import BATCH_SIZE, DOCTYPE_COLLECTION_MAP
from zevar_core.rag.embedding.manager import EmbeddingManager
from zevar_core.rag.indexing.serializers import SERIALIZERS
from zevar_core.rag.indexing.store import VectorStore

log = logging.getLogger(__name__)


class IndexingPipeline:
	"""Orchestrates document serialization, embedding, and storage."""

	def __init__(self):
		self.store = VectorStore()
		self.embedding_mgr = EmbeddingManager()

	def index_document(self, doctype: str, name: str):
		"""Index a single document (used by doc_events hooks).

		Args:
			doctype: The DocType name (e.g., "Item", "Customer")
			name: The document name/ID
		"""
		serializer = SERIALIZERS.get(doctype)
		if not serializer:
			log.warning("No serializer for DocType '%s'", doctype)
			return

		collection = DOCTYPE_COLLECTION_MAP.get(doctype)
		if not collection:
			log.warning("No collection mapping for DocType '%s'", doctype)
			return

		try:
			serialized = serializer(name)
			embedding = self.embedding_mgr.embed_single(serialized["text"])
			self.store.add_documents(
				collection_name=collection,
				ids=[serialized["id"]],
				documents=[serialized["text"]],
				embeddings=[embedding],
				metadatas=[serialized["metadata"]],
			)
			log.info("Indexed %s '%s' into '%s'", doctype, name, collection)
		except Exception:
			log.exception("Failed to index %s '%s'", doctype, name)
			frappe.log_error(f"RAG Indexing Error: {doctype} {name}")

	def remove_document(self, doctype: str, name: str):
		"""Remove a document from the vector store.

		Args:
			doctype: The DocType name
			name: The document name/ID
		"""
		collection = DOCTYPE_COLLECTION_MAP.get(doctype)
		if not collection:
			return

		try:
			self.store.delete_documents(collection, ids=[name])
			log.info("Removed %s '%s' from '%s'", doctype, name, collection)
		except Exception:
			log.exception("Failed to remove %s '%s'", doctype, name)

	def bulk_index_doctype(self, doctype: str, limit: int = 0) -> int:
		"""Bulk index all documents of a given DocType.

		Args:
			doctype: The DocType name
			limit: Max documents to index (0 = all)

		Returns:
			Number of documents indexed.
		"""
		serializer = SERIALIZERS.get(doctype)
		collection = DOCTYPE_COLLECTION_MAP.get(doctype)
		if not serializer or not collection:
			log.error("Cannot bulk index: no serializer/collection for '%s'", doctype)
			return 0

		# Fetch all document names
		filters = {}
		if doctype == "Item":
			filters = {"disabled": 0, "has_variants": 0}

		doc_names = frappe.get_all(
			doctype,
			filters=filters,
			pluck="name",
			limit_page_length=limit or 0,
			ignore_permissions=True,
		)

		if not doc_names:
			log.info("No documents found for '%s'", doctype)
			return 0

		total = len(doc_names)
		indexed = 0

		log.info("Bulk indexing %d %s documents...", total, doctype)

		# Process in batches
		for batch_start in range(0, total, BATCH_SIZE):
			batch_names = doc_names[batch_start : batch_start + BATCH_SIZE]

			# Serialize all documents in batch
			serialized_batch = []
			for name in batch_names:
				try:
					s = serializer(name)
					serialized_batch.append(s)
				except Exception:
					log.exception("Failed to serialize %s '%s'", doctype, name)
					continue

			if not serialized_batch:
				continue

			# Generate embeddings for the batch
			texts = [s["text"] for s in serialized_batch]
			embeddings = self.embedding_mgr.embed_batch(texts)

			# Store in ChromaDB
			ids = [s["id"] for s in serialized_batch]
			metadatas = [s["metadata"] for s in serialized_batch]

			self.store.add_documents(
				collection_name=collection,
				ids=ids,
				documents=texts,
				embeddings=embeddings,
				metadatas=metadatas,
			)

			indexed += len(serialized_batch)
			log.info("Indexed %d/%d %s documents", min(batch_start + BATCH_SIZE, total), total, doctype)

		log.info("Bulk indexing complete: %d %s documents indexed", indexed, doctype)
		return indexed

	def rebuild_collection(self, doctype: str) -> int:
		"""Delete and rebuild a collection from scratch.

		Returns:
			Number of documents indexed.
		"""
		collection = DOCTYPE_COLLECTION_MAP.get(doctype)
		if collection:
			self.store.delete_collection(collection)
			log.info("Dropped collection '%s' for rebuild", collection)

		return self.bulk_index_doctype(doctype)

	def rebuild_all(self) -> dict:
		"""Rebuild all collections.

		Returns:
			Dict mapping DocType -> count indexed.
		"""
		results = {}
		for doctype in DOCTYPE_COLLECTION_MAP:
			count = self.rebuild_collection(doctype)
			results[doctype] = count
		return results
