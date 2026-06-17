# -*- coding: utf-8 -*-
# Copyright (c) 2025, Zevar and contributors
# For license information, please see license.txt

"""Defensive doc-event fan-out for the monitor suite (Quick-Win Q1/Q2).

These hooks run on Sales Invoice ``on_submit`` / ``on_cancel``. They are
*auxiliary* — they populate the Sale Cost Breakdown (profit spine) and the
Performance Log (workforce spine) — and must NEVER block the primary invoice
transaction. Each underlying hook is wrapped so that any failure is recorded
via ``frappe.log_error`` and skipped instead of propagating (which would roll
back the invoice submit).

Registered from ``zevar_core/hooks.py``::

    "Sales Invoice": {
        "on_submit": [..., "zevar_core.api.monitor_hooks.on_invoice_submit"],
        "on_cancel": [..., "zevar_core.api.monitor_hooks.on_invoice_cancel"],
    }

Order note: ``on_invoice_submit`` is appended AFTER ``commission.calculate_commissions``
so commission splits already exist when the Sale Cost Breakdown and the Sale
Completed Performance Log are written (both read commission attribution).
"""

from __future__ import annotations

import frappe

from zevar_core.api.profit_intelligence import (
	cancel_sale_cost_breakdown,
	calculate_sale_cost_breakdown,
)
from zevar_core.api.performance import log_sale_cancel_event, log_sale_event


def _safe(label: str, fn, doc, method=None) -> None:
	"""Run an auxiliary doc-event hook defensively.

	A failure is logged to Error Log and swallowed so the invoice submit/cancel
	is not aborted. The manual ``recalculate_breakdown`` endpoint still surfaces
	real errors because it calls ``calculate_sale_cost_breakdown`` directly.
	"""
	try:
		fn(doc, method)
	except Exception:
		frappe.log_error(
			title=f"Monitor hook failed: {label}",
			message=frappe.get_traceback(),
		)


def on_invoice_submit(doc, method=None):
	"""Sales Invoice on_submit: write Sale Cost Breakdown + Sale Completed log."""
	_safe("calculate_sale_cost_breakdown", calculate_sale_cost_breakdown, doc, method)
	_safe("log_sale_event", log_sale_event, doc, method)


def on_invoice_cancel(doc, method=None):
	"""Sales Invoice on_cancel: remove Sale Cost Breakdown + log the cancellation."""
	_safe("cancel_sale_cost_breakdown", cancel_sale_cost_breakdown, doc, method)
	_safe("log_sale_cancel_event", log_sale_cancel_event, doc, method)
