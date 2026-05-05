"""
Response Builder - Orchestrates retrieval + LLM generation.

Handles the full pipeline: classify query -> retrieve context -> generate answer
with citation injection and provider fallback.
"""

import logging
import time

import frappe

from zevar_core.rag.generation.prompt_templates import build_messages, get_system_prompt
from zevar_core.rag.generation.router import LLMRouter
from zevar_core.rag.retrieval.classifier import classify, get_search_collections
from zevar_core.rag.retrieval.context_assembler import assemble_context
from zevar_core.rag.retrieval.hybrid_search import hybrid_search

log = logging.getLogger(__name__)


class ResponseBuilder:
	"""Builds complete RAG responses with LLM generation."""

	def __init__(self):
		self.router = LLMRouter()

	def build(
		self,
		question: str,
		context_type: str | None = None,
		mask_pii: bool = True,
	) -> dict:
		"""Build a complete RAG response.

		Args:
			question: User's natural language question.
			context_type: Optional domain hint.
			mask_pii: Whether to mask PII in the response.

		Returns:
			Dict with: answer, sources, domain, confidence, provider, latency_ms.
		"""
		start = time.time()

		# Step 1: Classify the query
		domain = context_type if context_type in ("product", "customer", "repair", "policy", "general") else classify(question)

		# Step 2: Retrieve relevant documents (hybrid: vector + keyword)
		collections = get_search_collections(domain)
		results = hybrid_search(question, collections=collections, top_k=10)

		# Step 3: Assemble context with PII handling
		needs_masking = mask_pii and (domain == "customer")
		assembled = assemble_context(results, mask_pii=needs_masking)

		# Handle no results
		if not results:
			return {
				"answer": "I couldn't find relevant information for your question. Could you try rephrasing or be more specific?",
				"sources": [],
				"domain": domain,
				"confidence": 0,
				"provider": "none",
				"latency_ms": int((time.time() - start) * 1000),
			}

		# Step 4: Generate LLM response
		confidence = results[0].get("similarity", 0) if results else 0
 
		try:
			system_prompt = get_system_prompt(domain)
			messages = build_messages(system_prompt, assembled["context_text"], question)
			answer, provider_name = self.router.generate(messages, domain=domain)
			
			# Step 5: Check for tool calls
			if "{\"tool\":" in answer:
				answer = self._handle_tool_calls(answer)
				
		except RuntimeError as e:
			# LLM unavailable - fall back to retrieval-only answer
			log.warning("LLM generation failed: %s. Falling back to retrieval-only.", e)
			answer = _build_fallback_answer(question, assembled, domain)
			provider_name = f"retrieval-only (LLM error: {e})"
		except Exception:
			log.exception("Unexpected LLM error")
			answer = _build_fallback_answer(question, assembled, domain)
			provider_name = "retrieval-only (error)"
 
		latency = int((time.time() - start) * 1000)
 
		return {
			"answer": answer,
			"sources": assembled["sources"],
			"domain": domain,
			"confidence": round(confidence, 2),
			"provider": provider_name,
			"latency_ms": latency,
		}

	def _handle_tool_calls(self, answer: str) -> str:
		"""Parse and execute tool calls from the LLM answer."""
		import json
		from zevar_core.rag.tools import agent_tools

		# Find JSON block using a more robust method than regex for nested objects
		marker = '{"tool":'
		if marker not in answer:
			return answer

		start_idx = answer.find(marker)
		
		# Basic brace matching to find the full JSON object
		brace_count = 0
		end_idx = -1
		for i in range(start_idx, len(answer)):
			if answer[i] == '{':
				brace_count += 1
			elif answer[i] == '}':
				brace_count -= 1
				if brace_count == 0:
					end_idx = i + 1
					break
		
		if end_idx == -1:
			return answer

		json_str = answer[start_idx:end_idx]
		
		try:
			data = json.loads(json_str)
			tool_name = data.get("tool")
			params = data.get("params", {})
			
			# Security: Only allow tools explicitly listed in AGENT_TOOLS registry
			if hasattr(agent_tools, "AGENT_TOOLS") and tool_name in agent_tools.AGENT_TOOLS:
				tool_func = getattr(agent_tools, tool_name)
				result = tool_func(**params)
				
				# Format result back into the answer
				clean_answer = answer.replace(json_str, "").strip()
				status_msg = f"\n\n[Action Executed: {tool_name}]\n{result.get('message', 'Done')}"
				
				return f"{clean_answer}{status_msg}".strip()
			else:
				return f"{answer}\n\n(Error: Tool '{tool_name}' not found)"
		except Exception as e:
			return f"{answer}\n\n(Error executing tool: {e})"



def _build_fallback_answer(question: str, assembled: dict, domain: str) -> str:
	"""Build a retrieval-only answer when LLM is unavailable."""
	sources = assembled.get("sources", [])

	if not sources:
		return "No relevant information found."

	if domain == "product":
		lines = ["Here are the matching products:"]
		for i, src in enumerate(sources[:5]):
			lines.append(f"  {i + 1}. {src.get('label', 'Unknown')} (relevance: {src.get('similarity', 0):.0%})")
		return "\n".join(lines)

	# Return top context snippets
	snippets = []
	for src in sources[:3]:
		snippets.append(f"- {src.get('label', 'Source')}")

	return f"Top results found:\n" + "\n".join(snippets)
