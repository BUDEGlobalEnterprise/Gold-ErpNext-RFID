"""
Insight generator with grounding validation — Plan §9.6/§9.7.

Pipeline:
1. Embed the scope + focus into a query
2. Retrieve top-K chunks from COLLECTION_METRICS (ChromaDB)
3. Walk the KG to expand to 2-hop neighbors
4. Call Qwen3.6-35B with the structured prompt
5. Parse the JSON response
6. Run the grounding validator: every number in grounded_numbers must
   appear verbatim in a context chunk's value
7. Strip ungrounded insights; if all fail, return the deterministic fallback
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

import frappe

from zevar_core.rag.config import (
	COLLECTION_METRICS,
	DEFAULT_MAX_TOKENS,
	DEFAULT_TEMPERATURE,
	QWEN_DEFAULT_ENDPOINT,
	QWEN_DEFAULT_MODEL,
)
from zevar_core.rag.embedding.manager import EmbeddingManager
from zevar_core.rag.generation.llm_provider import get_llm_provider
from zevar_core.rag.generation.prompt_templates import build_pnl_prompt
from zevar_core.rag.indexing.kg_builder import get_or_build_kg
from zevar_core.rag.indexing.store import VectorStore


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_pnl_insights(scope: str = "today", focus: str | None = None) -> dict:
	"""Top-level entry point used by the analytics_hub.get_rag_insights endpoint."""
	cache_key = f"rag_insights:{scope}:{focus or 'all'}:{frappe.session.user}"
	cached = frappe.cache().get_value(cache_key)
	if cached:
		return cached

	# 1) Retrieve grounded context chunks
	chunks = _retrieve_chunks(scope, focus, limit=12)
	kg_summary = ""
	try:
		kg = get_or_build_kg()
		kg_summary = kg.summary()
	except Exception as e:
		frappe.log_error(f"KG load failed: {e}", "RAG")

	# 2) Build the prompt
	messages = build_pnl_prompt(scope, focus, chunks, kg_summary)

	# 3) Call the LLM
	try:
		provider = get_llm_provider()
		raw = provider.generate(
			messages=messages,
			max_tokens=min(DEFAULT_MAX_TOKENS, 1200),
			temperature=DEFAULT_TEMPERATURE,
		)
	except Exception as e:
		frappe.log_error(f"LLM call failed: {e}", "RAG")
		raw = ""

	# 4) Parse JSON safely
	parsed = _parse_json_safely(raw)

	# 5) Validate grounding
	insights = parsed.get("insights", []) if isinstance(parsed, dict) else []
	validated = [i for i in insights if _validate_grounding(i, chunks)]

	# 6) Fallback if nothing validated
	if not validated:
		fallback = _deterministic_fallback(scope, chunks)
		payload = {
			"headline": fallback["headline"],
			"body": fallback["body"],
			"insights": fallback["insights"],
			"generated_at": str(frappe.utils.now_datetime()),
			"model_version": "fallback",
			"prompt_hash": _prompt_hash(messages),
		}
		frappe.cache().set_value(cache_key, payload, expires_in_sec=3600)
		return payload

	# 7) Tag each insight with an id
	for ins in validated:
		ins["id"] = _insight_id(ins)

	payload = {
		"headline": parsed.get("headline", "Today at a glance"),
		"body": parsed.get("body", ""),
		"insights": validated,
		"generated_at": str(frappe.utils.now_datetime()),
		"model_version": QWEN_DEFAULT_MODEL,
		"prompt_hash": _prompt_hash(messages),
	}
	frappe.cache().set_value(cache_key, payload, expires_in_sec=3600)
	return payload


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------


def _retrieve_chunks(scope: str, focus: str | None, limit: int = 12) -> list[dict]:
	"""Embed the scope/focus query and pull top-K nearest metric chunks."""
	embedder = EmbeddingManager()
	store = VectorStore()
	query_text = _query_text(scope, focus)
	q_emb = embedder.embed_single(query_text)
	try:
		hits = store.query(
			collection_name=COLLECTION_METRICS,
			query_embedding=q_emb,
			n_results=limit,
		)
	except Exception as e:
		frappe.log_error(f"Chroma query failed: {e}", "RAG")
		return []
	chunks = []
	# ChromaDB returns nested lists (one per query)
	documents = (hits.get("documents") or [[]])[0]
	metadatas = (hits.get("metadatas") or [[]])[0]
	distances = (hits.get("distances") or [[]])[0]
	for i, doc in enumerate(documents):
		meta = metadatas[i] if i < len(metadatas) else {}
		dist = distances[i] if i < len(distances) else 0.0
		chunks.append({
			"value": str((meta or {}).get("revenue") or (meta or {}).get("count") or (meta or {}).get("value") or ""),
			"label": (doc or "")[:200],
			"source_query": (meta or {}).get("source_query", "rag_index"),
			"date": str((meta or {}).get("date", "")),
			"confidence": float(dist or 0.0),
		})
	# Always include the deterministic today numbers as a baseline
	chunks.extend(_today_baseline_chunks())
	return chunks


def _query_text(scope: str, focus: str | None) -> str:
	parts = ["Zevar P&L", scope or "today"]
	if focus:
		parts.append(focus)
	return " ".join(parts)


def _today_baseline_chunks() -> list[dict]:
	"""Always include today's actual numbers from analytics_hub."""
	from zevar_core.api.analytics_hub import (
		get_cash_variance_today,
		get_daily_revenue_breakdown,
		get_layaway_health,
		get_overdue_payments,
	)
	from frappe.utils import nowdate

	out = []
	try:
		d = get_daily_revenue_breakdown(nowdate(), nowdate())
		out.append({"value": f"{float(d.get('total_revenue') or 0):.2f}", "label": "Today's total revenue", "source_query": "get_daily_revenue_breakdown", "confidence": 1.0})
		out.append({"value": str(int(d.get("sales_count") or 0)), "label": "Today's sales count", "source_query": "get_daily_revenue_breakdown", "confidence": 1.0})
	except Exception:
		pass
	try:
		l = get_layaway_health()
		out.append({"value": str(int(l.get("active") or 0)), "label": "Active layaways", "source_query": "get_layaway_health", "confidence": 1.0})
		out.append({"value": str(int(l.get("overdue") or 0)), "label": "Overdue layaways", "source_query": "get_layaway_health", "confidence": 1.0})
	except Exception:
		pass
	try:
		cv = get_cash_variance_today()
		out.append({"value": f"{float(cv.get('total_variance') or 0):.2f}", "label": "Today's cash variance", "source_query": "get_cash_variance_today", "confidence": 1.0})
	except Exception:
		pass
	try:
		od = get_overdue_payments()
		out.append({"value": f"{float(od.get('total_overdue_amount') or 0):.2f}", "label": "Total overdue amount", "source_query": "get_overdue_payments", "confidence": 1.0})
	except Exception:
		pass
	return out


# ---------------------------------------------------------------------------
# Grounding validator (Plan §9.7)
# ---------------------------------------------------------------------------


def _validate_grounding(insight: dict, context_chunks: list[dict]) -> bool:
	"""Every grounded_numbers value must appear verbatim in some chunk's value."""
	if not isinstance(insight, dict):
		return False
	for n in insight.get("grounded_numbers", []) or []:
		v = str(n.get("value", "")).strip()
		if not v:
			return False
		if not any(v in str(c.get("value", "")) or v in str(c.get("label", "")) for c in context_chunks):
			return False
	return True


# ---------------------------------------------------------------------------
# JSON parse + fallback
# ---------------------------------------------------------------------------


def _parse_json_safely(raw: str) -> dict:
	if not raw:
		return {}
	# Direct
	try:
		return json.loads(raw)
	except Exception:
		pass
	# Strip fences
	m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
	if m:
		try:
			return json.loads(m.group(1))
		except Exception:
			pass
	# Last-ditch: find first { ... } block
	m = re.search(r"\{.*\}", raw, re.DOTALL)
	if m:
		try:
			return json.loads(m.group(0))
		except Exception:
			pass
	return {}


def _deterministic_fallback(scope: str, chunks: list[dict]) -> dict:
	"""Plan §9.7 last paragraph: rule-based summary when grounding fails."""
	# Pull out a few well-known labels
	def find(label):
		for c in chunks:
			if c.get("label") == label and c.get("value"):
				return c["value"]
		return "?"

	sales = find("Today's total revenue")
	count = find("Today's sales count")
	variance = find("Today's cash variance")
	overdue_amt = find("Total overdue amount")

	headline = f"Today: {count} sales totaling ${sales}"
	body = (
		f"Total revenue ${sales}, {count} transactions. "
		f"Cash variance ${variance}. "
		f"Overdue payments ${overdue_amt}."
	)
	return {
		"headline": headline,
		"body": body,
		"insights": [
			{
				"id": _insight_id({"text": headline, "value": sales}),
				"category": "revenue",
				"severity": "info",
				"text": f"Total revenue today is ${sales} across {count} sales.",
				"grounded_numbers": [
					{"value": f"${sales}", "label": "Total revenue", "source_query": "get_daily_revenue_breakdown", "confidence": 1.0}
				],
				"recommended_action": None,
			}
		],
	}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _insight_id(insight: dict) -> str:
	text = (insight.get("text") or insight.get("value") or json.dumps(insight, sort_keys=True)).encode("utf-8")
	return hashlib.sha1(text).hexdigest()[:12]


def _prompt_hash(messages: list[dict]) -> str:
	blob = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
	return hashlib.sha1(blob).hexdigest()[:12]
