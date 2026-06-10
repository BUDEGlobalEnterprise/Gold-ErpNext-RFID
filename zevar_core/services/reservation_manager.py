"""
Unified Reservation Manager

Manages both soft holds (logical reservation, no physical stock move)
and hard reserves (physical warehouse transfer) for the Zevar POS.

Soft Hold: Timed reservation for cart suspensions and customer holds.
Hard Reserve: Physical transfer to Reserved warehouse for deposits/layaways.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, now_datetime

# ---------------------------------------------------------------------------
# Soft Hold
# ---------------------------------------------------------------------------


def create_soft_hold(
	item_code: str,
	customer: str,
	warehouse: str,
	serial_no: str | None = None,
	held_by: str | None = None,
	cart_reference: str | None = None,
	hold_minutes: int = 120,
	pos_session: str | None = None,
) -> dict:
	"""Create a timed soft hold. Does NOT physically move stock."""
	_validate_no_conflict(item_code, serial_no, customer)

	res = frappe.new_doc("Stock Reservation")
	res.reservation_type = "Soft Hold"
	res.customer = customer
	res.item_code = item_code
	res.serial_no = serial_no or ""
	res.warehouse_from = warehouse
	res.warehouse_to = warehouse
	res.hold_until = add_to_date(now_datetime(), minutes=hold_minutes)
	res.auto_expire_on = add_to_date(now_datetime(), minutes=hold_minutes)
	res.cart_reference = cart_reference or ""
	res.salesperson = _resolve_employee(held_by)
	res.pos_session = pos_session or ""
	res.insert(ignore_permissions=True)
	res.submit()

	return {"success": True, "reservation": res.name, "type": "Soft Hold"}


# ---------------------------------------------------------------------------
# Hard Reserve
# ---------------------------------------------------------------------------


def create_hard_reserve(
	serial_no: str,
	customer: str,
	warehouse: str,
	deposit_amount: float = 0,
	salesperson: str | None = None,
	hold_until=None,
	notes: str = "",
) -> dict:
	"""Create a hard reserve. Physically transfers serial to Reserved warehouse."""
	res = frappe.new_doc("Stock Reservation")
	res.reservation_type = "Hard Reserve"
	res.customer = customer
	res.serial_no = serial_no
	res.deposit_amount = flt(deposit_amount)
	res.salesperson = salesperson or ""
	res.hold_until = hold_until or add_to_date(now_datetime(), days=30)
	res.notes = notes
	res.insert(ignore_permissions=True)
	res.submit()

	return {"success": True, "reservation": res.name, "type": "Hard Reserve"}


# ---------------------------------------------------------------------------
# Promote Soft → Hard
# ---------------------------------------------------------------------------


def promote_to_hard_reserve(soft_reservation_id: str, deposit_amount: float = 0) -> dict:
	"""Convert a soft hold to a hard reserve."""
	soft = frappe.get_doc("Stock Reservation", soft_reservation_id)
	if soft.reservation_type != "Soft Hold":
		frappe.throw(_("Only soft holds can be promoted to hard reserves"))
	if soft.status != "Active":
		frappe.throw(_("Reservation is not active"))

	serial_no = soft.serial_no
	customer = soft.customer

	# Cancel the soft hold first
	soft.cancel()

	# Create the hard reserve
	result = create_hard_reserve(
		serial_no=serial_no,
		customer=customer,
		warehouse=soft.warehouse_from,
		deposit_amount=deposit_amount,
		salesperson=soft.salesperson,
		hold_until=soft.hold_until,
		notes=f"Promoted from soft hold {soft_reservation_id}",
	)

	# Link them
	hard = frappe.get_doc("Stock Reservation", result["reservation"])
	hard.converted_from = soft_reservation_id
	hard.save(ignore_permissions=True)

	return {"success": True, "reservation": result["reservation"], "promoted_from": soft_reservation_id}


# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------


def release_reservation(reservation_id: str, reason: str | None = None) -> dict:
	"""Release either type of reservation."""
	res = frappe.get_doc("Stock Reservation", reservation_id)
	if res.status != "Active":
		frappe.throw(_("Reservation {0} is not active (status: {1})").format(reservation_id, res.status))

	if reason:
		res.notes = (res.notes or "") + f"\nReleased: {reason}"

	res.cancel()
	return {"success": True, "status": "Cancelled", "reservation": reservation_id}


# ---------------------------------------------------------------------------
# Availability
# ---------------------------------------------------------------------------


def check_availability(item_code: str, warehouse: str, serial_no: str | None = None) -> dict:
	"""Return on_hand, hard_reserved, soft_reserved, available for an item/warehouse."""
	on_hand = flt(
		frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
	)

	hard_reserved = flt(
		frappe.db.count(
			"Stock Reservation",
			filters={
				"item_code": item_code,
				"warehouse_to": ["!=", warehouse],
				"status": "Active",
				"reservation_type": "Hard Reserve",
				"docstatus": 1,
			},
		)
	)

	soft_reserved = flt(
		frappe.db.count(
			"Stock Reservation",
			filters={
				"item_code": item_code,
				"warehouse_from": warehouse,
				"status": "Active",
				"reservation_type": "Soft Hold",
				"docstatus": 1,
			},
		)
	)

	# For serial-specific check
	serial_held_by = None
	if serial_no:
		holder = frappe.db.get_value(
			"Stock Reservation",
			{"serial_no": serial_no, "status": "Active", "docstatus": 1},
			["name", "customer", "reservation_type"],
			as_dict=True,
		)
		if holder:
			serial_held_by = {
				"reservation": holder.name,
				"customer": holder.customer,
				"type": holder.reservation_type,
			}

	return {
		"item_code": item_code,
		"warehouse": warehouse,
		"on_hand": on_hand,
		"hard_reserved": hard_reserved,
		"soft_reserved": soft_reserved,
		"available": on_hand - hard_reserved - soft_reserved,
		"serial_held_by": serial_held_by,
	}


# ---------------------------------------------------------------------------
# Auto-Release on Sale
# ---------------------------------------------------------------------------


def release_reservation_for_invoice(doc, method=None):
	"""Hook: auto-release reservations when a POS invoice is submitted.

	Checks if any invoiced item had an active reservation for the same customer
	and releases it, since the sale itself already deducted the stock.
	"""
	if doc.doctype != "Sales Invoice":
		return

	for item in doc.items:
		# Check serial-specific reservations
		if item.serial_no:
			_releases_for_serial(item.serial_no, doc.customer)

		# Check item-level reservations
		_release_for_item(item.item_code, doc.customer, item.warehouse)


def _releases_for_serial(serial_no: str, customer: str):
	reservations = frappe.get_all(
		"Stock Reservation",
		filters={
			"serial_no": serial_no,
			"customer": customer,
			"status": "Active",
			"docstatus": 1,
		},
		pluck="name",
	)
	for res_name in reservations:
		try:
			release_reservation(res_name, reason=f"Auto-released: sale completed for {customer}")
			frappe.db.commit()
		except Exception:
			frappe.log_error(f"Failed to auto-release reservation {res_name}", frappe.get_traceback())


def _release_for_item(item_code: str, customer: str, warehouse: str):
	reservations = frappe.get_all(
		"Stock Reservation",
		filters={
			"item_code": item_code,
			"customer": customer,
			"warehouse_from": warehouse,
			"status": "Active",
			"docstatus": 1,
		},
		pluck="name",
		limit=1,
	)
	for res_name in reservations:
		try:
			release_reservation(res_name, reason=f"Auto-released: sale completed for {customer}")
			frappe.db.commit()
		except Exception:
			frappe.log_error(f"Failed to auto-release reservation {res_name}", frappe.get_traceback())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_no_conflict(item_code: str, serial_no: str | None, customer: str):
	if not serial_no:
		return
	existing = frappe.db.exists(
		"Stock Reservation",
		{
			"serial_no": serial_no,
			"status": "Active",
			"customer": ["!=", customer],
			"docstatus": 1,
		},
	)
	if existing:
		holder = frappe.db.get_value("Stock Reservation", existing, "customer")
		frappe.throw(
			_("Serial No {0} is already reserved for customer {1} (Reservation: {2})").format(
				serial_no, holder, existing
			)
		)


def _resolve_employee(user_id: str | None) -> str:
	if not user_id:
		user_id = frappe.session.user
	emp = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
	return emp or ""
