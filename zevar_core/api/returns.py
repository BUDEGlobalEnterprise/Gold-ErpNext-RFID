"""
Returns & Void Processing API

Handles return, exchange, and void operations for POS transactions.
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import flt, getdate, now_datetime


def _get_return_reference_field() -> str:
	"""Prefer the custom return link when available, otherwise use ERPNext's standard field."""
	return (
		"custom_return_against"
		if frappe.get_meta("Sales Invoice").get_field("custom_return_against")
		else "return_against"
	)


@frappe.whitelist()
def get_returnable_items(invoice_name: str) -> dict:
	"""
	Get items that can be returned from a POS invoice.

	Args:
		invoice_name: Sales Invoice name

	Returns:
		List of returnable items with quantities
	"""
	frappe.has_permission("Sales Invoice", "read", throw=True)

	invoice = frappe.get_doc("Sales Invoice", invoice_name)

	if not invoice.is_pos:
		frappe.throw(_("Only POS invoices can be returned."))

	if invoice.docstatus != 1:
		frappe.throw(_("Only submitted invoices can be returned."))

	if invoice.status == "Cancelled":
		frappe.throw(_("This invoice has been cancelled."))

	# Check if already returned
	return_reference_field = _get_return_reference_field()
	existing_returns = frappe.get_all(
		"Sales Invoice",
		filters={return_reference_field: invoice_name, "docstatus": 1},
		fields=["name", "grand_total"],
	)

	returned_amount = sum(flt(r.grand_total) for r in existing_returns)

	# Batch fetch returned quantities for all items in this invoice
	returned_qtys = frappe.db.sql(  # nosemgrep
		f"""
		SELECT si_item.item_code, COALESCE(SUM(si_item.qty), 0) as total_qty
		FROM `tabSales Invoice Item` si_item
		JOIN `tabSales Invoice` si ON si.name = si_item.parent
		WHERE si.{return_reference_field} = %s
			AND si.docstatus = 1
		GROUP BY si_item.item_code
		""",
		(invoice_name,),
		as_dict=True,
	)
	returned_qty_map = {r.item_code: r.total_qty for r in returned_qtys}

	items = []
	for item in invoice.items:
		# Calculate already returned quantity
		returned_qty = returned_qty_map.get(item.item_code, 0)

		remaining_qty = flt(item.qty) - flt(returned_qty)

		if remaining_qty > 0:
			items.append(
				{
					"item_code": item.item_code,
					"item_name": item.item_name,
					"qty": item.qty,
					"returned_qty": flt(returned_qty),
					"returnable_qty": remaining_qty,
					"rate": flt(item.rate),
					"amount": flt(item.amount),
					"warehouse": item.warehouse,
				}
			)

	return {
		"invoice_name": invoice_name,
		"customer": invoice.customer,
		"posting_date": str(invoice.posting_date),
		"grand_total": flt(invoice.grand_total),
		"returned_amount": returned_amount,
		"remaining_amount": flt(invoice.grand_total) + returned_amount,  # Negative for returns
		"items": items,
		"existing_returns": existing_returns,
	}


@frappe.whitelist(methods=["POST"])
def create_return_invoice(
	original_invoice: str,
	items: str,
	reason: str,
	return_type: str = "refund",
	refund_mode: str | None = None,
) -> dict:
	"""
	Create a return invoice for a POS transaction.

	Args:
		original_invoice: Original Sales Invoice name
		items: JSON string of items to return [{item_code, qty, rate}]
		reason: Reason for return
		return_type: Type of return ('refund', 'store_credit', 'exchange')
		refund_mode: Payment mode for refund

	Returns:
		Created return invoice details
	"""
	frappe.only_for(["Sales Manager", "System Manager"])

	# Validate return type
	if return_type not in ["refund", "store_credit", "exchange"]:
		frappe.throw(_("Invalid return type. Must be 'refund', 'store_credit', or 'exchange'."))

	items_list = frappe.parse_json(items) if isinstance(items, str) else items

	if not items_list:
		frappe.throw(_("At least one item is required for return."))

	# Get original invoice
	original = frappe.get_doc("Sales Invoice", original_invoice)

	if not original.is_pos:
		frappe.throw(_("Only POS invoices can be returned."))

	if original.docstatus != 1:
		frappe.throw(_("Only submitted invoices can be returned."))

	try:
		meta = frappe.get_meta("Sales Invoice")

		# Create return invoice (Sales Invoice with negative quantities)
		return_invoice = frappe.copy_doc(original)

		return_invoice.is_return = 1
		return_invoice.return_against = original_invoice
		if meta.get_field("custom_return_against"):
			return_invoice.custom_return_against = original_invoice
		if meta.get_field("custom_return_reason"):
			return_invoice.custom_return_reason = reason
		if meta.get_field("custom_return_type"):
			return_invoice.custom_return_type = return_type
		return_invoice.set_posting_time = 1
		return_invoice.posting_date = getdate()
		return_invoice.posting_time = now_datetime().strftime("%H:%M:%S")

		# Clear items and add return items
		return_invoice.items = []

		for return_item in items_list:
			# Find original item
			original_item = next(
				(i for i in original.items if i.item_code == return_item.get("item_code")), None
			)

			if not original_item:
				frappe.throw(
					_("Item {0} not found in original invoice.").format(return_item.get("item_code"))
				)

			return_qty = flt(return_item.get("qty", 0))
			if return_qty <= 0:
				continue

			# Add with negative quantity
			return_invoice.append(
				"items",
				{
					"item_code": original_item.item_code,
					"item_name": original_item.item_name,
					"qty": -return_qty,  # Negative for return
					"rate": flt(return_item.get("rate", original_item.rate)),
					"warehouse": original_item.warehouse,
					"allow_zero_valuation_rate": 1,
				},
			)

		# Clear payments and add refund payment
		return_invoice.payments = []

		if return_type == "refund":
			if not refund_mode:
				refund_mode = "Cash"

			# Calculate refund amount
			refund_amount = sum(flt(item.get("qty", 0)) * flt(item.get("rate", 0)) for item in items_list)
			refund_account = frappe.db.get_value(
				"Mode of Payment Account",
				{"parent": refund_mode, "company": return_invoice.company},
				"default_account",
			)
			if not refund_account:
				refund_account = original.cash_bank_account or original.debit_to
			if not refund_account:
				frappe.throw(_("No refund account configured for mode of payment '{0}'.").format(refund_mode))

			return_invoice.cash_bank_account = refund_account

			return_invoice.append(
				"payments",
				{
					"mode_of_payment": refund_mode,
					"amount": -refund_amount,  # Negative for refund
					"account": refund_account,
				},
			)

		# Clear custom fields that shouldn't be copied
		return_invoice.custom_salesperson_1 = original.custom_salesperson_1
		return_invoice.custom_salesperson_2 = original.custom_salesperson_2

		return_invoice.insert(ignore_permissions=True)
		return_invoice.submit()

		# Log the return
		from zevar_core.api.audit_log import log_event

		log_event(
			event_type="invoice_returned",
			details={
				"original_invoice": original_invoice,
				"return_invoice": return_invoice.name,
				"return_type": return_type,
				"reason": reason,
				"items": items_list,
			},
			reference_document=return_invoice.name,
		)

		return {
			"success": True,
			"return_invoice": return_invoice.name,
			"grand_total": flt(return_invoice.grand_total),
			"return_type": return_type,
			"message": _("Return invoice {0} created successfully.").format(return_invoice.name),
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Return Invoice Creation Failed", frappe.get_traceback())
		frappe.throw(_("Failed to create return invoice: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def void_invoice(invoice_name: str, reason: str, manager_pin: str) -> dict:
	"""
	Void a POS invoice (cancel with manager approval).

	Args:
		invoice_name: Sales Invoice name
		reason: Reason for voiding
		manager_pin: Manager's PIN for approval

	Returns:
		Void status
	"""
	from zevar_core.api.permissions import verify_manager_pin

	# Verify manager PIN
	manager = verify_manager_pin(manager_pin)
	if not manager:
		frappe.throw(_("Invalid manager PIN."), frappe.ValidationError)

	# Get invoice
	invoice = frappe.get_doc("Sales Invoice", invoice_name)

	if not invoice.is_pos:
		frappe.throw(_("Only POS invoices can be voided."))

	if invoice.docstatus != 1:
		frappe.throw(_("Only submitted invoices can be voided."))

	if invoice.status == "Cancelled":
		frappe.throw(_("This invoice is already cancelled."))

	# Check if has returns
	returns = frappe.db.count("Sales Invoice", {"custom_return_against": invoice_name, "docstatus": 1})
	if returns > 0:
		frappe.throw(_("This invoice has returns and cannot be voided."))

	try:
		# Add comment before cancelling
		invoice.add_comment("Comment", f"Voided by {manager['user']}. Reason: {reason}")

		# Cancel the invoice
		invoice.cancel()

		# Log the void
		from zevar_core.api.audit_log import log_event

		log_event(
			event_type="invoice_voided",
			details={
				"invoice": invoice_name,
				"reason": reason,
				"voided_by": manager["user"],
			},
			reference_document=invoice_name,
		)

		return {
			"success": True,
			"invoice_name": invoice_name,
			"status": "Cancelled",
			"voided_by": manager["user"],
			"message": _("Invoice {0} has been voided.").format(invoice_name),
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Invoice Void Failed", frappe.get_traceback())
		frappe.throw(_("Failed to void invoice: {0}").format(str(e)))


@frappe.whitelist()
def get_return_history(invoice_name: str | None = None, customer: str | None = None) -> list:
	"""
	Get return history for an invoice or customer.

	Args:
		invoice_name: Original invoice name
		customer: Customer name

	Returns:
		List of returns
	"""
	frappe.has_permission("Sales Invoice", "read", throw=True)

	filters = {"is_return": 1, "docstatus": 1}

	if invoice_name:
		filters["custom_return_against"] = invoice_name

	returns = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=[
			"name",
			"custom_return_against",
			"customer",
			"posting_date",
			"grand_total",
			"custom_return_type",
			"custom_return_reason",
		],
		order_by="posting_date desc",
		limit_page_length=50,
	)

	if customer and not invoice_name:
		returns = [r for r in returns if r.customer == customer]

	return returns
