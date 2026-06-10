"""
Knowledge Graph Builder — Plan §9.3, §9.7.

Builds a lightweight in-memory knowledge graph of Frappe entities:
- Metric nodes (time-series revenue, repair volume, etc.)
- Item nodes (with metal/purity/stone attributes)
- Customer nodes (RFM attributes)
- Category nodes (bridal, fashion, etc.)
- Edges: Item -[:SOLD_IN]-> SalesInvoice, Customer -[:OWNS]-> Layaway, etc.

Serialized to a pickle file (per Q10 recommendation).
Refreshed weekly (Sunday 03:00) and on demand via admin button.
"""

from __future__ import annotations

import datetime
import os
import pickle
import tempfile
from dataclasses import dataclass, field
from typing import Any

import frappe
from frappe.utils import add_days, getdate, nowdate

# Plan Q10 — Pickle to /tmp
DEFAULT_PICKLE = os.path.join(tempfile.gettempdir(), "zevar_kg.pickle")


# ---------------------------------------------------------------------------
# Node & Edge dataclasses
# ---------------------------------------------------------------------------


@dataclass
class KGNode:
	id: str
	type: str  # "Item" | "Customer" | "Category" | "Metric" | "Cohort"
	attrs: dict = field(default_factory=dict)


@dataclass
class KGEdge:
	src: str
	dst: str
	type: str  # "SOLD_IN" | "OWNS" | "IN_CATEGORY" | "MOUNTS" | "OF_METAL" | "PAID_INTO"
	attrs: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class ZevarKG:
	"""In-memory knowledge graph for Zevar RAG.

	Plan 9.3: ~10,000 items x 5,000 customers x 365 days x 8 categories.
	Total nodes < 100K, edges < 500K. In-memory, no scaling issues.
	"""

	def __init__(self) -> None:
		self.nodes: dict[str, KGNode] = {}
		self.edges: list[KGEdge] = []

	def add_node(self, node_id: str, ntype: str, attrs: dict | None = None) -> None:
		if node_id in self.nodes:
			# Merge attrs
			self.nodes[node_id].attrs.update(attrs or {})
			return
		self.nodes[node_id] = KGNode(id=node_id, type=ntype, attrs=attrs or {})

	def add_edge(self, src: str, dst: str, etype: str, attrs: dict | None = None) -> None:
		self.edges.append(KGEdge(src=src, dst=dst, type=etype, attrs=attrs or {}))

	# ------------------------------------------------------------------
	# 2-hop neighborhood expansion
	# ------------------------------------------------------------------

	def expand_2_hop(self, seed_node_ids: list[str]) -> dict[str, Any]:
		"""Walk up to 2 hops from the seed nodes. Returns the subgraph as
		{ nodes: [...], edges: [...], facts: [str] }.
		"""
		seen_nodes: dict[str, KGNode] = {}
		seen_edges: list[KGEdge] = []

		frontier = set(seed_node_ids)
		for _hop in (1, 2):
			next_frontier: set[str] = set()
			for e in self.edges:
				if e.src in frontier and e.dst not in seen_nodes:
					seen_nodes[e.dst] = self.nodes.get(e.dst, KGNode(id=e.dst, type="?"))
					next_frontier.add(e.dst)
				elif e.dst in frontier and e.src not in seen_nodes:
					seen_nodes[e.src] = self.nodes.get(e.src, KGNode(id=e.src, type="?"))
					next_frontier.add(e.src)
			for e in self.edges:
				if (e.src in frontier and e.dst in frontier) or (e.src in frontier or e.dst in frontier):
					if e not in seen_edges:
						seen_edges.append(e)
			frontier = next_frontier or frontier  # 1-hop may be empty
		return {
			"nodes": list(seen_nodes.values()),
			"edges": seen_edges,
			"facts": [self._edge_fact(e) for e in seen_edges[:30]],
		}

	def _edge_fact(self, e: KGEdge) -> str:
		attrs = ", ".join(f"{k}={v}" for k, v in (e.attrs or {}).items())
		return f"{e.src} -[{e.type}]-> {e.dst} ({attrs})"

	def summary(self) -> str:
		"""A short, plain-text summary of the graph — fed to the LLM prompt."""
		by_type: dict[str, int] = {}
		for n in self.nodes.values():
			by_type[n.type] = by_type.get(n.type, 0) + 1
		by_edge: dict[str, int] = {}
		for e in self.edges:
			by_edge[e.type] = by_edge.get(e.type, 0) + 1
		parts = [f"{k}={v}" for k, v in sorted(by_type.items())]
		parts.extend(f"edge_{k}={v}" for k, v in sorted(by_edge.items()))
		return "KG: " + ", ".join(parts) + f" (total_nodes={len(self.nodes)}, total_edges={len(self.edges)})"


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class KGBuilder:
	"""Build a fresh ZevarKG from Frappe tables.

	Heavy queries: run during the weekly Sunday 03:00 scheduler job.
	"""

	def __init__(self, days_lookback: int = 365) -> None:
		self.days_lookback = days_lookback

	def build(self) -> ZevarKG:
		kg = ZevarKG()
		self._add_metric_nodes(kg)
		self._add_items_and_categories(kg)
		self._add_customers(kg)
		self._add_sales_edges(kg)
		self._add_layaway_edges(kg)
		return kg

	def _add_metric_nodes(self, kg: ZevarKG) -> None:
		"""Time-series metric nodes — daily revenue/repair/layaway volume."""
		from_date = add_days(nowdate(), -self.days_lookback)
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
		for r in rows:
			if not r.get("posting_date"):
				continue
			nid = f"metric:sales:{r['posting_date']}"
			kg.add_node(
				nid,
				"Metric",
				{
					"date": str(r["posting_date"]),
					"revenue": float(r["revenue"] or 0),
					"count": int(r["count"] or 0),
				},
			)

	def _add_items_and_categories(self, kg: ZevarKG) -> None:
		"""Item and category nodes. Limit to the top N most-sold to bound graph size."""
		items = frappe.get_all(
			"Item",
			filters={"disabled": 0, "has_variants": 0, "is_sales_item": 1},
			fields=["name", "item_name", "item_group", "custom_jewelry_type", "custom_metal_type"],
			limit_page_length=2000,
		)
		for it in items:
			nid = f"item:{it['name']}"
			kg.add_node(
				nid,
				"Item",
				{
					"name": it.get("item_name") or it["name"],
					"category": it.get("custom_jewelry_type") or it.get("item_group"),
					"metal": it.get("custom_metal_type"),
				},
			)
			cat = it.get("custom_jewelry_type") or it.get("item_group")
			if cat:
				cat_id = f"category:{cat}"
				kg.add_node(cat_id, "Category", {"name": cat})
				kg.add_edge(nid, cat_id, "IN_CATEGORY")

	def _add_customers(self, kg: ZevarKG) -> None:
		customers = frappe.get_all(
			"Customer",
			filters={"disabled": 0},
			fields=["name", "customer_name", "customer_group"],
			limit_page_length=2000,
		)
		for c in customers:
			nid = f"customer:{c['name']}"
			kg.add_node(
				nid,
				"Customer",
				{
					"name": c.get("customer_name") or c["name"],
					"group": c.get("customer_group"),
				},
			)

	def _add_sales_edges(self, kg: ZevarKG) -> None:
		"""Item -[:SOLD_IN]-> SalesInvoice (per date)."""
		from_date = add_days(nowdate(), -min(self.days_lookback, 90))
		si_items = frappe.qb.DocType("Sales Invoice Item")
		si = frappe.qb.DocType("Sales Invoice")
		rows = (
			frappe.qb.from_(si_items)
			.join(si)
			.on(si_items.parent == si.name)
			.select(si_items.item_code, si.posting_date, si.customer, si_items.amount)
			.where(si.docstatus == 1)
			.where(si.posting_date >= from_date)
			.limit(5000)
		).run(as_dict=True)
		for r in rows:
			item_id = f"item:{r['item_code']}"
			cust_id = f"customer:{r['customer']}"
			metric_id = f"metric:sales:{r['posting_date']}"
			if item_id in kg.nodes:
				kg.add_edge(item_id, metric_id, "SOLD_IN", {"amount": float(r.get("amount") or 0)})
			if cust_id in kg.nodes:
				kg.add_edge(cust_id, metric_id, "PAID_INTO", {"amount": float(r.get("amount") or 0)})

	def _add_layaway_edges(self, kg: ZevarKG) -> None:
		layaway_items = frappe.qb.DocType("Layaway Contract Item")
		lc = frappe.qb.DocType("Layaway Contract")
		rows = (
			frappe.qb.from_(layaway_items)
			.join(lc)
			.on(layaway_items.parent == lc.name)
			.select(lc.customer, layaway_items.item_code, lc.status)
			.where(lc.docstatus == 1)
			.limit(3000)
		).run(as_dict=True)
		for r in rows:
			cust_id = f"customer:{r['customer']}"
			item_id = f"item:{r['item_code']}"
			if cust_id in kg.nodes and item_id in kg.nodes:
				kg.add_edge(cust_id, item_id, "OWNS", {"status": r.get("status")})


# ---------------------------------------------------------------------------
# Persistence (per Q10 — pickle to /tmp)
# ---------------------------------------------------------------------------


def save_kg(kg: ZevarKG, path: str = DEFAULT_PICKLE) -> None:
	with open(path, "wb") as f:
		pickle.dump(kg, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_kg(path: str = DEFAULT_PICKLE) -> ZevarKG | None:
	if not os.path.exists(path):
		return None
	try:
		with open(path, "rb") as f:
			return pickle.load(f)
	except Exception as e:
		frappe.log_error(f"Failed to load KG from {path}: {e}", "ZevarKG")
		return None


def kg_age_hours(path: str = DEFAULT_PICKLE) -> float:
	if not os.path.exists(path):
		return float("inf")
	mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
	delta = datetime.datetime.now() - mtime
	return delta.total_seconds() / 3600.0


# ---------------------------------------------------------------------------
# Frappe-callable entrypoints
# ---------------------------------------------------------------------------


def rebuild_kg_now(days_lookback: int = 365) -> dict:
	"""Rebuild the KG synchronously. Used by the admin button and the scheduler."""
	frappe.only_for(["System Manager"])
	frappe.enqueue(
		"zevar_core.rag.indexing.kg_builder._rebuild_job",
		days_lookback=days_lookback,
		queue="long",
		timeout=900,
		job_id="kg_rebuild",
		deduplicate=True,
	)
	return {"queued": True, "job": "kg_rebuild"}


def _rebuild_job(days_lookback: int = 365) -> None:
	"""Background job — runs the builder and persists the pickle."""
	kg = KGBuilder(days_lookback=days_lookback).build()
	save_kg(kg)
	frappe.logger().info("ZevarKG rebuilt: %d nodes, %d edges", len(kg.nodes), len(kg.edges))


def get_or_build_kg(max_age_hours: float = 168.0) -> ZevarKG:
	"""Return the cached KG, rebuilding it if older than max_age_hours.

	168h = 7 days (matches §9.8 "weekly rebuild").
	"""
	if kg_age_hours() > max_age_hours:
		_rebuild_job()
	return load_kg() or KGBuilder().build()
