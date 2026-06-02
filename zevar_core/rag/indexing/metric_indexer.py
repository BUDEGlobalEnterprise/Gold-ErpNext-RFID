"""
Metric indexer — Plan §9.4.

Indexes daily metric time-series into the COLLECTION_METRICS ChromaDB
collection. Text representations are embedded (so they share the 384-d
space with text chunks) and stored as metric embeddings.

Refreshed weekly alongside the KG rebuild.
"""
from __future__ import annotations

import frappe

from zevar_core.rag.config import COLLECTION_METRICS, METRIC_TEXT_TEMPLATES
from zevar_core.rag.embedding.manager import EmbeddingManager
from zevar_core.rag.indexing.store import VectorStore


def _metric_text(template_key: str, **kwargs) -> str:
	tpl = METRIC_TEXT_TEMPLATES.get(template_key, "{date}: {value}")
	try:
		return tpl.format(**{k: (v if v is not None else "?") for k, v in kwargs.items()})
	except KeyError:
		return f"{template_key} {kwargs}"


def index_daily_revenue(days: int = 90) -> int:
	"""Embed the last N days of sales revenue. Returns the number of metrics indexed."""
	from frappe.utils import add_days, nowdate

	from_date = add_days(nowdate(), -days)
	si = frappe.qb.DocType("Sales Invoice")
	rows = (
		frappe.qb.from_(si)
		.select(
			si.posting_date,
			frappe.qb.functions.Sum(si.base_grand_total).as_("revenue"),
			frappe.qb.functions.Count(si.name).as_("count"),
		)
		.where(si.docstatus == 1)
		.where(si.is_pos == 1)
		.where(si.posting_date >= from_date)
		.groupby(si.posting_date)
	).run(as_dict=True)

	docs = []
	metas = []
	ids = []
	for r in rows:
		date_str = str(r["posting_date"])
		text = _metric_text(
			"daily_revenue",
			date=date_str,
			value=f"{float(r['revenue'] or 0):.2f}",
			count=int(r["count"] or 0),
		)
		docs.append(text)
		metas.append({
			"date": date_str,
			"revenue": float(r["revenue"] or 0),
			"count": int(r["count"] or 0),
			"source_query": "get_daily_revenue_breakdown",
		})
		ids.append(f"daily_revenue:{date_str}")

	return _upsert_metrics(docs, metas, ids)


def index_daily_repair(days: int = 90) -> int:
	"""Embed the last N days of repair deliveries."""
	from frappe.utils import add_days, nowdate

	from_date = add_days(nowdate(), -days)
	ro = frappe.qb.DocType("Repair Order")
	rows = (
		frappe.qb.from_(ro)
		.select(
			ro.posting_date,
			frappe.qb.functions.Sum(ro.grand_total).as_("revenue"),
			frappe.qb.functions.Count(ro.name).as_("count"),
		)
		.where(ro.docstatus == 1)
		.where(ro.workflow_state == "Delivered")
		.where(ro.posting_date >= from_date)
		.groupby(ro.posting_date)
	).run(as_dict=True)

	docs = []
	metas = []
	ids = []
	for r in rows:
		date_str = str(r["posting_date"])
		text = _metric_text(
			"daily_repair",
			date=date_str,
			value=f"{float(r['revenue'] or 0):.2f}",
			count=int(r["count"] or 0),
		)
		docs.append(text)
		metas.append({
			"date": date_str,
			"revenue": float(r["revenue"] or 0),
			"count": int(r["count"] or 0),
			"source_query": "get_daily_revenue_breakdown",
		})
		ids.append(f"daily_repair:{date_str}")

	return _upsert_metrics(docs, metas, ids)


def _upsert_metrics(docs: list[str], metas: list[dict], ids: list[str]) -> int:
	"""Embed and upsert into COLLECTION_METRICS."""
	if not docs:
		return 0
	embedder = EmbeddingManager()
	embeddings = embedder.embed_batch(docs)
	store = VectorStore()
	store.add_documents(
		collection_name=COLLECTION_METRICS,
		ids=ids,
		documents=docs,
		embeddings=embeddings,
		metadatas=metas,
	)
	return len(docs)


def rebuild_metric_index() -> int:
	"""Rebuild the full metric index. Called weekly via the scheduler."""
	total = 0
	total += index_daily_revenue(90)
	total += index_daily_repair(90)
	frappe.logger().info("ZevarKG metrics index rebuilt: %d rows", total)
	return total
