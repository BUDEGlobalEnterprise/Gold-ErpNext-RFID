"""
Abstract LLM Provider Interface.

All LLM providers (GLM, Qwen/OpenAI-compatible) implement this interface.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
	"""Interface for LLM generation providers."""

	@abstractmethod
	def generate(self, messages: list[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
		"""Generate a response from the LLM.

		Args:
			messages: List of message dicts with 'role' and 'content'.
				e.g. [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
			max_tokens: Maximum tokens in the response.
			temperature: Sampling temperature (0 = deterministic, 1 = creative).

		Returns:
			Generated text string.
		"""

	@abstractmethod
	def is_available(self) -> bool:
		"""Check if the provider is reachable and configured."""

	@abstractmethod
	def get_name(self) -> str:
		"""Return the provider name for logging."""
