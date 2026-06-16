"""
profit_math — the single shared margin definition for the whole suite (Phase 0).

This is the M0 "one true margin" gate. Every margin number in Zevar —
commission payouts, the top-profitability report, the analytics hero, the Sale
Cost Breakdown, and the What-If simulator — MUST come from
:func:`compute_invoice_margin` so they reconcile to the penny.

Implementation note: the per-component COGS helpers (metal / gemstone / labor /
commission / payment / overhead) currently live in
``zevar_core.api.profit_intelligence`` and are invoked here via lazy import to
avoid a circular dependency (``api`` depends on ``services``). The computation
is unchanged — it is the same logic ``calculate_sale_cost_breakdown`` used — so
routing it through here makes every surface agree without changing any number.
A follow-up Phase 0 refactor can move the helpers into this module; until then
this is the sole entry point, which is what makes the surfaces reconcile.
"""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import flt


def get_item_cogs(item_code: str, qty: float = 1.0) -> dict[str, float]:
	"""Per-item COGS at sale: metal (net_weight x gold_rate_at_sale) + gemstone.

	This is the cost basis analytics / what-if should use instead of the
	stock-ledger ``valuation_rate`` (which understates gold-bearing items).
	"""
	from zevar_core.api.pricing import _get_gold_rate
	from zevar_core.api.profit_intelligence import _get_gemstone_value

	qty = flt(qty) or 1.0
	item_doc = (
		frappe.get_cached_value(
			"Item",
			item_code,
			["custom_net_weight_g", "custom_metal_type", "custom_purity", "valuation_rate"],
			as_dict=True,
		)
		or {}
	)

	metal = 0.0
	net_weight = flt(item_doc.get("custom_net_weight_g"))
	if net_weight > 0 and item_doc.get("custom_metal_type") and item_doc.get("custom_purity"):
		gold_rate = flt(_get_gold_rate(item_doc["custom_metal_type"], item_doc["custom_purity"]))
		metal = net_weight * gold_rate * qty
	elif item_doc.get("valuation_rate"):
		# Non-metal items, or metal items without a purity profile: fall back to stock valuation.
		metal = flt(item_doc["valuation_rate"]) * qty

	gemstone = flt(_get_gemstone_value(item_code)) * qty
	return {
		"metal_cogs": flt(metal, 2),
		"gemstone_cogs": flt(gemstone, 2),
		"item_cogs": flt(metal + gemstone, 2),
	}


def compute_invoice_margin(
	invoice: str | Any,
	*,
	include_overhead: bool = True,
	include_payment: bool = True,
	include_labor: bool = True,
	include_commission: bool = True,
) -> dict[str, Any]:
	"""The canonical invoice margin. Accepts an invoice name or a Sales Invoice doc.

	Returns the full breakdown so each consuming surface can read the component it
	needs while all sharing one ``gross_margin_pct``.

	Kwarg ``include_commission=False`` gives the contribution margin *before* this
	sale's commission — the correct basis for the commission engine's "By Profit
	Margin" rule, because ``calculate_commissions`` runs before the splits exist.
	"""
	from zevar_core.api.profit_intelligence import (
		_allocate_labor,
		_allocate_overhead,
		_calculate_item_cogs,
		_calculate_payment_costs,
		_get_commission_total,
	)

	doc = invoice if hasattr(invoice, "items") and hasattr(invoice, "doctype") else frappe.get_doc("Sales Invoice", invoice)

	total_revenue = flt(doc.base_grand_total) or flt(doc.grand_total)
	total_qty = sum(flt(i.qty) for i in (doc.items or []))

	metal_cogs, gemstone_cogs, gold_rate, gold_source, gold_ts = _calculate_item_cogs(doc)
	item_cogs = flt(metal_cogs) + flt(gemstone_cogs)

	labor_cost, labor_detail = _allocate_labor(doc) if include_labor else (0.0, [])
	commission_total = flt(_get_commission_total(doc.name)) if include_commission else 0.0
	payment_cost, payment_detail = _calculate_payment_costs(doc) if include_payment else (0.0, {})
	overhead_cost, overhead_method = (
		_allocate_overhead(total_revenue, doc.posting_date) if include_overhead else (0.0, None)
	)

	total_cost = (
		flt(item_cogs) + flt(labor_cost) + flt(commission_total) + flt(payment_cost) + flt(overhead_cost)
	)
	gross_profit = flt(total_revenue) - flt(total_cost)
	gross_margin_pct = (gross_profit / total_revenue * 100) if total_revenue else 0.0

	return {
		"revenue": flt(total_revenue, 2),
		"total_qty": total_qty,
		"metal_cogs": flt(metal_cogs, 2),
		"gemstone_cogs": flt(gemstone_cogs, 2),
		"item_cogs": flt(item_cogs, 2),
		"making_charge": 0.0,
		"alloy_adjustment": 0.0,
		"labor": flt(labor_cost, 2),
		"labor_detail": labor_detail,
		"commission": flt(commission_total, 2),
		"payment_cost": flt(payment_cost, 2),
		"payment_detail": payment_detail,
		"overhead": flt(overhead_cost, 2),
		"overhead_method": overhead_method,
		"total_cost": flt(total_cost, 2),
		"gross_profit": flt(gross_profit, 2),
		"gross_margin_pct": flt(gross_margin_pct, 2),
		# With every bucket included this equals gross_margin_pct; a future
		# tighter definition can subtract an interchange/overhead floor here.
		"net_contribution_margin_pct": flt(gross_margin_pct, 2),
		"gold_rate_at_sale": flt(gold_rate, 2),
		"gold_rate_source": gold_source,
		"gold_rate_timestamp": gold_ts,
	}
