"""
Layaway API - Contract creation, payments, and cancellation
"""

import frappe
from frappe import _
from frappe.utils import add_months, flt, getdate, nowdate, today

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
		"cancellation_refund_type": getattr(layaway, "cancellation_refund_type", None),
		"store_credit_reference": getattr(layaway, "store_credit_reference", None),
		"store_location": getattr(layaway, "store_location", None),
		"sales_person": getattr(layaway, "sales_person", None),
		"pos_profile": getattr(layaway, "pos_profile", None),
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
		"customer_id_number": doc.customer_id_number,
		"status": doc.status,
		"is_overdue": is_overdue,
		"contract_date": str(doc.contract_date) if doc.contract_date else None,
		"target_completion_date": str(doc.target_completion_date) if doc.target_completion_date else None,
		"duration_months": doc.maximum_duration_months,
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
		"store_credit_reference": doc.store_credit_reference,
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
) -> dict:
	"""Create a new Layaway Contract with deposit and payment schedule."""
	_enforce_layaway_access()

	items_list = frappe.parse_json(items) if isinstance(items, str) else items

	if not items_list:
		frappe.throw(_("At least one item is required."))

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	try:
		duration = int(duration_months)
	except (ValueError, TypeError):
		frappe.throw(_("Duration must be a valid number (3, 6, 9, or 12 months)."))

	if duration not in (3, 6, 9, 12):
		frappe.throw(_("Duration must be 3, 6, 9, or 12 months."))

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
		doc.cancellation_refund_type = "Store Credit Only"
		doc.store_location = store_location
		doc.sales_person = sales_person
		doc.pos_profile = pos_profile
		doc.notes = notes
		doc.terms_accepted = 1 if int(terms_accepted or 0) else 0
		doc.customer_contact = customer_contact
		# Store email in notes if provided
		if customer_email:
			email_note = f"\n\nCustomer Email: {customer_email}"
			doc.notes = (doc.notes or "") + email_note

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

		return {
			"success": True,
			"layaway_id": doc.name,
			"message": "Layaway created successfully",
		}
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

	if int(term_months) not in (3, 6, 9, 12):
		frappe.throw(_("Duration must be 3, 6, 9, or 12 months."))

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
	"""Cancel an active layaway. Generates a Gift Card as strict Store Credit."""
	_enforce_layaway_access()

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status not in ("Active", "Overdue"):
		frappe.throw(_("Layaway is {0}, cannot cancel.").format(doc.status))

	if flt(doc.deposit_amount) <= 0:
		frappe.throw(_("No payments to refund."))

	try:
		gc = frappe.new_doc("Gift Card")
		gc.customer = doc.customer
		gc.initial_value = doc.deposit_amount
		gc.balance = doc.deposit_amount
		gc.source = "Layaway Cancellation"
		gc.issue_date = today()
		gc.status = "Active"
		gc.insert(ignore_permissions=True)
		gc.submit()

		doc.status = "Cancelled"
		doc.store_credit_reference = gc.name
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

		return {
			"success": True,
			"store_credit_id": gc.name,
			"amount_refunded": flt(doc.deposit_amount),
			"message": f"Layaway cancelled. Store Credit {gc.name} generated.",
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Cancellation Failed", frappe.get_traceback())
		frappe.throw(_("Failed to cancel layaway: {0}").format(str(e)))
