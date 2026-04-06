"""
Layaway API - Contract creation, payments, and cancellation
"""

import frappe
from frappe import _
from frappe.utils import add_months, flt, today


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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	# Build filters
	filters = {"docstatus": ["!=", 2]}

	if status:
		filters["status"] = status

	if customer:
		filters["customer"] = ["like", f"%{customer}%"]

	if search:
		filters["name"] = ["like", f"%{search}%"]

	# Get total count for pagination
	total_count = frappe.db.count("Layaway Contract", filters=filters)

	# Calculate pagination
	total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
	offset = (page - 1) * page_size

	# Get layaway contracts
	layaways = frappe.get_all(
		"Layaway Contract",
		filters=filters,
		fields=[
			"name",
			"customer",
			"status",
			"contract_date",
			"target_completion_date",
			"total_amount",
			"deposit_amount",
			"balance_amount",
			"maximum_duration_months",
			"cancellation_refund_type",
			"store_credit_reference",
			"creation",
		],
		order_by="creation desc",
		start=offset,
		page_length=page_size,
	)

	# Enrich layaway data
	for layaway in layaways:
		# Get customer name
		if layaway.customer:
			layaway.customer_name = (
				frappe.db.get_value("Customer", layaway.customer, "customer_name") or layaway.customer
			)

		# Calculate next payment due
		if layaway.status == "Active":
			pending_payments = frappe.get_all(
				"Layaway Payment Schedule",
				filters={"parent": layaway.name, "status": "Pending"},
				fields=["payment_date", "expected_amount"],
				order_by="payment_date asc",
				limit=1,
			)
			if pending_payments:
				layaway.next_payment_date = str(pending_payments[0].payment_date)
				layaway.next_payment_amount = flt(pending_payments[0].expected_amount)

		# Get item count
		item_count = frappe.db.count("Layaway Contract Item", filters={"parent": layaway.name})
		layaway.item_count = item_count

		# Check if overdue (based on target date OR overdue payment schedule entries)
		layaway.is_overdue = False
		if layaway.status == "Active":
			from frappe.utils import getdate

			overdue_flag = False
			if layaway.target_completion_date and getdate(layaway.target_completion_date) < getdate():
				overdue_flag = True

			if not overdue_flag:
				overdue_payments = frappe.get_all(
					"Layaway Payment Schedule",
					filters={
						"parent": layaway.name,
						"status": "Pending",
						"payment_date": ["<", today()],
					},
					limit=1,
				)
				if overdue_payments:
					overdue_flag = True

			layaway.is_overdue = overdue_flag

	return {
		"layaways": layaways,
		"pagination": {
			"page": page,
			"total_pages": total_pages,
			"total_count": total_count,
			"page_size": page_size,
		},
	}


@frappe.whitelist(methods=["GET"])
def get_layaway_details(layaway_id: str) -> dict:
	"""Return full details of a Layaway Contract including items and schedule."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	from frappe.utils import getdate

	is_overdue = False
	if doc.status == "Active":
		if doc.target_completion_date and getdate(doc.target_completion_date) < getdate():
			is_overdue = True
		if not is_overdue:
			overdue_payments = frappe.get_all(
				"Layaway Payment Schedule",
				filters={
					"parent": doc.name,
					"status": "Pending",
					"payment_date": ["<", today()],
				},
				limit=1,
			)
			if overdue_payments:
				is_overdue = True

	payment_schedule = []
	for row in doc.payment_schedule:
		schedule_status = row.status
		if row.status == "Pending" and getdate(row.payment_date) < getdate():
			schedule_status = "Overdue"
		payment_schedule.append(
			{
				"payment_date": str(row.payment_date),
				"expected_amount": flt(row.expected_amount),
				"paid_amount": flt(row.paid_amount),
				"status": schedule_status,
			}
		)

	return {
		"layaway_id": doc.name,
		"customer": doc.customer,
		"status": doc.status,
		"is_overdue": is_overdue,
		"contract_date": str(doc.contract_date),
		"target_completion_date": str(doc.target_completion_date),
		"duration_months": doc.maximum_duration_months,
		"total_amount": flt(doc.total_amount),
		"deposit_amount": flt(doc.deposit_amount),
		"balance_amount": flt(doc.balance_amount),
		"cancellation_refund_type": doc.cancellation_refund_type,
		"store_credit_reference": doc.store_credit_reference,
		"items": [
			{
				"item_code": row.item_code,
				"qty": flt(row.qty),
				"rate": flt(row.rate),
				"amount": flt(row.amount),
			}
			for row in doc.items
		],
		"payment_schedule": payment_schedule,
	}


@frappe.whitelist()
def get_customer_layaways(customer: str) -> list:
	"""Return all Layaway Contracts for a customer, newest first."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

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
) -> dict:
	"""Create a new Layaway Contract with deposit and payment schedule."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	items_list = frappe.parse_json(items) if isinstance(items, str) else items

	# --- Input validation ---
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

	if not warehouse or not frappe.db.exists("Warehouse", warehouse):
		frappe.throw(
			_(
				"Warehouse '{0}' not found. Please ensure a store location has an active default warehouse."
			).format(warehouse)
		)

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

	# --- Build contract ---
	try:
		doc = frappe.new_doc("Layaway Contract")
		doc.customer = customer
		doc.contract_date = today()
		doc.maximum_duration_months = str(duration)
		doc.target_completion_date = add_months(today(), duration)
		doc.cancellation_refund_type = "Store Credit Only"

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
				},
			)

		doc.total_amount = total_amount
		doc.deposit_amount = deposit
		doc.balance_amount = total_amount - deposit

		# Initial deposit entry in schedule
		doc.append(
			"payment_schedule",
			{
				"payment_date": today(),
				"expected_amount": deposit,
				"paid_amount": deposit,
				"status": "Paid",
			},
		)

		# Generate remaining monthly schedule
		remaining_months = duration - 1
		if remaining_months > 0 and doc.balance_amount > 0:
			monthly_payment = doc.balance_amount / remaining_months
			for i in range(1, remaining_months + 1):
				doc.append(
					"payment_schedule",
					{
						"payment_date": add_months(today(), i),
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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

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
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

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
def process_layaway_payment(layaway_id: str, payment_amount: float, mode_of_payment: str) -> dict:
	"""Process a payment towards a layaway balance."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status != "Active":
		frappe.throw(_("Layaway is {0}, cannot process payment.").format(doc.status))

	amount = flt(payment_amount)
	if amount <= 0:
		frappe.throw(_("Payment amount must be greater than zero."))

	if amount > flt(doc.balance_amount):
		frappe.throw(_("Payment amount cannot exceed balance amount."))

	if not mode_of_payment:
		frappe.throw(_("Mode of payment is required."))

	try:
		# Distribute payment across pending schedule rows
		remaining = amount
		for row in doc.payment_schedule:
			if row.status == "Pending" and remaining > 0:
				needed = flt(row.expected_amount) - flt(row.paid_amount)
				applied = min(remaining, needed)
				row.paid_amount += applied
				remaining -= applied

				if row.paid_amount >= row.expected_amount:
					row.status = "Paid"

		doc.balance_amount -= amount
		doc.deposit_amount += amount

		if doc.balance_amount <= 0:
			doc.status = "Completed"

		doc.save(ignore_permissions=True)

		return {
			"success": True,
			"new_balance": doc.balance_amount,
			"status": doc.status,
			"message": "Payment processed successfully",
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Payment Failed", frappe.get_traceback())
		frappe.throw(_("Failed to process layaway payment: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def cancel_layaway(layaway_id: str) -> dict:
	"""Cancel an active layaway. Generates a Gift Card as strict Store Credit."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not layaway_id or not frappe.db.exists("Layaway Contract", layaway_id):
		frappe.throw(_("Layaway Contract '{0}' not found.").format(layaway_id))

	doc = frappe.get_doc("Layaway Contract", layaway_id)

	if doc.status != "Active":
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
		doc.save(ignore_permissions=True)

		return {
			"success": True,
			"store_credit_id": gc.name,
			"amount_refunded": doc.deposit_amount,
			"message": f"Layaway cancelled. Store Credit {gc.name} generated.",
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Layaway Cancellation Failed", frappe.get_traceback())
		frappe.throw(_("Failed to cancel layaway: {0}").format(str(e)))
