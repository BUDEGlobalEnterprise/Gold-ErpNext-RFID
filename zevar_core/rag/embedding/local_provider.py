"""
Local embedding provider using sentence-transformers.

Uses the all-MiniLM-L6-v2 model (384-dim) for fast, offline-capable embeddings.
The model is loaded once and reused across calls.
"""

import hashlib
import json
import logging

import frappe
from sentence_transformers import SentenceTransformer

from zevar_core.rag.config import DEFAULT_EMBEDDING_MODEL, EMBEDDING_CACHE_PREFIX, EMBEDDING_CACHE_TTL
from zevar_core.rag.embedding.provider import EmbeddingProvider

log = logging.getLogger(__name__)

_model = None


def _get_model() -> SentenceTransformer:
	"""Lazy-load the sentence-transformers model (singleton)."""
	global _model
	if _model is None:
		_model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
		log.info("Loaded embedding model: %s", DEFAULT_EMBEDDING_MODEL)
	return _model


class LocalEmbeddingProvider(EmbeddingProvider):
	"""Local sentence-transformers embedding provider with Redis caching."""

	def __init__(self, use_cache: bool = True):
		self.use_cache = use_cache

	def embed(self, texts: list[str]) -> list[list[float]]:
		if not texts:
			return []

		# Check Redis cache for each text
		cached = {}
		to_embed = []

		if self.use_cache:
			for i, text in enumerate(texts):
				cache_key = self._cache_key(text)
				hit = frappe.cache().get_value(cache_key)
				if hit is not None:
					cached[i] = json.loads(hit)
				else:
					to_embed.append((i, text))
		else:
			to_embed = list(enumerate(texts))

		# Compute embeddings for uncached texts
		new_embeddings = {}
		if to_embed:
			model = _get_model()
			embeddings = model.encode([t for _, t in to_embed], show_progress_bar=False)
			for idx, (_, text) in enumerate(to_embed):
				vec = embeddings[idx].tolist()
				new_embeddings[to_embed[idx][0]] = vec

				# Cache the result
				if self.use_cache:
					cache_key = self._cache_key(text)
					frappe.cache().set_value(cache_key, json.dumps(vec), expires_in_sec=EMBEDDING_CACHE_TTL)

		# Merge cached + new in original order
		all_embeddings = {**cached, **new_embeddings}
		return [all_embeddings[i] for i in range(len(texts))]

	def get_dimension(self) -> int:
		return 384

	@staticmethod
	def _cache_key(text: str) -> str:
		text_hash = hashlib.md5(text.encode()).hexdigest()
		return f"{EMBEDDING_CACHE_PREFIX}{text_hash}"
