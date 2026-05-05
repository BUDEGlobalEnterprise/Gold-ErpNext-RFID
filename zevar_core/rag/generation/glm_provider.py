"""
Z.ai / GLM API Provider.

Uses the GLM API (open.bigmodel.cn) for LLM generation.
Best for: General queries, product search, policy questions.
"""

import json
import logging

import frappe
import requests

from zevar_core.rag.generation.llm_provider import LLMProvider

log = logging.getLogger(__name__)


class GLMProvider(LLMProvider):
	"""Z.ai GLM API LLM provider."""

	def __init__(self):
		self._load_settings()

	def _load_settings(self):
		"""Load settings from RAG Settings DocType."""
		try:
			settings = frappe.get_single("RAG Settings")
			self.api_key = settings.glm_api_key or frappe.conf.get("glm_api_key", "")
			self.endpoint = settings.glm_endpoint or "https://open.bigmodel.cn/api/paas/v4/chat/completions"
			self.model = settings.glm_model or "glm-4-flash"
		except Exception:
			self.api_key = ""
			self.endpoint = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
			self.model = "glm-4-flash"

	def generate(self, messages: list[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
		if not self.api_key:
			raise RuntimeError("GLM API key not configured. Set it in RAG Settings.")

		headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
		}

		payload = {
			"model": self.model,
			"messages": messages,
			"max_tokens": max_tokens,
			"temperature": temperature,
		}

		try:
			resp = requests.post(
				self.endpoint,
				headers=headers,
				json=payload,
				timeout=30,
			)
			resp.raise_for_status()
			data = resp.json()
			return data["choices"][0]["message"]["content"]
		except requests.exceptions.Timeout:
			raise RuntimeError("GLM API request timed out after 30s")
		except requests.exceptions.HTTPError as e:
			log.error("GLM API HTTP error: %s - %s", e, resp.text[:500])
			raise RuntimeError(f"GLM API error: {e}")
		except (KeyError, IndexError, json.JSONDecodeError) as e:
			log.error("GLM API response parse error: %s", e)
			raise RuntimeError(f"Failed to parse GLM response: {e}")

	def is_available(self) -> bool:
		if not self.api_key:
			return False
		try:
			resp = requests.get(
				self.endpoint.rsplit("/", 2)[0] + "/models",
				headers={"Authorization": f"Bearer {self.api_key}"},
				timeout=5,
			)
			return resp.status_code == 200
		except Exception:
			return False

	def get_name(self) -> str:
		return f"GLM/{self.model}"
