"""
Context Assembler - Builds structured LLM context from retrieved chunks.

Handles source attribution, PII masking, and context window management.
"""

import logging

from zevar_core.rag.config import DEFAULT_RERANK_TOP_N

log = logging.getLogger(__name__)

# Fields that contain PII and must be masked in LLM context
PII_FIELDS = {"phone", "email", "ssn", "social_security", "date_of_birth", "dob"}


def assemble_context(
	results: list[dict],
	max_results: int = DEFAULT_RERANK_TOP_N,
	mask_pii: bool = True,
) -> dict:
	"""Build a structured context block from retrieval results.

	Args:
		results: List of retrieval result dicts (from vector_search.search).
		max_results: Maximum number of results to include.
		mask_pii: Whether to mask PII in the context text.

	Returns:
		Dict with keys:
			- context_text: Formatted context string for LLM
			- sources: List of source attribution dicts
			- domains: Set of domains found
	"""
	top_results = results[:max_results]

	if not top_results:
		return {"context_text": "", "sources": [], "domains": set()}

	context_parts = []
	sources = []
	domains = set()

	for i, result in enumerate(top_results):
		domain = result.get("domain", "general")
		domains.add(domain)
		metadata = result.get("metadata", {})
		text = result.get("text", "")

		if mask_pii:
			text = _mask_pii(text)

		# Format based on domain
		if domain == "product":
			source_label = metadata.get("item_name", result.get("id", "Unknown"))
			context_parts.append(f"[Product {i + 1}] {text}")
		elif domain == "customer":
			source_label = metadata.get("customer_name", result.get("id", "Unknown"))
			context_parts.append(f"[Customer {i + 1}] {text}")
		elif domain == "policy":
			source_label = metadata.get("title", result.get("id", "Unknown"))
			context_parts.append(f"[Policy/Article {i + 1}] {text}")
		else:
			source_label = result.get("id", "Unknown")
			context_parts.append(f"[Source {i + 1}] {text}")

		sources.append(
			{
				"type": domain,
				"id": result.get("id", ""),
				"label": source_label,
				"similarity": result.get("similarity", 0),
				"collection": result.get("collection", ""),
			}
		)

	context_text = "\n\n".join(context_parts)

	return {
		"context_text": context_text,
		"sources": sources,
		"domains": domains,
	}


def _mask_pii(text: str) -> str:
	"""Mask common PII patterns in text."""
	import re

	# Phone numbers: (XXX) XXX-XXXX or XXX-XXX-XXXX
	text = re.sub(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "***-***-****", text)

	# Email addresses
	text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "***@***.***", text)

	# SSN patterns: XXX-XX-XXXX
	text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****", text)

	return text
