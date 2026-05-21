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
			# Serials originally sold on this line, parsed from the
			# newline-separated serial_no field. The UI uses these to let
			# the cashier pick which physical piece is being returned.
			line_serials = [sn.strip() for sn in (item.get("serial_no") or "").splitlines() if sn.strip()]

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
					"serial_nos": line_serials,
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
	return_warehouse: str | None = None,
) -> dict:
	"""
	Create a return invoice for a POS transaction.

	Args:
		original_invoice: Original Sales Invoice name
		items: JSON string of items to return [{item_code, qty, rate, serial_no?}]
		reason: Reason for return
		return_type: Type of return ('refund', 'store_credit', 'exchange')
		refund_mode: Payment mode for refund
		return_warehouse: Warehouse the returned stock lands back into. If
			omitted, falls back to each original line's warehouse so same-
			store returns keep their pre-Fix-#7 behaviour. When set, every
			returned line will use this warehouse — used by cross-store
			returns where a cashier in store B accepts a return that was
			originally sold by store A and the piece must end up in B's
			available inventory.

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

	# Multi-store guard: if the cashier is sending the stock back into a
	# specific warehouse, make sure they're allowed to operate there. Empty
	# return_warehouse keeps the original-line warehouse (same-store return)
	# and is unconditionally allowed.
	if return_warehouse:
		from zevar_core.api.permissions import assert_pos_warehouse_access

		assert_pos_warehouse_access(return_warehouse)

	# Build a quick lookup of the original lines keyed by (item_code,
	# serial_no). Same-item-code lines with different serials are distinct
	# physical pieces and need to be matched precisely.
	original_lines_by_serial: dict[tuple, Any] = {}
	original_lines_by_code: dict[str, Any] = {}
	original_serials_for_item: dict[str, set] = {}
	for orig_line in original.items:
		original_lines_by_code.setdefault(orig_line.item_code, orig_line)
		serial_set = original_serials_for_item.setdefault(orig_line.item_code, set())
		# An ERPNext SI item can carry multiple serials newline-separated.
		for sn in (orig_line.get("serial_no") or "").splitlines():
			sn = sn.strip()
			if sn:
				serial_set.add(sn)
				original_lines_by_serial[(orig_line.item_code, sn)] = orig_line

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
			item_code = return_item.get("item_code")
			serial_no = (return_item.get("serial_no") or "").strip() or None

			# Resolve the original line — preferring an exact serial match
			# when one is supplied, falling back to first-line-by-item-code
			# for non-serialized items.
			original_item = None
			if serial_no:
				original_item = original_lines_by_serial.get((item_code, serial_no))
				if not original_item:
					sold_serials = original_serials_for_item.get(item_code, set())
					if sold_serials:
						frappe.throw(
							_(
								"Serial Number '{0}' was not sold on invoice {1}. "
								"Sold serials for {2}: {3}."
							).format(
								serial_no,
								original_invoice,
								item_code,
								", ".join(sorted(sold_serials)),
							)
						)
					# Item exists on the invoice but had no serials recorded
					# (legacy / non-serialized line). Fall through to the
					# code-based lookup below.
			if not original_item:
				original_item = original_lines_by_code.get(item_code)

			if not original_item:
				frappe.throw(_("Item {0} not found in original invoice.").format(item_code))

			return_qty = flt(return_item.get("qty", 0))
			if return_qty <= 0:
				continue

			# A serialized item must come back one piece at a time so the
			# returning serial maps unambiguously to a stock movement.
			if serial_no and abs(return_qty) > 1:
				frappe.throw(
					_("Serial Number '{0}' is a single physical piece — " "return qty must be 1.").format(
						serial_no
					)
				)

			# Where does the returned stock land?
			# - explicit return_warehouse (cross-store) wins
			# - otherwise the original line's warehouse (same-store)
			line_warehouse = return_warehouse or original_item.warehouse

			# Add with negative quantity. Passing serial_no through is
			# what lets ERPNext's Stock Ledger flip the Serial No back to
			# Active and put the piece in line_warehouse.
			return_line: dict = {
				"item_code": original_item.item_code,
				"item_name": original_item.item_name,
				"qty": -return_qty,
				"rate": flt(return_item.get("rate", original_item.rate)),
				"warehouse": line_warehouse,
				"allow_zero_valuation_rate": 1,
			}
			if serial_no:
				return_line["serial_no"] = serial_no
			return_invoice.append("items", return_line)

		# Clear payments and add refund payment
		return_invoice.payments = []

		if return_type == "refund":
			if not refund_mode:
				refund_mode = "Cash"

			# Validate refund_mode exists and is a real Mode of Payment
			if not frappe.db.exists("Mode of Payment", refund_mode):
				frappe.throw(_("Refund mode '{0}' is not a valid payment method.").format(refund_mode))

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
		# Hide raw technical details from end users
		raw = str(e)
		if "permission" in raw.lower():
			frappe.throw(
				_("You do not have permission to create this return. Please ask a manager for help.")
			)
		frappe.throw(
			_(
				"Unable to process the return at this time. Please check the details and try again, or ask a manager for help."
			)
		)


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
