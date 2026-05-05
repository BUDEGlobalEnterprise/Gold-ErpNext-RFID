"""
Document Chunker

Splits long text documents into overlapping chunks suitable for embedding.
"""

from zevar_core.rag.config import CHUNK_OVERLAP_TOKENS, CHUNK_SIZE_TOKENS


def chunk_text(
	text: str,
	chunk_size: int = CHUNK_SIZE_TOKENS,
	chunk_overlap: int = CHUNK_OVERLAP_TOKENS,
) -> list[str]:
	"""Split text into overlapping chunks based on approximate token count.

	Uses a simple word-based approximation (1 token ~= 0.75 words).

	Args:
		text: The text to chunk.
		chunk_size: Target chunk size in tokens.
		chunk_overlap: Overlap between chunks in tokens.

	Returns:
		List of text chunks.
	"""
	if not text:
		return []

	# Approximate: 1 token ≈ 0.75 words (for English)
	words = text.split()
	words_per_chunk = int(chunk_size * 0.75)
	overlap_words = int(chunk_overlap * 0.75)

	if words_per_chunk <= 0:
		words_per_chunk = 100
	if overlap_words >= words_per_chunk:
		overlap_words = words_per_chunk // 4

	chunks = []
	start = 0
	while start < len(words):
		end = start + words_per_chunk
		chunk = " ".join(words[start:end])
		chunks.append(chunk)
		if end >= len(words):
			break
		start += words_per_chunk - overlap_words

	return chunks


def chunk_document(
	title: str,
	content: str,
	metadata: dict | None = None,
	chunk_size: int = CHUNK_SIZE_TOKENS,
) -> list[dict]:
	"""Chunk a document with metadata preservation.

	Returns:
		List of dicts with keys: id, text, metadata
	"""
	chunks = chunk_text(content, chunk_size=chunk_size)
	results = []
	for i, chunk in enumerate(chunks):
		chunk_meta = dict(metadata or {})
		chunk_meta["chunk_index"] = i
		chunk_meta["chunk_total"] = len(chunks)
		chunk_meta["title"] = title

		# Generate unique chunk ID
		chunk_id = f"{metadata.get('article_id', metadata.get('doctype', 'doc'))}_{i}"
		results.append({"id": chunk_id, "text": chunk, "metadata": chunk_meta})

	return results
