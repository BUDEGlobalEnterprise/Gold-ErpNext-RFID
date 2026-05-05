"""
Sales Invoice tax hooks.
Automatically applies county tax from Store Location on POS invoices.
"""

import frappe
from frappe.utils import flt


def apply_store_tax(doc, method):
	"""
	Run on Sales Invoice validate.
	Looks up the Store Location via pos_profile (or first-item warehouse)
	and applies the county tax template + rate when not already set.
	"""
	if not doc.is_pos:
		return

	if getattr(doc, "custom_no_tax_override", 0):
		return

	store_info = _resolve_store(doc)
	if not store_info:
		return

	tax_template = store_info.get("tax_template")
	county_rate = flt(store_info.get("county_tax_rate"))

	# Apply the template only when the invoice doesn't already have one
	if tax_template and not doc.taxes_and_charges:
		doc.taxes_and_charges = tax_template
		doc.run_method("set_taxes")

	# Override the first tax row's rate with the county-specific rate
	if county_rate > 0 and doc.get("taxes"):
		doc.taxes[0].rate = county_rate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_store(doc):
	"""Try pos_profile first, then fall back to warehouse on the first item."""
	filters = {"is_active": 1}

	if doc.pos_profile:
		filters["pos_profile"] = doc.pos_profile
	elif doc.items:
		wh = doc.items[0].get("warehouse")
		if wh:
			filters["default_warehouse"] = wh
	else:
		return None

	store = frappe.get_all(
		"Store Location",
		filters=filters,
		fields=["tax_template", "county_tax_rate"],
		limit=1,
	)
	return store[0] if store else None
