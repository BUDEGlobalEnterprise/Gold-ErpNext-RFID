"""
Layaway API - Contract creation, payments, and cancellation
"""

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate, nowdate, today, add_days

from zevar_core.constants import (
	DEFAULT_AUTO_FORFEIT_DAYS,
	DEFAULT_CANCELLATION_FEE_PERCENT,
	LAYAWAY_DURATION_OPTIONS,
	LAYAWAY_DURATION_LABELS,
	LAYAWAY_PLAN_SUGGESTIONS,
	MAX_EXTENSIONS_ALLOWED,
)

LAYAWAY_ALLOWED_ROLES = ["Sales User", "Sales Manager", "System Manager"]


def _enforce_layaway_access() -> None:
	frappe.only_for(LAYAWAY_ALLOWED_ROLES)


def _coerce_statuses(statuses: str | list | tuple | None) -> list[str]:
	if not statuses:
		return []

	status_values = frappe.parse_json(statuses) if isinstance(statuses, str) else statuses
	if not isinstance(status_values, (list, tuple)):
		status_values = [status_values]

	return [str(status).strip() for status in status_values if str(status).strip()]


def _get_next_pending_payment(layaway_id: str) -> dict | None:
	pending_payments = frappe.get_all(
		"Layaway Payment Schedule",
		filters={"parent": layaway_id, "status": "Pending"},
		fields=["payment_date", "expected_amount"],
		order_by="payment_date asc",
		limit=1,
	)
	if not pending_payments:
		return None

	return {
		"payment_date": str(pending_payments[0].payment_date),
		"expected_amount": flt(pending_payments[0].expected_amount),
	}


def _is_layaway_overdue(layaway_id: str, status: str, target_completion_date=None) -> bool:
	if status not in ("Active", "Overdue"):
		return False

	if target_completion_date and getdate(target_completion_date) < getdate():
		return True

	overdue_payments = frappe.get_all(
		"Layaway Payment Schedule",
		filters={
			"parent": layaway_id,
			"status": "Pending",
			"payment_date": ["<", today()],
		},
		limit=1,
	)
	return bool(overdue_payments)


def _serialize_layaway_row(layaway) -> dict:
	next_payment = _get_next_pending_payment(layaway.name)

	return {
		"name": layaway.name,
		"customer": layaway.customer,
		"customer_name": getattr(layaway, "customer_name", None) or layaway.customer,
		"customer_contact": getattr(layaway, "customer_contact", None),
		"customer_email": getattr(layaway, "customer_email", None),
		"customer_id_number": getattr(layaway, "customer_id_number", None),
		"status": layaway.status,
		"contract_date": str(layaway.contract_date) if getattr(layaway, "contract_date", None) else None,
		"target_completion_date": (
			str(layaway.target_completion_date) if getattr(layaway, "target_completion_date", None) else None
		),
		"total_amount": flt(layaway.total_amount),
		"deposit_amount": flt(layaway.deposit_amount),
		"balance_amount": flt(layaway.balance_amount),
		"maximum_duration_months": getattr(layaway, "maximum_duration_months", None),
		"duration_label": LAYAWAY_DURATION_LABELS.get(
			int(getattr(layaway, "maximum_duration_months", 0) or 0), ""
		),
		"cancellation_refund_type": getattr(layaway, "cancellation_refund_type", None),
		"cancellation_fee_percent": flt(
			getattr(layaway, "cancellation_fee_percent", DEFAULT_CANCELLATION_FEE_PERCENT)
		),
		"cancellation_fee_amount": flt(getattr(layaway, "cancellation_fee_amount", 0)),
		"store_credit_reference": getattr(layaway, "store_credit_reference", None),
		"store_location": getattr(layaway, "store_location", None),
		"sales_person": getattr(layaway, "sales_person", None),
		"pos_profile": getattr(layaway, "pos_profile", None),
		"extension_count": getattr(layaway, "extension_count", 0),
		"original_target_date": str(getattr(layaway, "original_target_date", ""))
		if getattr(layaway, "original_target_date", None)
		else None,
		"auto_forfeit_days": getattr(layaway, "auto_forfeit_days", DEFAULT_AUTO_FORFEIT_DAYS),
		"inventory_reserved": int(getattr(layaway, "inventory_reserved", 0)),
		"creation": str(layaway.creation) if getattr(layaway, "creation", None) else None,
		"item_count": frappe.db.count("Layaway Contract Item", filters={"parent": layaway.name}),
		"is_overdue": _is_layaway_overdue(
			layaway.name,
			layaway.status,
			getattr(layaway, "target_completion_date", None),
		),
		"next_payment_date": next_payment["payment_date"] if next_payment else None,
		"next_payment_amount": next_payment["expected_amount"] if next_payment else None,
	}


@frappe.whitelist(methods=["GET"])
def get_layaway_hub_stats() -> dict:
	"""Return aggregate stats for the Layaway Hub dashboard."""
	_enforce_layaway_access()

	active_count = frappe.db.count(
		"Layaway Contract", filters={"status": ["in", ["Active", "Overdue"]], "docstatus": ["!=", 2]}
	)
	overdue_count = frappe.db.count("Layaway Contract", filters={"status": "Overdue", "docstatus": ["!=", 2]})

	outstanding_result = frappe.db.sql(
		"""SELECT COALESCE(SUM(balance_amount), 0) as total
		FROM `tabLayaway Contract`
		WHERE status IN ('Active', 'Overdue') AND docstatus != 2""",
		as_dict=True,
	)
	outstanding_balance = flt(outstanding_result[0]["total"]) if outstanding_result else 0

	today_payment_count = frappe.db.count(
		"Layaway Payment Schedule",
		filters={"status": "Paid", "paid_amount": [">", 0]},
	)

	return {
		"active_count": active_count,
		"overdue_count": overdue_count,
		"outstanding_balance": outstanding_balance,
		"today_payment_count": today_payment_count,
	}


@frappe.whitelist(methods=["GET"])
def get_all_layaways(
	status: str | None = None,
	customer: str | None = None,
	search: str | None = None,
	page: int = 1,
	page_size: int = 20,
) -> dict:
	"""
	Get all layaway contracts with filtering and pagination.

	Args:
		status: Filter by status (Active, Completed, Cancelled, Defaulted)
		customer: Filter by customer name
		search: Search by contract number or customer name
		page: Page number for pagination
		page_size: Number of records per page

	Returns:
		dict: Contains 'layaways' list and 'pagination' info
	"""
	_enforce_layaway_access()

	filters = {"docstatus": ["!=", 2]}

	if status:
		filters["status"] = status

	if customer:
		filters["customer"] = ["like", f"%{customer}%"]

	if search:
		filters["name"] = ["like", f"%{search}%"]

	total_count = frappe.db.count("Layaway Contract", filters=filters)
	total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
	offset = (page - 1) * page_size

	layaways = frappe.get_all(
		"Layaway Contract",
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"customer_contact",
			"customer_id_number",
			"status",
			"contract_date",
			"target_completion_date",
			"total_amount",
			"deposit_amount",
			"balance_amount",
			"maximum_duration_months",
			"cancellation_refund_type",
			"store_credit_reference",
			"store_location",
			"sales_person",
			"pos_profile",
			"creation",
		],
		order_by="creation desc",
		start=offset,
		page_length=page_size,
	)

	return {
		"layaways": [_serialize_layaway_row(layaway) for layaway in layaways],
		"pagination": {
			"page": page,
			"total_pages": total_pages,
			"total_count": total_count,
			"page_size": page_size,
		},
	}


@frappe.whitelist(methods=["GET"])
def search_layaway_contracts(
	query: str | None = None, statuses: str | list | tuple | None = None, limit: int = 20
) -> list[dict]:
	"""Search layaway contracts by contract number, customer, phone, or ID."""
	_enforce_layaway_access()

	filters = {"docstatus": ["!=", 2]}
	status_list = _coerce_statuses(statuses)
	if status_list:
		filters["status"] = ["in", status_list]

	contracts = frappe.get_all(
		"Layaway Contract",
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"customer_contact",
			"customer_id_number",
			"status",
			"contract_date",
			"target_completion_date",
			"total_amount",
			"deposit_amount",
			"balance_amount",
			"maximum_duration_months",
			"cancellation_refund_type",
			"store_credit_reference",
			"store_location",
			"sales_person",
			"pos_profile",
			"creation",
		],
		order_by="modified desc",
		page_length=max(1, min(int(limit or 20), 50)),
	)

	needle = (query or "").strip().lower()
	if needle:
		contracts = [
			contract
			for contract in contracts
			if needle in (contract.name or "").lower()
			or needle in (contract.customer or "").lower()
			or needle in (contract.customer_name or "").lower()
			or needle in (contract.customer_contact or "").lower()
			or needle in (contract.customer_id_number or "").lower()
		]

	return [_serialize_layaway_row(contract) for contract in contracts]


@frappe.whitelist(methods=["GET"])
def get_layaway_details(layaway_id: str) -> dict:
	"""Return full details of a Layaway Contract including items and schedule."""
	_enforce_layaway_access()

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)
	is_overdue = _is_layaway_overdue(doc.name, doc.status, doc.target_completion_date)

	payment_schedule = []
	for row in doc.payment_schedule:
		schedule_status = row.status
		if row.status == "Pending" and getdate(row.payment_date) < getdate():
			schedule_status = "Overdue"
		payment_schedule.append(
			{
				"name": row.name,
				"payment_date": str(row.payment_date),
				"expected_amount": flt(row.expected_amount),
				"paid_amount": flt(row.paid_amount),
				"mode_of_payment": row.mode_of_payment,
				"reference_number": row.reference_number,
				"status": schedule_status,
			}
		)

	return {
		"layaway_id": doc.name,
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"customer_contact": doc.customer_contact,
		"customer_email": getattr(doc, "customer_email", None),
		"customer_id_number": doc.customer_id_number,
		"status": doc.status,
		"is_overdue": is_overdue,
		"contract_date": str(doc.contract_date) if doc.contract_date else None,
		"target_completion_date": str(doc.target_completion_date) if doc.target_completion_date else None,
		"duration_months": doc.maximum_duration_months,
		"duration_label": LAYAWAY_DURATION_LABELS.get(int(doc.maximum_duration_months or 0), ""),
		"store_location": doc.store_location,
		"sales_person": doc.sales_person,
		"pos_profile": doc.pos_profile,
		"total_amount": flt(doc.total_amount),
		"deposit_amount": flt(doc.deposit_amount),
		"balance_amount": flt(doc.balance_amount),
		"total_paid": flt(doc.total_paid),
		"payment_count": doc.payment_count,
		"last_payment_date": str(doc.last_payment_date) if doc.last_payment_date else None,
		"last_payment_amount": flt(doc.last_payment_amount),
		"cancellation_refund_type": doc.cancellation_refund_type,
		"cancellation_fee_percent": flt(
			getattr(doc, "cancellation_fee_percent", DEFAULT_CANCELLATION_FEE_PERCENT)
		),
		"cancellation_fee_amount": flt(getattr(doc, "cancellation_fee_amount", 0)),
		"store_credit_reference": doc.store_credit_reference,
		"extension_count": getattr(doc, "extension_count", 0),
		"original_target_date": str(getattr(doc, "original_target_date", ""))
		if getattr(doc, "original_target_date", None)
		else None,
		"auto_forfeit_days": getattr(doc, "auto_forfeit_days", DEFAULT_AUTO_FORFEIT_DAYS),
		"inventory_reserved": int(getattr(doc, "inventory_reserved", 0)),
		"max_extensions_allowed": MAX_EXTENSIONS_ALLOWED,
		"notes": doc.notes,
		"terms_accepted": int(doc.terms_accepted or 0),
		"customer_signature": doc.customer_signature,
		"items": [
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"description": row.description,
				"qty": flt(row.qty),
				"rate": flt(row.rate),
				"amount": flt(row.amount),
				"serial_no": row.serial_no,
				"batch_no": row.batch_no,
				"warehouse": row.warehouse,
			}
			for row in doc.items
		],
		"payment_schedule": payment_schedule,
	}


@frappe.whitelist()
def get_customer_layaways(customer: str) -> list:
	"""Return all Layaway Contracts for a customer, newest first."""
	_enforce_layaway_access()

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	contracts = frappe.get_all(
		"Layaway Contract",
		filters={"customer": customer, "docstatus": ["!=", 2]},
		fields=[
			"name",
			"status",
			"contract_date",
			"target_completion_date",
			"total_amount",
			"deposit_amount",
			"balance_amount",
		],
		order_by="creation desc",
	)
	return contracts


@frappe.whitelist(methods=["POST"])
def create_layaway(
	customer: str,
	items: str,
	deposit_amount: float,
	duration_months: int,
	warehouse: str | None = None,
	store_location: str | None = None,
	sales_person: str | None = None,
	pos_profile: str | None = None,
	notes: str | None = None,
	terms_accepted: int | bool = 0,
	customer_contact: str | None = None,
	customer_email: str | None = None,
	cancellation_fee_percent: float | None = None,
	auto_forfeit_days: int | None = None,
) -> dict:
	_enforce_layaway_access()

	items_list = frappe.parse_json(items) if isinstance(items, str) else items

	if not items_list:
		frappe.throw(_("At least one item is required."))

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	try:
		duration = int(duration_months)
	except (ValueError, TypeError):
		frappe.throw(_("Duration must be a valid number (1, 2, 3, 6, 9, or 12 months)."))

	if duration not in LAYAWAY_DURATION_OPTIONS:
		frappe.throw(_("Duration must be 1, 2, 3, 6, 9, or 12 months."))

	if not warehouse:
		store_loc = frappe.db.get_value("Store Location", {"is_active": 1}, "default_warehouse")
		if store_loc:
			warehouse = store_loc

	if not warehouse:
		any_wh = frappe.db.get_value("Warehouse", {"is_group": 0, "disabled": 0}, "name")
		if any_wh:
			warehouse = any_wh

	if warehouse and not frappe.db.exists("Warehouse", warehouse):
		warehouse = None

	for item in items_list:
		if not item.get("item_code"):
			frappe.throw(_("Each item must have an item_code."))
		if flt(item.get("rate", 0)) <= 0:
			frappe.throw(_("Item {0}: rate must be greater than zero.").format(item.get("item_code")))

	deposit = flt(deposit_amount)
	total_amount = sum(flt(i.get("qty", 1)) * flt(i.get("rate")) for i in items_list)

	if deposit <= 0:
		frappe.throw(_("Deposit amount must be greater than zero."))

	if deposit >= total_amount:
		frappe.throw(_("Deposit cannot equal or exceed total amount. Use a regular sale instead."))

	try:
		doc = frappe.new_doc("Layaway Contract")
		doc.customer = customer
		doc.contract_date = today()
		doc.maximum_duration_months = str(duration)
		doc.target_completion_date = add_months(today(), duration)
		doc.original_target_date = add_months(today(), duration)
		doc.cancellation_refund_type = "Store Credit Only"
		doc.cancellation_fee_percent = (
			flt(cancellation_fee_percent)
			if cancellation_fee_percent is not None
			else DEFAULT_CANCELLATION_FEE_PERCENT
		)
		doc.auto_forfeit_days = (
			int(auto_forfeit_days) if auto_forfeit_days is not None else DEFAULT_AUTO_FORFEIT_DAYS
		)
		doc.store_location = store_location
		doc.sales_person = sales_person
		doc.pos_profile = pos_profile
		doc.notes = notes
		doc.terms_accepted = 1 if int(terms_accepted or 0) else 0
		doc.customer_contact = customer_contact
		doc.customer_email = customer_email

		for item in items_list:
			qty = flt(item.get("qty", 1))
			rate = flt(item.get("rate"))
			doc.append(
				"items",
				{
					"item_code": item.get("item_code"),
					"qty": qty,
					"rate": rate,
					"amount": qty * rate,
					"warehouse": item.get("warehouse") or warehouse,
				},
			)

		doc.total_amount = total_amount
		doc.deposit_amount = deposit
		doc.balance_amount = total_amount - deposit

		doc.append(
			"payment_schedule",
			{
				"payment_date": today(),
				"expected_amount": deposit,
				"paid_amount": deposit,
				"status": "Paid",
			},
		)

		remaining_months = duration - 1
		if remaining_months > 0 and doc.balance_amount > 0:
			monthly_payment = doc.balance_amount / remaining_months
			for month_index in range(1, remaining_months + 1):
				doc.append(
					"payment_schedule",
					{
						"payment_date": add_months(today(), month_index),
						"expected_amount": monthly_payment,
						"paid_amount": 0,
						"status": "Pending",
					},
				)

		doc.status = "Active"
		doc.insert(ignore_permissions=True)
		doc.submit()

		_reserve_inventory(doc)

		return {
			"success": True,
			"layaway_id": doc.name,
			"message": "Layaway created successfully",
		}
	except frappe.ValidationError:
		frappe.db.rollback()
		raise
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Creation Failed", frappe.get_traceback())
		frappe.throw(_("Failed to create layaway: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def get_layaway_preview(
	items: str | list,
	customer: str | None = None,
	down_payment_percent: float = 20,
	term_months: int = 3,
) -> dict:
	"""Preview layaway totals and schedule for the legacy quick-layaway API."""
	_enforce_layaway_access()

	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	if not items_list:
		frappe.throw(_("At least one item is required."))

	if int(term_months) not in LAYAWAY_DURATION_OPTIONS:
		frappe.throw(_("Duration must be 1, 2, 3, 6, 9, or 12 months."))

	total = sum(flt(item.get("qty", 1)) * flt(item.get("rate")) for item in items_list)
	down_payment = total * (flt(down_payment_percent) / 100)
	balance = total - down_payment

	schedule = []
	if term_months > 0:
		monthly_amount = balance / term_months if term_months else 0
		for month_index in range(1, int(term_months) + 1):
			schedule.append(
				{
					"payment_number": month_index,
					"payment_date": str(add_months(today(), month_index)),
					"amount": flt(monthly_amount),
				}
			)

	return {
		"preview": {
			"customer": customer,
			"total": flt(total),
			"down_payment": flt(down_payment),
			"balance": flt(balance),
			"term_months": int(term_months),
		},
		"payment_schedule": schedule,
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
) -> dict:
	"""Compatibility wrapper for the legacy quick-layaway API."""
	_enforce_layaway_access()

	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	if not items_list:
		frappe.throw(_("At least one item is required."))

	total = sum(flt(item.get("qty", 1)) * flt(item.get("rate")) for item in items_list)
	deposit_amount = (
		flt(initial_payment) if initial_payment is not None else total * (flt(down_payment_percent) / 100)
	)

	if initial_payment_mode and not frappe.db.exists("Mode of Payment", initial_payment_mode):
		frappe.throw(_("Mode of Payment '{0}' not found.").format(initial_payment_mode))

	result = create_layaway(
		customer=customer,
		items=frappe.as_json(items_list),
		deposit_amount=deposit_amount,
		duration_months=int(term_months),
		warehouse=warehouse,
	)

	return {
		"success": result.get("success", False),
		"contract_name": result.get("layaway_id"),
		"layaway_id": result.get("layaway_id"),
		"message": result.get("message"),
	}


@frappe.whitelist(methods=["POST"])
def update_layaway_contract(layaway_id: str, updates: str | dict) -> dict:
	"""Update only the operationally safe layaway fields from the Desk edit flow."""
	_enforce_layaway_access()

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	update_values = frappe.parse_json(updates) if isinstance(updates, str) else (updates or {})
	if not isinstance(update_values, dict):
		frappe.throw(_("Updates payload must be an object."))

	doc = frappe.get_doc("Layaway Contract", layaway_id)
	if doc.status not in ("Draft", "Active", "Overdue"):
		frappe.throw(_("Layaway is {0}, cannot be edited from the Desk flow.").format(doc.status))

	allowed_fields = {
		"customer_contact",
		"customer_id_number",
		"store_location",
		"sales_person",
		"pos_profile",
		"notes",
		"terms_accepted",
	}

	for fieldname, value in update_values.items():
		if fieldname in allowed_fields:
			setattr(doc, fieldname, value)

		doc.save(ignore_permissions=True)

		send_payment_confirmation(doc.name, amount, flt(doc.balance_amount))

		return {
			"success": True,
			"layaway_id": doc.name,
			"message": _("Layaway updated successfully."),
		}


@frappe.whitelist(methods=["POST"])
def process_layaway_payment(
	layaway_id: str,
	payment_amount: float,
	mode_of_payment: str,
	reference_number: str | None = None,
) -> dict:
	"""Process a payment towards a layaway balance."""
	_enforce_layaway_access()

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status not in ("Active", "Overdue"):
		frappe.throw(_("Layaway is {0}, cannot process payment.").format(doc.status))

	amount = flt(payment_amount)
	if amount <= 0:
		frappe.throw(_("Payment amount must be greater than zero."))

	if amount > flt(doc.balance_amount):
		frappe.throw(_("Payment amount cannot exceed balance amount."))

	if not mode_of_payment:
		frappe.throw(_("Mode of payment is required."))

	try:
		remaining = amount
		for row in doc.payment_schedule:
			if row.status == "Pending" and remaining > 0:
				needed = flt(row.expected_amount) - flt(row.paid_amount)
				applied = min(remaining, needed)
				row.paid_amount += applied
				row.mode_of_payment = mode_of_payment
				row.reference_number = reference_number
				remaining -= applied

				if row.paid_amount >= row.expected_amount:
					row.status = "Paid"

		doc.balance_amount = flt(doc.balance_amount) - amount
		doc.deposit_amount = flt(doc.deposit_amount) + amount
		doc.total_paid = flt(doc.total_paid) + amount
		doc.last_payment_date = nowdate()
		doc.last_payment_amount = amount

		if doc.balance_amount <= 0:
			doc.status = "Completed"
			doc.balance_amount = 0
		elif _is_layaway_overdue(doc.name, doc.status, doc.target_completion_date):
			doc.status = "Overdue"
		else:
			doc.status = "Active"

		doc.save(ignore_permissions=True)

		return {
			"success": True,
			"layaway_id": doc.name,
			"new_balance": flt(doc.balance_amount),
			"status": doc.status,
			"message": "Payment processed successfully",
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Payment Failed", frappe.get_traceback())
		frappe.throw(_("Failed to process layaway payment: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def cancel_layaway(layaway_id: str, cancellation_reason: str | None = None) -> dict:
	_enforce_layaway_access()

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status not in ("Active", "Overdue"):
		frappe.throw(_("Layaway is {0}, cannot cancel.").format(doc.status))

	if flt(doc.deposit_amount) <= 0:
		frappe.throw(_("No payments to refund."))

	try:
		cancellation_fee = flt(getattr(doc, "cancellation_fee_amount", 0))
		if cancellation_fee <= 0 and flt(getattr(doc, "cancellation_fee_percent", 0)) > 0:
			cancellation_fee = flt(doc.total_paid) * (flt(doc.cancellation_fee_percent) / 100)

		refund_amount = flt(doc.deposit_amount) - cancellation_fee
		if refund_amount < 0:
			refund_amount = 0

		if refund_amount > 0:
			gc = frappe.new_doc("Gift Card")
			gc.customer = doc.customer
			gc.initial_value = refund_amount
			gc.balance = refund_amount
			gc.source = "Layaway Cancellation"
			gc.issue_date = today()
			gc.status = "Active"
			gc.insert(ignore_permissions=True)
			gc.submit()
			gc_name = gc.name
		else:
			gc_name = None

		doc.status = "Cancelled"
		doc.store_credit_reference = gc_name
		doc.cancellation_fee_amount = cancellation_fee
		if cancellation_reason:
			doc.notes = "\n\n".join(
				part
				for part in [
					(doc.notes or "").strip(),
					_("Cancellation Reason ({0}): {1}").format(nowdate(), cancellation_reason.strip()),
				]
				if part
			)
		doc.save(ignore_permissions=True)

		_release_inventory(doc)

		result = {
			"success": True,
			"amount_refunded": refund_amount,
			"cancellation_fee": cancellation_fee,
			"message": f"Layaway cancelled.",
		}
		if gc_name:
			result["store_credit_id"] = gc_name
			result["message"] = (
				f"Store Credit {gc_name} generated for ${refund_amount:.2f}. Cancellation fee: ${cancellation_fee:.2f}."
			)
		else:
			result["message"] = (
				f"Layaway cancelled. Full cancellation fee of ${cancellation_fee:.2f} applied. No store credit issued."
			)

		return result
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Cancellation Failed", frappe.get_traceback())
		frappe.throw(_("Failed to cancel layaway: {0}").format(str(e)))


def _reserve_inventory(doc) -> None:
	for item in doc.items:
		if item.warehouse and item.item_code:
			try:
				reservation_note = f"Layaway {doc.name}"
				existing = frappe.db.get_value(
					"Stock Reservation Entry",
					{"item_code": item.item_code, "warehouse": item.warehouse, "docstatus": 1},
					"name",
				)
				if not existing:
					from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
						create_stock_reservation_entry,
					)

					create_stock_reservation_entry(
						item_code=item.item_code,
						warehouse=item.warehouse,
						qty=item.qty,
						reservation_note=reservation_note,
					)
			except Exception:
				frappe.log_error(f"Inventory Reservation Failed for {doc.name}", frappe.get_traceback())

		frappe.db.set_value("Layaway Contract", doc.name, "inventory_reserved", 1)


def _release_inventory(doc) -> None:
	if not getattr(doc, "inventory_reserved", 0):
		return
	try:
		reservations = frappe.get_all(
			"Stock Reservation Entry",
			filters={"reservation_note": f"Layaway {doc.name}", "docstatus": 1},
			pluck="name",
		)
		for res_name in reservations:
			res_doc = frappe.get_doc("Stock Reservation Entry", res_name)
			res_doc.cancel()
	except Exception:
		frappe.log_error(f"Inventory Release Failed for {doc.name}", frappe.get_traceback())

	frappe.db.set_value("Layaway Contract", doc.name, "inventory_reserved", 0)


@frappe.whitelist(methods=["GET"])
def suggest_layaway_plan(total_amount: float) -> dict:
	_enforce_layaway_access()

	amount = flt(total_amount)
	if amount <= 0:
		frappe.throw(_("Total amount must be greater than zero."))

	suggestion = None
	for plan in LAYAWAY_PLAN_SUGGESTIONS:
		if amount <= plan["max_price"]:
			suggestion = plan
			break

	if not suggestion:
		suggestion = LAYAWAY_PLAN_SUGGESTIONS[-1]

	duration = suggestion["suggested_duration"]
	down_percent = suggestion["suggested_down_percent"]
	down_payment = amount * (down_percent / 100)
	balance = amount - down_payment
	installment = balance / duration if duration > 0 else 0

	warnings = []
	if duration >= 9:
		warnings.append("Longer plans carry higher forfeiture risk.")
	if amount > 5000:
		warnings.append("High-value items may require manager approval for extended terms.")

	return {
		"suggested_duration": duration,
		"suggested_duration_label": LAYAWAY_DURATION_LABELS.get(duration, f"{duration} months"),
		"suggested_down_percent": down_percent,
		"down_payment": flt(down_payment),
		"balance": flt(balance),
		"installment_amount": flt(installment),
		"warnings": warnings,
		"all_plans": [
			{
				"duration": d,
				"label": LAYAWAY_DURATION_LABELS.get(d, f"{d} months"),
				"down_percent": down_percent,
				"down_payment": flt(amount * (down_percent / 100)),
				"installment": flt((amount - amount * (down_percent / 100)) / d) if d > 0 else 0,
			}
			for d in LAYAWAY_DURATION_OPTIONS
		],
	}


@frappe.whitelist(methods=["POST"])
def extend_layaway(
	layaway_id: str,
	additional_months: int,
	reason: str | None = None,
	approver: str | None = None,
) -> dict:
	_enforce_layaway_access()
	frappe.only_for("Sales Manager", "System Manager")

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	try:
		additional = int(additional_months)
	except (ValueError, TypeError):
		frappe.throw(_("Additional months must be a valid number."))

	if additional not in (1, 2, 3):
		frappe.throw(_("Can extend by 1, 2, or 3 months at a time."))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status not in ("Active", "Overdue"):
		frappe.throw(_("Layaway is {0}, cannot extend.").format(doc.status))

	current_extensions = int(getattr(doc, "extension_count", 0) or 0)
	if current_extensions >= MAX_EXTENSIONS_ALLOWED:
		frappe.throw(_("Maximum {0} extensions already used.").format(MAX_EXTENSIONS_ALLOWED))

	try:
		old_target = doc.target_completion_date
		new_target = add_months(getdate(doc.target_completion_date), additional)

		balance = flt(doc.balance_amount)
		if balance > 0:
			remaining_schedule = [s for s in doc.payment_schedule if s.status == "Pending"]
			for row in remaining_schedule:
				new_date = add_months(getdate(row.payment_date), additional)
				row.payment_date = new_date

			if len(remaining_schedule) == 0 and balance > 0:
				installment = balance / additional
				for m in range(1, additional + 1):
					doc.append(
						"payment_schedule",
						{
							"payment_date": add_months(old_target, m),
							"expected_amount": installment,
							"paid_amount": 0,
							"status": "Pending",
						},
					)

		doc.target_completion_date = new_target
		doc.maximum_duration_months = str(int(doc.maximum_duration_months) + additional)
		doc.extension_count = current_extensions + 1
		if reason:
			doc.notes = "\n\n".join(
				part
				for part in [
					(doc.notes or "").strip(),
					_("Extension ({0}): +{1} months. Reason: {2}").format(
						nowdate(), additional, reason.strip()
					),
				]
				if part
			)
		if doc.status == "Overdue":
			doc.status = "Active"

		doc.save(ignore_permissions=True)

		return {
			"success": True,
			"layaway_id": doc.name,
			"new_target_date": str(new_target),
			"new_duration_months": doc.maximum_duration_months,
			"extensions_used": doc.extension_count,
			"extensions_remaining": MAX_EXTENSIONS_ALLOWED - doc.extension_count,
			"message": _("Layaway extended by {0} months.").format(additional),
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Extension Failed", frappe.get_traceback())
		frappe.throw(_("Failed to extend layaway: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def process_split_layaway_payment(
	layaway_id: str,
	payments: str,
) -> dict:
	_enforce_layaway_access()

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status not in ("Active", "Overdue"):
		frappe.throw(_("Layaway is {0}, cannot process payment.").format(doc.status))

	payments_list = frappe.parse_json(payments) if isinstance(payments, str) else payments
	if not payments_list:
		frappe.throw(_("At least one payment entry is required."))

	total_payment = sum(flt(p.get("amount", 0)) for p in payments_list)
	if total_payment <= 0:
		frappe.throw(_("Total payment amount must be greater than zero."))

	if total_payment > flt(doc.balance_amount):
		frappe.throw(_("Total payment cannot exceed balance amount."))

	try:
		remaining = total_payment
		for row in doc.payment_schedule:
			if row.status == "Pending" and remaining > 0:
				needed = flt(row.expected_amount) - flt(row.paid_amount)
				applied = min(remaining, needed)
				row.paid_amount += applied
				primary_payment = payments_list[0] if payments_list else {}
				row.mode_of_payment = primary_payment.get("mode_of_payment", "Cash")
				row.reference_number = primary_payment.get("reference_number", "")
				remaining -= applied

				if row.paid_amount >= row.expected_amount:
					row.status = "Paid"

		doc.balance_amount = flt(doc.balance_amount) - total_payment
		doc.deposit_amount = flt(doc.deposit_amount) + total_payment
		doc.total_paid = flt(doc.total_paid) + total_payment
		doc.last_payment_date = nowdate()
		doc.last_payment_amount = total_payment

		if doc.balance_amount <= 0:
			doc.status = "Completed"
			doc.balance_amount = 0
			_release_inventory(doc)
		elif _is_layaway_overdue(doc.name, doc.status, doc.target_completion_date):
			doc.status = "Overdue"
		else:
			doc.status = "Active"

		doc.save(ignore_permissions=True)

		return {
			"success": True,
			"layaway_id": doc.name,
			"new_balance": flt(doc.balance_amount),
			"status": doc.status,
			"payment_breakdown": [
				{
					"mode": p.get("mode_of_payment", "Cash"),
					"amount": flt(p.get("amount", 0)),
				}
				for p in payments_list
			],
			"message": "Split payment processed successfully",
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Split Layaway Payment Failed", frappe.get_traceback())
		frappe.throw(_("Failed to process payment: {0}").format(str(e)))


def check_overdue_and_forfeit():
	overdue_contracts = frappe.get_all(
		"Layaway Contract",
		filters={"status": ["in", ["Active", "Overdue"]], "docstatus": ["!=", 2]},
		fields=["name", "status", "target_completion_date", "auto_forfeit_days"],
	)

	today_date = getdate()

	for contract in overdue_contracts:
		doc = frappe.get_doc("Layaway Contract", contract.name)

		has_overdue_payments = False
		days_overdue = 0

		for payment in doc.payment_schedule:
			if payment.status == "Pending" and getdate(payment.payment_date) < today_date:
				has_overdue_payments = True
				days_late = (today_date - getdate(payment.payment_date)).days
				days_overdue = max(days_overdue, days_late)
				payment.status = "Overdue"

		if has_overdue_payments:
			forfeit_days = int(getattr(doc, "auto_forfeit_days", DEFAULT_AUTO_FORFEIT_DAYS))
			if days_overdue >= forfeit_days:
				_auto_forfeit_layaway(doc)
			else:
				if doc.status != "Overdue":
					doc.status = "Overdue"
				doc.save(ignore_permissions=True)
				_send_overdue_reminder(doc, days_overdue)


def _auto_forfeit_layaway(doc):
	cancellation_fee = flt(doc.total_paid)
	refund_amount = flt(doc.deposit_amount) - cancellation_fee

	if refund_amount > 0:
		gc = frappe.new_doc("Gift Card")
		gc.customer = doc.customer
		gc.initial_value = refund_amount
		gc.balance = refund_amount
		gc.source = "Layaway Cancellation"
		gc.issue_date = today()
		gc.status = "Active"
		gc.insert(ignore_permissions=True)
		gc.submit()
		doc.store_credit_reference = gc.name

	doc.status = "Forfeited"
	doc.cancellation_fee_amount = cancellation_fee
	doc.notes = "\n\n".join(
		part
		for part in [
			(doc.notes or "").strip(),
			_("Auto-forfeited on {0} due to {1} days overdue.").format(
				nowdate(), getattr(doc, "auto_forfeit_days", DEFAULT_AUTO_FORFEIT_DAYS)
			),
		]
		if part
	)
	doc.save(ignore_permissions=True)
	_release_inventory(doc)


def _send_overdue_reminder(doc, days_overdue):
	customer_contact = getattr(doc, "customer_contact", None)
	customer_email = getattr(doc, "customer_email", None)

	if customer_contact:
		try:
			next_payment = _get_next_pending_payment(doc.name)
			amount_str = f"${flt(next_payment['expected_amount']):.2f}" if next_payment else "N/A"
			message = f"Your Zevar layaway payment of {amount_str} is {days_overdue} day(s) overdue. Please visit the store to make a payment. Contract: {doc.name}"

			frappe.get_doc(
				{
					"doctype": "SMS Log",
					"sender_name": "Zevar POS",
					"receiver_number": customer_contact,
					"message": message,
				}
			).insert(ignore_permissions=True)
		except Exception:
			frappe.log_error(f"Overdue SMS Failed for {doc.name}", frappe.get_traceback())

	if customer_email:
		try:
			next_payment = _get_next_pending_payment(doc.name)
			amount_str = f"${flt(next_payment['expected_amount']):.2f}" if next_payment else "N/A"
			frappe.sendmail(
				recipients=[customer_email],
				subject=f"Layaway Payment Reminder - {doc.name}",
				message=f"""
				<p>Dear {doc.customer_name},</p>
				<p>Your layaway payment of <strong>{amount_str}</strong> is <strong>{days_overdue} day(s) overdue</strong>.</p>
				<p>Contract: {doc.name}</p>
				<p>Please visit our store to make a payment at your earliest convenience.</p>
				<p>Thank you,<br>Zevar Jewelry</p>
				""",
				reference_doctype="Layaway Contract",
				reference_name=doc.name,
			)
		except Exception:
			frappe.log_error(f"Overdue Email Failed for {doc.name}", frappe.get_traceback())


def send_payment_reminders():
	upcoming = frappe.get_all(
		"Layaway Payment Schedule",
		filters={
			"status": "Pending",
			"payment_date": ["between", [today(), add_days(today(), 3)]],
		},
		fields=["parent", "payment_date", "expected_amount"],
	)

	reminded = set()
	for entry in upcoming:
		if entry.parent in reminded:
			continue
		reminded.add(entry.parent)

		try:
			doc = frappe.get_doc("Layaway Contract", entry.parent)
			if doc.status not in ("Active", "Overdue"):
				continue

			customer_contact = getattr(doc, "customer_contact", None)
			customer_email = getattr(doc, "customer_email", None)
			amount_str = f"${flt(entry.expected_amount):.2f}"
			date_str = getdate(entry.payment_date).strftime("%b %d, %Y")

			if customer_contact:
				message = f"Reminder: Your Zevar layaway payment of {amount_str} is due on {date_str}. Contract: {doc.name}"
				frappe.get_doc(
					{
						"doctype": "SMS Log",
						"sender_name": "Zevar POS",
						"receiver_number": customer_contact,
						"message": message,
					}
				).insert(ignore_permissions=True)

			if customer_email:
				frappe.sendmail(
					recipients=[customer_email],
					subject=f"Layaway Payment Due Soon - {doc.name}",
					message=f"""
					<p>Dear {doc.customer_name},</p>
					<p>This is a friendly reminder that your layaway payment of <strong>{amount_str}</strong> is due on <strong>{date_str}</strong>.</p>
					<p>Contract: {doc.name}</p>
					<p>Please visit our store to make a payment.</p>
					<p>Thank you,<br>Zevar Jewelry</p>
					""",
					reference_doctype="Layaway Contract",
					reference_name=doc.name,
				)
		except Exception:
			frappe.log_error(f"Payment Reminder Failed for {entry.parent}", frappe.get_traceback())


def send_payment_confirmation(layaway_id: str, amount: float, new_balance: float):
	try:
		doc = frappe.get_doc("Layaway Contract", layaway_id)
		customer_contact = getattr(doc, "customer_contact", None)
		customer_email = getattr(doc, "customer_email", None)
		amount_str = f"${flt(amount):.2f}"
		balance_str = f"${flt(new_balance):.2f}"

		if customer_contact:
			message = f"Payment of {amount_str} received for layaway {doc.name}. Remaining balance: {balance_str}. Thank you!"
			frappe.get_doc(
				{
					"doctype": "SMS Log",
					"sender_name": "Zevar POS",
					"receiver_number": customer_contact,
					"message": message,
				}
			).insert(ignore_permissions=True)

		if customer_email:
			frappe.sendmail(
				recipients=[customer_email],
				subject=f"Payment Received - Layaway {doc.name}",
				message=f"""
				<p>Dear {doc.customer_name},</p>
				<p>We received your layaway payment of <strong>{amount_str}</strong>.</p>
				<p>Remaining balance: <strong>{balance_str}</strong></p>
				<p>Contract: {doc.name}</p>
				<p>Thank you for your payment!<br>Zevar Jewelry</p>
				""",
				reference_doctype="Layaway Contract",
				reference_name=doc.name,
			)
	except Exception:
		frappe.log_error(f"Payment Confirmation Failed for {layaway_id}", frappe.get_traceback())
