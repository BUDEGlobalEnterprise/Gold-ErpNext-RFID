"""
Abstract base class for embedding providers.
"""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
	"""Interface for embedding model providers."""

	@abstractmethod
	def embed(self, texts: list[str]) -> list[list[float]]:
		"""Generate embeddings for a list of texts.

		Args:
			texts: List of text strings to embed.

		Returns:
			List of embedding vectors (each a list of floats).
		"""

	@abstractmethod
	def get_dimension(self) -> int:
		"""Return the dimension of the embedding vectors."""
