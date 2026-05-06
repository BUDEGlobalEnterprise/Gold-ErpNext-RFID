"""
LLM Router - Routes queries to the Qwen LLM provider.

All queries go through the self-hosted Qwen model.
No external/cloud LLM is used — all data stays on-prem.
"""

import logging

import frappe

from zevar_core.rag.generation.llm_provider import LLMProvider
from zevar_core.rag.generation.openai_compat_provider import OpenAICompatProvider

log = logging.getLogger(__name__)


class LLMRouter:
	"""Routes all queries to the self-hosted Qwen model."""

	def __init__(self):
		self._qwen = None

	@property
	def qwen(self) -> OpenAICompatProvider:
		if self._qwen is None:
			self._qwen = OpenAICompatProvider()
		return self._qwen

	def get_provider(self, domain: str) -> LLMProvider:
		"""Get the Qwen provider for any domain.

		All queries go to the self-hosted Qwen model.
		No data leaves the network.
		"""
		return self.qwen

	def generate(
		self, messages: list[dict], domain: str = "general", max_tokens: int = 1024, temperature: float = 0.3
	) -> tuple[str, str]:
		"""Generate a response using Qwen.

		Returns:
			Tuple of (response_text, provider_name).
		"""
		provider = self.get_provider(domain)

		try:
			settings = frappe.get_single("RAG Settings")
			max_tokens = max_tokens or settings.llm_max_tokens or 1024
			temperature = (
				temperature
				if temperature != 0.3
				else ((settings.llm_max_tokens and settings.llm_temperature) or 0.3)
			)
		except Exception:
			pass

		response = provider.generate(messages, max_tokens=max_tokens, temperature=temperature)
		return response, provider.get_name()
