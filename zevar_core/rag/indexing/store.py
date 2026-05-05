"""
ChromaDB Vector Store Manager

Manages ChromaDB collections for products, customers, and knowledge base.
Provides CRUD operations for documents and their embeddings.
"""

import logging
import os

import chromadb

from zevar_core.rag.config import (
	CHROMA_PERSIST_DIR,
	COLLECTION_CUSTOMERS,
	COLLECTION_KNOWLEDGE,
	COLLECTION_PRODUCTS,
	EMBEDDING_DIMENSION,
)

log = logging.getLogger(__name__)


def _get_client() -> chromadb.ClientAPI:
	"""Get or create the ChromaDB client with persistent storage."""
	persist_dir = CHROMA_PERSIST_DIR
	os.makedirs(persist_dir, exist_ok=True)
	return chromadb.PersistentClient(path=persist_dir)


class VectorStore:
	"""ChromaDB collection manager with CRUD operations."""

	def __init__(self):
		self.client = _get_client()

	def get_or_create_collection(self, name: str) -> chromadb.Collection:
		"""Get an existing collection or create a new one."""
		return self.client.get_or_create_collection(
			name=name,
			metadata={"hnsw:space": "cosine", "dimension": EMBEDDING_DIMENSION},
		)

	def get_products_collection(self) -> chromadb.Collection:
		return self.get_or_create_collection(COLLECTION_PRODUCTS)

	def get_customers_collection(self) -> chromadb.Collection:
		return self.get_or_create_collection(COLLECTION_CUSTOMERS)

	def get_knowledge_collection(self) -> chromadb.Collection:
		return self.get_or_create_collection(COLLECTION_KNOWLEDGE)

	# ---- CRUD Operations ----

	def add_documents(
		self,
		collection_name: str,
		ids: list[str],
		documents: list[str],
		embeddings: list[list[float]],
		metadatas: list[dict] | None = None,
	):
		"""Add documents to a collection."""
		collection = self.get_or_create_collection(collection_name)
		# Upsert to handle both new and existing documents
		collection.upsert(
			ids=ids,
			documents=documents,
			embeddings=embeddings,
			metadatas=metadatas or [{}] * len(ids),
		)
		log.info("Upserted %d documents into '%s'", len(ids), collection_name)

	def delete_documents(self, collection_name: str, ids: list[str]):
		"""Delete documents from a collection by ID."""
		collection = self.get_or_create_collection(collection_name)
		if ids:
			collection.delete(ids=ids)
			log.info("Deleted %d documents from '%s'", len(ids), collection_name)

	def query(
		self,
		collection_name: str,
		query_embedding: list[float],
		n_results: int = 10,
		where: dict | None = None,
		where_document: dict | None = None,
	) -> dict:
		"""Query a collection by embedding similarity.

		Returns:
			Dict with keys: ids, documents, metadatas, distances
		"""
		collection = self.get_or_create_collection(collection_name)
		return collection.query(
			query_embeddings=[query_embedding],
			n_results=n_results,
			where=where,
			where_document=where_document,
			include=["documents", "metadatas", "distances"],
		)

	def get_collection_count(self, collection_name: str) -> int:
		"""Return the number of documents in a collection."""
		try:
			collection = self.client.get_collection(collection_name)
			return collection.count()
		except Exception:
			return 0

	def get_all_collection_stats(self) -> dict:
		"""Return stats for all zevar collections."""
		stats = {}
		for name in [COLLECTION_PRODUCTS, COLLECTION_CUSTOMERS, COLLECTION_KNOWLEDGE]:
			count = self.get_collection_count(name)
			stats[name] = {"count": count}
		return stats

	def delete_collection(self, collection_name: str):
		"""Delete an entire collection (useful for rebuild)."""
		try:
			self.client.delete_collection(collection_name)
			log.info("Deleted collection '%s'", collection_name)
		except Exception:
			pass  # Collection may not exist
