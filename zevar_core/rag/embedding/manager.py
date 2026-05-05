"""
Embedding Manager - Orchestrates embedding generation with batch processing
and caching.
"""

import frappe

from zevar_core.rag.config import BATCH_SIZE
from zevar_core.rag.embedding.local_provider import LocalEmbeddingProvider


class EmbeddingManager:
	"""Manages embedding generation with batch support and caching."""

	def __init__(self, provider=None):
		self.provider = provider or LocalEmbeddingProvider()

	def embed_single(self, text: str) -> list[float]:
		"""Generate embedding for a single text."""
		result = self.provider.embed([text])
		return result[0] if result else []

	def embed_batch(self, texts: list[str]) -> list[list[float]]:
		"""Generate embeddings for a batch of texts, processing in chunks."""
		all_embeddings = []
		for i in range(0, len(texts), BATCH_SIZE):
			chunk = texts[i : i + BATCH_SIZE]
			embeddings = self.provider.embed(chunk)
			all_embeddings.extend(embeddings)
			frappe.publish_realtime(
				"rag_index_progress",
				{"current": min(i + BATCH_SIZE, len(texts)), "total": len(texts)},
			)
		return all_embeddings

	@property
	def dimension(self) -> int:
		return self.provider.get_dimension()
