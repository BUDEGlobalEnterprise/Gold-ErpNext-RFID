"""
OpenAI-Compatible Provider (Self-Hosted Qwen 3.6).

Works with any OpenAI-compatible API endpoint (vLLM, Ollama, LM Studio, etc.).
All data stays on-prem — no external calls.
"""

import json
import logging
import re

import frappe
import requests

from zevar_core.rag.generation.llm_provider import LLMProvider

log = logging.getLogger(__name__)

_THINK_RE = re.compile(r"<think[^>]*>.*?</think[^>]*>", re.DOTALL)


def _strip_thinking(text: str) -> str:
	"""Remove Qwen3 thinking blocks from response text."""
	return _THINK_RE.sub("", text).strip()


class OpenAICompatProvider(LLMProvider):
	"""OpenAI-compatible LLM provider for self-hosted Qwen."""

	def __init__(self):
		self._load_settings()

	def _load_settings(self):
		"""Load settings from RAG Settings DocType, falling back to config defaults."""
		from zevar_core.rag.config import QWEN_DEFAULT_ENDPOINT, QWEN_DEFAULT_MODEL, QWEN_DEFAULT_API_KEY

		try:
			settings = frappe.get_single("RAG Settings")
			self.endpoint = settings.qwen_endpoint or QWEN_DEFAULT_ENDPOINT
			self.model = settings.qwen_model or QWEN_DEFAULT_MODEL
			self.api_key = settings.qwen_api_key or QWEN_DEFAULT_API_KEY
		except Exception:
			self.endpoint = QWEN_DEFAULT_ENDPOINT
			self.model = QWEN_DEFAULT_MODEL
			self.api_key = QWEN_DEFAULT_API_KEY

	def generate(self, messages: list[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
		headers = {"Content-Type": "application/json"}
		if self.api_key:
			headers["Authorization"] = f"Bearer {self.api_key}"

		# Suppress Qwen3 thinking mode — saves ~50% tokens and doubles speed
		processed_messages = list(messages)
		if processed_messages:
			last = processed_messages[-1]
			if last.get("role") == "user":
				last = dict(last)
				last["content"] = last["content"] + "\n\n/no_think"
				processed_messages[-1] = last

		payload = {
			"model": self.model,
			"messages": processed_messages,
			"max_tokens": max_tokens,
			"temperature": temperature,
			# vLLM-specific: disable Qwen3 thinking mode entirely
			"chat_template_kwargs": {"enable_thinking": False},
		}

		try:
			resp = requests.post(
				self.endpoint,
				headers=headers,
				json=payload,
				timeout=45,
			)
			resp.raise_for_status()
			data = resp.json()

			message = data["choices"][0]["message"]
			content = message.get("content", "")

			# If content is empty but reasoning_content exists, use reasoning
			# (happens when /no_think didn't fully suppress thinking)
			if not content.strip():
				reasoning = message.get("reasoning_content", "")
				if reasoning.strip():
					content = reasoning

			# Strip <think...</think tags aggressively — Qwen sometimes leaks them
			content = _strip_thinking(content)

			if not content.strip():
				raise RuntimeError("Qwen returned empty content")

			return content.strip()

		except requests.exceptions.Timeout:
			raise RuntimeError("Qwen API request timed out after 45s. Check if the server at " + self.endpoint + " is responding.")
		except requests.exceptions.ConnectionError:
			raise RuntimeError(f"Cannot connect to Qwen at {self.endpoint}. Is the server running?")
		except requests.exceptions.HTTPError as e:
			log.error("Qwen API HTTP error: %s - %s", e, resp.text[:500])
			raise RuntimeError(f"Qwen API error: {e}")
		except (KeyError, IndexError, json.JSONDecodeError) as e:
			log.error("Qwen API response parse error: %s", e)
			raise RuntimeError(f"Failed to parse Qwen response: {e}")

	def is_available(self) -> bool:
		try:
			base_url = self.endpoint.rsplit("/", 2)[0]
			headers = {"Content-Type": "application/json"}
			if self.api_key:
				headers["Authorization"] = f"Bearer {self.api_key}"
			resp = requests.get(f"{base_url}/models", headers=headers, timeout=5)
			return resp.status_code == 200
		except Exception:
			return False

	def get_name(self) -> str:
		return f"Qwen"
