"""
Quick Layaway API - Shim module that re-exports from layaway.py with field mapping

The frontend QuickLayawayModal.vue calls zevar_core.api.quick_layaway.* endpoints.
This module delegates to layaway.py and transforms the response schema to match
what the frontend expects.

Field mapping:
  Backend (layaway.py)          Frontend (QuickLayawayModal.vue)
  payment_number              → installment
  payment_date                → due_date
  amount                      → amount (unchanged)
  preview.down_payment        → down_payment_amount
  preview.balance             → balance_amount
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.api.layaway import (
	create_quick_layaway as _create_quick_layaway,
	get_layaway_preview as _get_layaway_preview,
)


@frappe.whitelist(methods=["POST"])
def get_layaway_preview(
	items: str | list,
	customer: str | None = None,
	down_payment_percent: float = 20,
	term_months: int = 3,
) -> dict:
	"""
	Preview layaway schedule with frontend-compatible field names.

	Returns payment_schedule entries with 'installment' and 'due_date'
	instead of 'payment_number' and 'payment_date'.
	"""
	result = _get_layaway_preview(
		items=items,
		customer=customer,
		down_payment_percent=down_payment_percent,
		term_months=term_months,
	)

	mapped_schedule = []
	for entry in result.get("payment_schedule", []):
		mapped_schedule.append(
			{
				"installment": entry.get("payment_number", 0),
				"due_date": entry.get("payment_date", ""),
				"amount": flt(entry.get("amount", 0)),
			}
		)

	preview = result.get("preview", {})
	return {
		"preview": {
			"customer": preview.get("customer"),
			"total": flt(preview.get("total", 0)),
			"down_payment_amount": flt(preview.get("down_payment", 0)),
			"balance_amount": flt(preview.get("balance", 0)),
			"down_payment_percent": flt(down_payment_percent),
			"term_months": int(term_months),
		},
		"payment_schedule": mapped_schedule,
	}


@frappe.whitelist(methods=["POST"])
def create_quick_layaway(
	items: str | list,
	customer: str,
	down_payment_percent: float = 20,
	term_months: int = 3,
	initial_payment: float | None = None,
	initial_payment_mode: str | None = None,
	warehouse: str | None = None,
	notes: str | None = None,
) -> dict:
	"""
	Create a quick layaway with frontend-compatible response schema.

	Returns total_amount, down_payment_amount, and balance_amount
	in addition to the standard contract fields.
	"""
	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	total = sum(flt(item.get("qty", 1)) * flt(item.get("rate")) for item in items_list)
	down_payment = (
		flt(initial_payment) if initial_payment is not None else total * (flt(down_payment_percent) / 100)
	)
	balance = total - down_payment

	result = _create_quick_layaway(
		items=items,
		customer=customer,
		down_payment_percent=down_payment_percent,
		term_months=term_months,
		initial_payment=initial_payment,
		initial_payment_mode=initial_payment_mode,
		warehouse=warehouse,
	)

	return {
		"success": result.get("success", False),
		"contract_name": result.get("contract_name") or result.get("layaway_id"),
		"layaway_id": result.get("layaway_id"),
		"message": result.get("message", "Layaway created successfully"),
		"total_amount": flt(total),
		"down_payment_amount": flt(down_payment),
		"balance_amount": flt(balance),
	}
