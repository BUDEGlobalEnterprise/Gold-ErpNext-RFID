"""
POS API - Invoice creation and settings
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.constants import DEFAULT_TAX_RATES, PAYMENT_MODES

# ---------------------------------------------------------------------------
# Payment validation helpers
# ---------------------------------------------------------------------------

_PAYMENT_ERROR_MAP = {
    "total payment amount must be equal to grand total": _(
        "The payment amount does not match the invoice total. Please check the amounts and try again."
    ),
    "payments amount must be negative": _(
        "Invalid payment amount. Please check the amounts and try again."
    ),
    "account is mandatory": _(
        "A payment account is missing. Please ask a manager to check the payment setup."
    ),
    "cannot pay more than": _(
        "Payment amount is more than the invoice total. Please check the amounts and try again."
    ),
    "serial no": _(
        "There is an issue with a serial number. Please ask a manager for help."
    ),
    "stock": _(
        "There is a stock issue with one of the items. Please ask a manager for help."
    ),
}


def _friendly_payment_error(raw_message: str) -> str:
    """Map internal ERPNext / framework errors to cashier-friendly text."""
    if not raw_message:
        return _(
            "There was a problem processing your payment. Please check the details and try again, or ask a manager for help."
        )
    lowered = raw_message.lower()
    for pattern, friendly in _PAYMENT_ERROR_MAP.items():
        if pattern in lowered:
            return friendly
    return _(
        "There was a problem processing your payment. Please check the details and try again, or ask a manager for help."
    )


def _validate_payments(payments_list, trade_in_list, discount_amount, tax_exempt, warehouse, items_list):
    """
    Proactive payment validation before we build the Sales Invoice.

    Returns:
        tuple: (validated_payments_list, trade_in_credit, computed_grand_total)

    Raises:
        frappe.ValidationError via checkout_bouncer on any issue.
    """
    from frappe.utils import flt

    if not payments_list:
        return [], 0, 0

    # 1. Basic per-payment sanity
    seen_modes = set()
    cleaned_payments = []
    for idx, pay in enumerate(payments_list):
        mode = (pay.get("mode_of_payment") or pay.get("mode", "")).strip()
        amount = flt(pay.get("amount", 0))

        if not mode:
            raise frappe.ValidationError(
                _("Payment #{0} is missing a payment mode. Please select a payment method.").format(idx + 1)
            )
        if amount <= 0:
            raise frappe.ValidationError(
                _("Payment mode '{0}' must have an amount greater than zero.").format(mode)
            )
        if mode in seen_modes:
            raise frappe.ValidationError(
                _("Payment mode '{0}' appears more than once. Please combine the amounts or remove the duplicate.").format(mode)
            )
        seen_modes.add(mode)
        cleaned_payments.append({"mode_of_payment": mode, "amount": amount})

    # 2. Compute expected grand total (same logic as calculate_invoice_totals)
    subtotal = sum(flt(i.get("rate", 0)) * flt(i.get("qty", 1)) for i in (items_list or []))
    discount = max(0.0, flt(discount_amount))
    subtotal_after_discount = max(0.0, subtotal - discount)

    tax = 0.0
    if not tax_exempt:
        settings = get_pos_settings(warehouse)
        tax_rate = flt(settings.get("tax_rate", 0))
        tax = (subtotal_after_discount * tax_rate) / 100

    computed_grand_total = subtotal_after_discount + tax

    # 3. Trade-in credit
    total_trade_in_credit = sum(flt(ti.get("trade_in_value")) for ti in (trade_in_list or []))

    # 4. If cashier already included Trade-In in payments, merge / de-duplicate
    trade_in_in_payments = False
    for pay in cleaned_payments:
        if pay["mode_of_payment"] == "Trade-In":
            trade_in_in_payments = True
            break

    if total_trade_in_credit > 0 and trade_in_in_payments:
        # Replace the manual Trade-In line with the computed one so they match
        cleaned_payments = [p for p in cleaned_payments if p["mode_of_payment"] != "Trade-In"]
        seen_modes.discard("Trade-In")

    total_payments = sum(p["amount"] for p in cleaned_payments)

    # After removing any manual Trade-In, add the computed credit back
    if total_trade_in_credit > 0:
        cleaned_payments.append({"mode_of_payment": "Trade-In", "amount": flt(total_trade_in_credit)})
        total_payments += total_trade_in_credit

    # 5. Validate payment total covers grand total (within 1-cent tolerance)
    if abs(total_payments - computed_grand_total) > 0.01:
        raise frappe.ValidationError(
            _(
                "Total payments ({0}) do not match the invoice total ({1}). "
                "Please adjust the payment amounts and try again."
            ).format(total_payments, computed_grand_total)
        )

    return cleaned_payments, total_trade_in_credit, computed_grand_total


# ---------------------------------------------------------------------------

@frappe.whitelist(methods=["POST"])
def create_pos_invoice(
	items: str,
	payments: str,
	customer: str,
	warehouse: str | None = None,
	discount_amount: float = 0,
	tax_exempt: str | bool = False,
	salespersons: str | None = None,
	layaway_reference: str | None = None,
	trade_ins: str | None = None,
	gift_card_number: str | None = None,
	override_reference: str | None = None,
) -> dict:
	"""
	Create a complete POS Invoice with:
	- Stock reservation/deduction
	- Multiple payment modes (split tender)
	- Tax calculation based on warehouse/store location
	- Salesperson tracking (up to 4 with split percentages)
	- Commission calculation trigger (on submit)
	"""
	from frappe.utils import flt

	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	payments_list = frappe.parse_json(payments) if isinstance(payments, str) else payments
	trade_in_list = frappe.parse_json(trade_ins) if trade_ins else []

	from zevar_core.api.audit_log import log_event_safely

	def checkout_bouncer(message, event_type="permission_denied", details=None):
		"""Log failure and throw error."""
		log_event_safely(
			event_type=event_type,
			details={
				"message": message,
				"customer": customer,
				"items_count": len(items_list) if items_list else 0,
				"additional_details": details or {},
			},
		)
		frappe.throw(
			message, frappe.ValidationError if "permission" not in event_type else frappe.PermissionError
		)

	# Validate the user has an allowed role for POS invoicing
	allowed_roles = {
		"Sales User",
		"Sales Manager",
		"Store Manager",
		"POS Manager",
		"Employee",
		"Employee Self Service",
		"System Manager",
	}
	user_roles = set(frappe.get_roles())
	if not user_roles & allowed_roles:
		checkout_bouncer(
			_(
				"You do not have permission to create POS Invoices. Required role: Sales User, Employee, or equivalent."
			),
			"permission_denied",
		)

	if not items_list:
		checkout_bouncer(_("At least one item is required."), "invoice_failed")

	if not payments_list:
		checkout_bouncer(_("At least one payment mode is required."), "invoice_failed")

	# Resolve warehouse BEFORE per-item validation so the stock and serial
	# checks below run against the final warehouse, not a stale or
	# unvalidated client value. Order is:
	#   1. caller-supplied (after multi-store check)
	#   2. user's active POS Opening Entry profile
	#   3. first active Store Location's default warehouse
	if not warehouse:
		active_pos_profile = frappe.db.get_value(
			"POS Opening Entry",
			filters={"user": frappe.session.user, "docstatus": 1, "status": "Open"},
			fieldname="pos_profile",
			order_by="creation desc",
		)
		if active_pos_profile:
			warehouse = frappe.db.get_value("POS Profile", active_pos_profile, "warehouse")

		if not warehouse:
			store_loc = frappe.db.get_value("Store Location", {"is_active": 1}, "default_warehouse")
			if store_loc:
				warehouse = store_loc

	if not warehouse:
		checkout_bouncer(
			_("Warehouse is required. Please select a store location or configure a default warehouse."),
			"invoice_failed",
		)

	if not frappe.db.exists("Warehouse", warehouse):
		checkout_bouncer(
			_("Warehouse '{0}' not found. Please ensure a valid warehouse is configured.").format(warehouse),
			"invoice_failed",
		)

	# Multi-store enforcement: a cashier in store A must not be able to
	# pass store B's warehouse name and deduct stock from store B.
	# Manager-class roles bypass via assert_pos_warehouse_access.
	from zevar_core.api.permissions import assert_pos_warehouse_access

	try:
		assert_pos_warehouse_access(warehouse)
	except frappe.PermissionError as exc:
		checkout_bouncer(str(exc), "permission_denied", details={"warehouse": warehouse})

	# Validate all items before creating invoice
	for item in items_list:
		item_code = item.get("item_code")
		if not item_code:
			checkout_bouncer(_("Each item must have an item_code."), "invoice_failed")
		if flt(item.get("qty", 0)) <= 0:
			checkout_bouncer(
				_("Item {0}: quantity must be greater than zero.").format(item_code), "invoice_failed"
			)
		if flt(item.get("rate", 0)) <= 0:
			checkout_bouncer(
				_("Item {0}: rate must be greater than zero.").format(item_code), "invoice_failed"
			)
		# Verify item exists in the system
		if not frappe.db.exists("Item", item_code):
			checkout_bouncer(_("Item '{0}' not found in the system.").format(item_code), "invoice_failed")

		# Validate Serial Number
		serial_no = item.get("serial_no")
		if serial_no:
			sn_doc = frappe.db.get_value(
				"Serial No", serial_no, ["status", "warehouse", "item_code"], as_dict=True
			)
			if not sn_doc:
				checkout_bouncer(
					_("Serial Number '{0}' not found in the system.").format(serial_no), "invoice_failed"
				)
			if sn_doc.item_code != item_code:
				checkout_bouncer(
					_("Serial Number '{0}' does not belong to Item '{1}'.").format(serial_no, item_code),
					"invoice_failed",
				)
			if sn_doc.status != "Active":
				checkout_bouncer(
					_(
						"Serial Number '{0}' is not active or available for sale (Status: {1})."
					).format(serial_no, sn_doc.status),
					"invoice_failed",
				)
			if not sn_doc.warehouse:
				checkout_bouncer(
					_("Serial Number '{0}' is not in any warehouse.").format(serial_no), "invoice_failed"
				)
			# A serial sitting in another store's safe must not be sellable
			# from this register — both for honest mistakes (cashier scans
			# the wrong tag) and for cross-store leakage attempts.
			try:
				assert_pos_warehouse_access(sn_doc.warehouse)
			except frappe.PermissionError:
				checkout_bouncer(
					_(
						"Serial Number '{0}' belongs to warehouse '{1}', which is outside your store."
					).format(serial_no, sn_doc.warehouse),
					"permission_denied",
					details={"serial_no": serial_no, "sn_warehouse": sn_doc.warehouse},
				)

		# Validate actual stock availability to handle edge cases where items
		# sell out while in the cart. Now safe because `warehouse` is
		# resolved and access-checked.
		is_stock_item, has_serial_no = frappe.db.get_value(
			"Item", item_code, ["is_stock_item", "has_serial_no"]
		)
		if is_stock_item and not has_serial_no and warehouse:
			# Use flt() on the DB result so None → 0.0 explicitly.
			# A missing Bin row means 0 stock — never allow the sale.
			actual_qty = flt(
				frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
			)
			requested_qty = flt(item.get("qty", 1))
			if actual_qty < requested_qty:
				checkout_bouncer(
					_(
						"Item '{0}' does not have enough stock in warehouse '{1}'. "
						"Available: {2}, Requested: {3}"
					).format(item_code, warehouse, actual_qty, requested_qty),
					"invoice_failed",
				)

	# Validate active POS session exists (managers bypass)
	active_session = frappe.db.get_value(
		"POS Opening Entry",
		filters={"user": frappe.session.user, "docstatus": 1, "status": "Open"},
		fieldname="name",
		order_by="creation desc",
	)
	if not active_session:
		manager_roles = {"Sales Manager", "Store Manager", "System Manager"}
		if not (manager_roles & set(frappe.get_roles())):
			checkout_bouncer(
				_("You must open a POS session before making sales. Please open a register first."),
				"permission_denied",
			)

	salesperson_data = []
	if salespersons:
		salesperson_data = frappe.parse_json(salespersons) if isinstance(salespersons, str) else salespersons
		# Validate each salesperson exists
		for sp in salesperson_data[:4]:
			emp = sp.get("salesperson") or sp.get("employee")
			if emp and not frappe.db.exists("Employee", emp):
				checkout_bouncer(_("Salesperson '{0}' not found.").format(emp), "invoice_failed")
		total_split = sum(flt(sp.get("split")) for sp in salesperson_data[:4])
		if salesperson_data and abs(total_split - 100) > 0.01:
			checkout_bouncer(
				_("Salesperson splits must total 100%. Current total: {0}%").format(total_split),
				"invoice_failed",
			)

	is_tax_exempt = str(tax_exempt).lower() in ["true", "1", "t", "y", "yes"]

	if not customer:
		customer = frappe.db.get_single_value("Global Defaults", "default_customer") or "Walk-In Customer"

	for pay in payments_list:
		mode = pay.get("mode_of_payment") or pay.get("mode", "")
		if mode and not frappe.db.exists("Mode of Payment", mode):
			from zevar_core.install import create_required_modes_of_payment

			create_required_modes_of_payment()
			if not frappe.db.exists("Mode of Payment", mode):
				checkout_bouncer(
					_("Payment mode '{0}' is not set up. Please run migrate or contact admin.").format(mode),
					"invoice_failed",
				)

	if not frappe.db.exists("Customer", customer):
		if customer == "Walk-In Customer":
			try:
				from zevar_core.api.customer import quick_create_customer

				quick_create_customer(customer_name="Walk-In Customer")
			except Exception:
				# If quick_create_customer fails, create basic customer directly
				cust = frappe.new_doc("Customer")
				cust.customer_name = "Walk-In Customer"
				cust.customer_type = "Individual"
				cust.insert(ignore_permissions=True)
		else:
			checkout_bouncer(_("Customer '{0}' not found.").format(customer), "invoice_failed")

	# ------------------------------------------------------------------
	# Payment validation (covers amounts, duplicates, totals, trade-in)
	# ------------------------------------------------------------------
	try:
		payments_list, total_trade_in_credit, computed_grand_total = _validate_payments(
			payments_list,
			trade_in_list,
			discount_amount,
			is_tax_exempt,
			warehouse,
			items_list,
		)
	except frappe.ValidationError as ve:
		checkout_bouncer(str(ve), "invoice_failed")

	# Validate gift card before creating invoice
	gc_payment_amount = 0
	for pay in payments_list:
		mode = pay.get("mode_of_payment") or pay.get("mode", "")
		if mode == "Gift Card":
			gc_payment_amount = flt(pay.get("amount"))
			break

	if gc_payment_amount > 0:
		if not gift_card_number:
			checkout_bouncer(
				_("Gift Card number is required when using Gift Card payment."), "invoice_failed"
			)
		if not frappe.db.exists("Gift Card", gift_card_number):
			checkout_bouncer(_("Gift Card '{0}' not found.").format(gift_card_number), "invoice_failed")

		from frappe.utils import getdate, today

		gc_doc = frappe.get_doc("Gift Card", gift_card_number)
		if gc_doc.status != "Active":
			checkout_bouncer(
				_("Gift Card is {0}. Cannot process payment.").format(gc_doc.status), "invoice_failed"
			)
		if gc_doc.expiry_date and getdate(gc_doc.expiry_date) < getdate(today()):
			checkout_bouncer(_("Gift Card has expired."), "invoice_failed")
		if gc_payment_amount > flt(gc_doc.balance):
			checkout_bouncer(
				_(
					"Gift Card balance insufficient. Available: {0}, Requested: {1}"
				).format(
					flt(gc_doc.balance), gc_payment_amount
				),
				"invoice_failed",
			)
		# Prevent gift card from being used more than once in the same invoice
		# (e.g., split into two Gift Card lines with the same number).
		if len([p for p in payments_list if (p.get("mode_of_payment") or p.get("mode", "")) == "Gift Card"]) > 1:
			checkout_bouncer(
				_("Gift Card payment can only be used once per invoice. Please combine the amounts."),
				"invoice_failed",
			)

	try:
		si = frappe.new_doc("Sales Invoice")
		si.is_pos = 1
		si.update_stock = 1
		si.customer = customer
		si.set_posting_time = 1

		if frappe.db.get_single_value("POS Settings", "invoice_type") == "Sales Invoice":
			si.is_created_using_pos = 1

		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		if company:
			si.company = company

		# Find POS profile and Tax Template from Store Location by Warehouse
		store_location = frappe.get_all(
			"Store Location",
			filters={"default_warehouse": warehouse, "is_active": 1},
			fields=["pos_profile", "tax_template", "county_tax_rate"],
			limit=1,
		)

		tax_template = None
		if store_location:
			store_info = store_location[0]
			if store_info.get("pos_profile"):
				si.pos_profile = store_info.get("pos_profile")
			tax_template = store_info.get("tax_template")

		if not si.pos_profile:
			active_pos_profile = frappe.db.get_value(
				"POS Opening Entry",
				filters={"user": frappe.session.user, "docstatus": 1, "status": "Open"},
				fieldname="pos_profile",
				order_by="creation desc",
			)
			if active_pos_profile:
				si.pos_profile = active_pos_profile

		for item in items_list:
			si.append(
				"items",
				{
					"item_code": item.get("item_code"),
					"qty": flt(item.get("qty", 1)),
					"rate": flt(item.get("rate")),
					"warehouse": warehouse,
					"allow_zero_valuation_rate": 1,
					"serial_no": item.get("serial_no"),
				},
			)

		if flt(discount_amount) > 0:
			si.apply_discount_on = "Grand Total"
			si.discount_amount = flt(discount_amount)

		has_no_tax_field = hasattr(si, "custom_no_tax_override")
		has_transaction_stream = hasattr(si, "custom_transaction_stream")
		has_tax_override_fields = hasattr(si, "custom_tax_override_approved_by")

		if is_tax_exempt:
			# Validate customer tax exemption status
			customer_doc = frappe.db.get_value(
				"Customer",
				customer,
				["exempt_from_sales_tax", "customer_name"],
				as_dict=True,
			)
			customer_is_exempt = bool(customer_doc and customer_doc.get("exempt_from_sales_tax"))

			if not customer_is_exempt:
				# Non-exempt customer requires manager override
				if not override_reference:
					checkout_bouncer(
						_(
							"Tax exemption requires manager approval. Customer '{0}' is not marked as tax exempt."
						).format(customer),
						"invoice_failed",
					)
				_validate_tax_override(override_reference, customer)

			si.taxes = []
			if has_no_tax_field:
				si.custom_no_tax_override = 1
			if has_tax_override_fields and not customer_is_exempt and override_reference:
				override_doc = frappe.get_doc("POS Manager Override", override_reference)
				si.custom_tax_override_approved_by = override_doc.approved_by or frappe.session.user
				si.custom_tax_override_reason = override_doc.reason or ""
		elif tax_template:
			si.taxes_and_charges = tax_template
			if has_no_tax_field:
				si.custom_no_tax_override = 0
		else:
			si.taxes = []
			si.taxes_and_charges = ""
			if has_no_tax_field:
				si.custom_no_tax_override = 1

		if has_transaction_stream and not si.get("custom_transaction_stream"):
			si.custom_transaction_stream = "Jewelry Sale"

		has_salesperson_splits = hasattr(si, "custom_salesperson_splits")
		has_salesperson_fields = hasattr(si, "custom_salesperson_1")
		for i, sp in enumerate(salesperson_data):
			emp = sp.get("salesperson") or sp.get("employee")
			split = flt(sp.get("split"))
			if has_salesperson_splits:
				si.append(
					"custom_salesperson_splits",
					{
						"employee": emp,
						"split_percent": split,
					},
				)
			if has_salesperson_fields:
				if i == 0:
					si.custom_salesperson_1 = emp
					si.custom_salesperson_1_split = split
				elif i == 1:
					si.custom_salesperson_2 = emp
					si.custom_salesperson_2_split = split
				elif i == 2:
					si.custom_salesperson_3 = emp
					si.custom_salesperson_3_split = split
				elif i == 3:
					si.custom_salesperson_4 = emp
					si.custom_salesperson_4_split = split

		if layaway_reference and hasattr(si, "custom_layaway_reference"):
			si.custom_layaway_reference = layaway_reference

		has_trade_ins = hasattr(si, "custom_trade_ins")
		for ti in trade_in_list:
			trade_in_item = {
				"trade_in_value": flt(ti.get("trade_in_value")),
				"new_item_value": flt(ti.get("new_item_value")),
				"manager_override": ti.get("manager_override"),
				"override_reason": ti.get("override_reason"),
			}
			if not ti.get("new_item_code") and items_list:
				trade_in_item["new_item_code"] = items_list[0].get("item_code")

			if ti.get("original_item_code"):
				trade_in_item["original_item_code"] = ti.get("original_item_code")
			elif ti.get("description"):
				if not trade_in_item.get("override_reason"):
					trade_in_item["override_reason"] = f"Trade-In Item: {ti.get('description')}"

			if has_trade_ins:
				si.append("custom_trade_ins", trade_in_item)

		# payments_list already includes Trade-In (if any) from _validate_payments.
		for pay in payments_list:
			si.append(
				"payments",
				{
					"mode_of_payment": pay.get("mode_of_payment") or pay.get("mode"),
					"amount": flt(pay.get("amount")),
				},
			)

		si.insert(ignore_permissions=True)

		# Deduct gift card balance before invoice submission for atomicity (Issue #12)
		if gc_payment_amount > 0 and gift_card_number:
			gc_doc = frappe.get_doc("Gift Card", gift_card_number)
			gc_doc.balance = flt(gc_doc.balance) - gc_payment_amount
			if gc_doc.balance <= 0:
				gc_doc.status = "Used"
			gc_doc.save(ignore_permissions=True)

		si.submit()

		from zevar_core.api.audit_log import log_event_safely
		from zevar_core.api.gift_card import log_gift_card_used

		log_event_safely(
			event_type="invoice_created",
			details={
				"invoice_name": si.name,
				"customer": si.customer,
				"grand_total": flt(si.grand_total),
				"outstanding_amount": flt(si.outstanding_amount),
				"item_count": len(si.items),
				"warehouse": warehouse,
				"payment_modes": [
					{
						"mode_of_payment": payment.mode_of_payment,
						"amount": flt(payment.amount),
					}
					for payment in si.payments
				],
				"layaway_reference": layaway_reference,
				"gift_card_number": gift_card_number,
			},
			reference_document=si.name,
			reference_type="Sales Invoice",
		)

		# Notify managers about new sale
		try:
			managers = frappe.get_all(
				"Has Role",
				filters={"role": ["in", ["Sales Manager", "Store Manager"]], "parenttype": "User"},
				fields=["parent"],
			)
			sale_event = {
				"event_type": "invoice_created",
				"invoice_name": si.name,
				"customer": si.customer,
				"grand_total": flt(si.grand_total),
				"salesperson": frappe.session.user,
				"timestamp": str(frappe.utils.now_datetime()),
			}
			for mgr in managers:
				frappe.publish_realtime("pos_sale_event", sale_event, user=mgr.parent)
		except Exception:
			frappe.log_error("POS Sale Notification Failed", frappe.get_traceback())

		# Broadcast stock update to all POS terminals for real-time catalog refresh
		try:
			affected_items = [item.item_code for item in si.items]
			frappe.publish_realtime(
				"stock_update",
				{
					"item_codes": affected_items,
					"warehouse": warehouse,
					"invoice": si.name,
					"timestamp": str(frappe.utils.now_datetime()),
				},
				after_commit=True,
			)
		except Exception:
			pass  # Non-critical — catalog will refresh on next poll

		if gc_payment_amount > 0 and gift_card_number:
			log_gift_card_used(gc_doc, gc_payment_amount, source_reference=si.name)

		return {
			"success": True,
			"invoice_name": si.name,
			"status": si.status,
			"grand_total": si.grand_total,
			"outstanding_amount": si.outstanding_amount,
			"message": f"Successfully created invoice {si.name}",
		}

	except frappe.ValidationError as e:
		frappe.db.rollback()
		frappe.log_error("POS Invoice Validation Error", frappe.get_traceback())
		# Never expose raw internal messages to cashiers / employees.
		friendly = _friendly_payment_error(str(e))
		frappe.throw(friendly, frappe.ValidationError)
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("POS Invoice Creation Failed", frappe.get_traceback())
		# Catch-all: hide technical details from end users.
		friendly = _friendly_payment_error(str(e))
		frappe.throw(friendly)


@frappe.whitelist()
def get_pos_settings(warehouse: str | None = None):
	"""
	Fetch POS settings including tax rates and payment modes.

	Args:
	    warehouse: Warehouse name to determine tax rate by location

	Returns:
	    POS settings dictionary
	"""
	# Fallback to active store location warehouse if not provided
	if not warehouse:
		store_loc_wh = frappe.db.get_value("Store Location", {"is_active": 1}, "default_warehouse")
		if store_loc_wh:
			warehouse = store_loc_wh
		else:
			# Try to get default warehouse from company
			company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
				"Global Defaults", "default_company"
			)
			if company:
				warehouse = frappe.db.get_value("Company", company, "default_warehouse")

	# Determine tax rate: Store Location > hardcoded fallback
	tax_rate = 0.0
	if warehouse:
		store_loc = frappe.db.get_value(
			"Store Location",
			{"default_warehouse": warehouse, "is_active": 1},
			["county_tax_rate", "tax_template"],
			as_dict=True,
		)
		if store_loc and store_loc.county_tax_rate:
			tax_rate = flt(store_loc.county_tax_rate)
		else:
			warehouse_lower = warehouse.lower()
			for location, rate in DEFAULT_TAX_RATES.items():
				if location.lower() in warehouse_lower:
					tax_rate = rate
					break

	# Default company
	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)

	return {"tax_rate": tax_rate, "currency": "USD", "company": company, "payment_modes": PAYMENT_MODES}


@frappe.whitelist()
def calculate_invoice_totals(
	items: str, tax_exempt: bool = False, discount_amount: float = 0, warehouse: str | None = None
):
	"""
	Calculate invoice totals.

	Args:
	    items: JSON string of items [{item_code, qty, rate}]
	    tax_exempt: Whether customer is tax exempt
	    discount_amount: Discount amount to apply
	    warehouse: Warehouse for tax rate determination

	Returns:
	    Totals dictionary
	"""
	items_list = frappe.parse_json(items) if isinstance(items, str) else items

	# Calculate subtotal
	subtotal = sum(float(item.get("rate", 0)) * float(item.get("qty", 1)) for item in items_list)

	# Apply discount
	discount = max(0.0, float(discount_amount))
	subtotal_after_discount = max(0.0, subtotal - discount)

	# Calculate tax
	tax = 0.0
	if not tax_exempt:
		settings = get_pos_settings(warehouse)
		tax_rate = settings.get("tax_rate", 0)
		tax = (subtotal_after_discount * tax_rate) / 100

	# Grand total
	grand_total = subtotal_after_discount + tax

	return {
		"subtotal": subtotal,
		"discount": discount,
		"subtotal_after_discount": subtotal_after_discount,
		"tax": tax,
		"grand_total": grand_total,
	}


# ---------------------------------------------------------------------------
# Tax Exemption Override Helpers & Endpoints
# ---------------------------------------------------------------------------


def _validate_tax_override(override_name: str, customer: str) -> None:
	"""Validate that a POS Manager Override is approved for tax exemption."""
	if not frappe.db.exists("POS Manager Override", override_name):
		frappe.throw(
			_("Override reference '{0}' not found.").format(override_name),
			frappe.ValidationError,
		)

	override = frappe.get_doc("POS Manager Override", override_name)

	if override.status != "Approved":
		frappe.throw(
			_("Tax exemption override is {0}. Only approved overrides are accepted.").format(override.status),
			frappe.ValidationError,
		)

	if override.action != "tax_exemption":
		frappe.throw(
			_("Override is not for tax exemption."),
			frappe.ValidationError,
		)


@frappe.whitelist(methods=["POST"])
def request_tax_exemption_override(
	customer: str,
	reason: str,
	invoice_data: str | None = None,
) -> dict:
	"""
	Request a manager override for tax exemption.

	Creates a POS Manager Override document in Pending status.
	"""
	allowed_roles = {
		"Sales User",
		"Sales Manager",
		"Store Manager",
		"POS Manager",
		"Employee",
		"Employee Self Service",
		"System Manager",
	}
	if not (allowed_roles & set(frappe.get_roles())):
		frappe.throw(_("You don't have permission to request overrides."), frappe.PermissionError)

	if not customer:
		frappe.throw(_("Customer is required."))

	if not reason or not reason.strip():
		frappe.throw(_("A reason is required for tax exemption override."))

	override = frappe.new_doc("POS Manager Override")
	override.requested_by = frappe.session.user
	override.action = "tax_exemption"
	override.reason = reason.strip()
	override.status = "Pending"
	override.reference_type = "Customer"
	override.reference_document = customer
	override.notes = invoice_data or ""
	override.insert(ignore_permissions=True)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="manager_override_requested",
		details={
			"override_name": override.name,
			"customer": customer,
			"reason": reason.strip(),
			"action": "tax_exemption",
		},
	)

	return {
		"success": True,
		"override_name": override.name,
		"status": "Pending",
		"message": _("Tax exemption override requested. Waiting for manager approval."),
	}


@frappe.whitelist(methods=["POST"])
def approve_tax_exemption_override(override_name: str) -> dict:
	"""Approve a tax exemption override. Manager only."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	if not override_name or not frappe.db.exists("POS Manager Override", override_name):
		frappe.throw(_("Override '{0}' not found.").format(override_name or ""))

	override = frappe.get_doc("POS Manager Override", override_name)

	if override.action != "tax_exemption":
		frappe.throw(_("This override is not for tax exemption."))

	if override.status != "Pending":
		frappe.throw(_("Override is already {0}.").format(override.status))

	override.status = "Approved"
	override.approved_by = frappe.session.user
	override.approval_time = frappe.utils.now_datetime()
	override.flags.ignore_permissions = True
	override.save(ignore_permissions=True)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="tax_exemption_approved",
		details={
			"override_name": override.name,
			"customer": override.reference_document,
			"approved_by": frappe.session.user,
		},
	)

	return {
		"success": True,
		"override_name": override.name,
		"status": "Approved",
		"message": _("Tax exemption override approved."),
	}


@frappe.whitelist(methods=["POST"])
def reject_tax_exemption_override(override_name: str, notes: str | None = None) -> dict:
	"""Reject a tax exemption override. Manager only."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	if not override_name or not frappe.db.exists("POS Manager Override", override_name):
		frappe.throw(_("Override '{0}' not found.").format(override_name or ""))

	override = frappe.get_doc("POS Manager Override", override_name)

	if override.action != "tax_exemption":
		frappe.throw(_("This override is not for tax exemption."))

	if override.status != "Pending":
		frappe.throw(_("Override is already {0}.").format(override.status))

	override.status = "Rejected"
	override.approved_by = frappe.session.user
	override.approval_time = frappe.utils.now_datetime()
	if notes:
		override.notes = notes
	override.flags.ignore_permissions = True
	override.save(ignore_permissions=True)

	from zevar_core.api.audit_log import log_event_safely

	log_event_safely(
		event_type="tax_exemption_denied",
		details={
			"override_name": override.name,
			"customer": override.reference_document,
			"rejected_by": frappe.session.user,
		},
	)

	return {
		"success": True,
		"override_name": override.name,
		"status": "Rejected",
		"message": _("Tax exemption override rejected."),
	}


@frappe.whitelist()
def get_pending_overrides() -> dict:
	"""Get all pending tax exemption overrides. Manager only."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	overrides = frappe.get_all(
		"POS Manager Override",
		filters={"action": "tax_exemption", "status": "Pending"},
		fields=["name", "requested_by", "reason", "request_time", "reference_document", "notes"],
		order_by="request_time asc",
	)

	# Enrich with requester names
	for o in overrides:
		o["requester_name"] = frappe.db.get_value("User", o.requested_by, "full_name") or o.requested_by
		o["customer_name"] = (
			frappe.db.get_value("Customer", o.reference_document, "customer_name") or o.reference_document
		)

	return {
		"overrides": overrides,
		"count": len(overrides),
	}

@frappe.whitelist(methods=["GET", "POST"])
def validate_cart_items(item_codes: str) -> dict:
	"""
	Takes a list of item_codes (JSON string), and returns their current state
	(price, active, name) so the frontend cart can update prices and remove inactive items.
	"""
	try:
		items = frappe.parse_json(item_codes)
	except Exception:
		items = []
	
	if not items:
		return {}

	results = {}
	for item_code in items:
		item = frappe.db.get_value("Item", item_code, ["item_name", "standard_rate", "disabled"], as_dict=True)
		if item:
			results[item_code] = {
				"item_name": item.item_name,
				"rate": flt(item.standard_rate),
				"disabled": item.disabled
			}
		else:
			results[item_code] = None
	return results



# ---------------------------------------------------------------------------
# Pre-submit cart validation (Fix #3)
# ---------------------------------------------------------------------------
#
# These helpers and the validate_pos_cart endpoint give the frontend a single
# call to make right before "Submit" so the cashier can be told *exactly* why
# a sale would fail (sold out, serial inactive, foreign warehouse, price
# changed, etc.) without having to attempt and roll back a full Sales Invoice.
#
# Issue types are stable strings so the UI can branch on them:
#
#   item_missing            — item_code does not exist in the system
#   item_disabled           — Item.disabled = 1
#   qty_invalid             — qty <= 0 or non-numeric
#   rate_invalid            — rate <= 0 or non-numeric
#   out_of_stock            — Bin.actual_qty < requested qty (non-serialized)
#   serial_not_found        — Serial No record missing
#   serial_wrong_item       — serial belongs to a different item
#   serial_inactive         — Serial No.status != "Active"
#   serial_no_warehouse     — Serial No.warehouse is empty
#   serial_wrong_warehouse  — serial sits in a foreign / inaccessible warehouse
#   price_drift             — current canonical price differs from cart rate
#                             (informational only; submission is not blocked)
#
# `blocking` flag on each issue is True for everything except price_drift, so
# callers can decide whether to refuse submission or just warn the user.


# Tolerance below which a price difference is considered floating-point noise
# rather than a real price change. 0.5 cents.
_PRICE_DRIFT_TOLERANCE_USD = 0.005


def _make_issue(item_code: str, type_: str, message: str, *, blocking: bool = True, **details) -> dict:
	"""Build a structured issue dict. Keep the schema stable for the UI."""
	issue = {
		"item_code": item_code,
		"type": type_,
		"message": message,
		"blocking": blocking,
	}
	if details:
		issue["details"] = details
	return issue


def _check_cart_item_availability(item_dict: dict, warehouse: str | None) -> list[dict]:
	"""Return a list of blocking-availability issues for one cart line.

	Covers item existence, qty/rate sanity, stock availability for non-
	serialized items, and serial number state for serialized items. Cross-
	store serial leakage is caught via assert_pos_warehouse_access from
	Fix #2.
	"""
	from zevar_core.api.permissions import assert_pos_warehouse_access

	issues: list[dict] = []
	item_code = item_dict.get("item_code")

	if not item_code:
		return [_make_issue("", "item_missing", _("Each cart line must have an item_code."))]

	qty = flt(item_dict.get("qty", 0))
	rate = flt(item_dict.get("rate", 0))

	if qty <= 0:
		issues.append(
			_make_issue(item_code, "qty_invalid", _("Quantity must be greater than zero."), qty=qty)
		)
	if rate <= 0:
		issues.append(
			_make_issue(item_code, "rate_invalid", _("Rate must be greater than zero."), rate=rate)
		)

	if not frappe.db.exists("Item", item_code):
		issues.append(
			_make_issue(item_code, "item_missing", _("Item '{0}' not found.").format(item_code))
		)
		return issues

	item_meta = frappe.db.get_value(
		"Item", item_code, ["disabled", "is_stock_item", "has_serial_no"], as_dict=True
	)
	if item_meta and item_meta.disabled:
		issues.append(
			_make_issue(item_code, "item_disabled", _("Item '{0}' is disabled.").format(item_code))
		)
		return issues

	serial_no = item_dict.get("serial_no")
	if serial_no:
		sn_doc = frappe.db.get_value(
			"Serial No", serial_no, ["status", "warehouse", "item_code"], as_dict=True
		)
		if not sn_doc:
			issues.append(
				_make_issue(
					item_code,
					"serial_not_found",
					_("Serial Number '{0}' not found.").format(serial_no),
					serial_no=serial_no,
				)
			)
			return issues
		if sn_doc.item_code != item_code:
			issues.append(
				_make_issue(
					item_code,
					"serial_wrong_item",
					_(
						"Serial Number '{0}' belongs to item '{1}', not '{2}'."
					).format(serial_no, sn_doc.item_code, item_code),
					serial_no=serial_no,
					expected_item=item_code,
					actual_item=sn_doc.item_code,
				)
			)
		if sn_doc.status != "Active":
			issues.append(
				_make_issue(
					item_code,
					"serial_inactive",
					_(
						"Serial Number '{0}' is no longer available (status: {1})."
					).format(serial_no, sn_doc.status),
					serial_no=serial_no,
					serial_status=sn_doc.status,
				)
			)
		if not sn_doc.warehouse:
			issues.append(
				_make_issue(
					item_code,
					"serial_no_warehouse",
					_("Serial Number '{0}' is not in any warehouse.").format(serial_no),
					serial_no=serial_no,
				)
			)
		else:
			# Cross-store guard from Fix #2.
			try:
				assert_pos_warehouse_access(sn_doc.warehouse)
			except frappe.PermissionError:
				issues.append(
					_make_issue(
						item_code,
						"serial_wrong_warehouse",
						_(
							"Serial Number '{0}' is in warehouse '{1}', which is outside your store."
						).format(serial_no, sn_doc.warehouse),
						serial_no=serial_no,
						sn_warehouse=sn_doc.warehouse,
					)
				)
		# Serial-numbered: no Bin qty check needed.
		return issues

	# Non-serialized stock-item flow: confirm Bin has enough on hand.
	if item_meta and item_meta.is_stock_item and warehouse:
		actual_qty = (
			flt(
				frappe.db.get_value(
					"Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty"
				)
			)
			or 0
		)
		if actual_qty < qty:
			issues.append(
				_make_issue(
					item_code,
					"out_of_stock",
					_(
						"Item '{0}' has {1} available in warehouse '{2}' but the cart requested {3}."
					).format(item_code, actual_qty, warehouse, qty),
					available=actual_qty,
					requested=qty,
					warehouse=warehouse,
				)
			)

	return issues


def _check_cart_item_price_drift(item_dict: dict) -> list[dict]:
	"""Return a `price_drift` issue if current canonical price differs from cart rate.

	Non-blocking — the cashier may have legitimately applied a discount or a
	manager override. The frontend uses this to surface a "price changed"
	warning so the customer/cashier can confirm.
	"""
	item_code = item_dict.get("item_code")
	cart_rate = flt(item_dict.get("rate", 0))
	if not item_code or cart_rate <= 0:
		return []

	try:
		from zevar_core.api.pricing import get_item_price

		price_data = get_item_price(item_code) or {}
		current_price = flt(price_data.get("final_price") or 0)
	except Exception:
		# Pricing failures must not block availability checks.
		return []

	if current_price <= 0:
		return []

	if abs(current_price - cart_rate) <= _PRICE_DRIFT_TOLERANCE_USD:
		return []

	return [
		_make_issue(
			item_code,
			"price_drift",
			_(
				"Item '{0}' price changed: cart had {1}, current price is {2}."
			).format(item_code, cart_rate, current_price),
			blocking=False,
			cart_rate=cart_rate,
			current_price=current_price,
		)
	]


@frappe.whitelist(methods=["POST"])
def validate_pos_cart(items: str, warehouse: str | None = None) -> dict:
	"""Pre-submit cart gate. Returns structured issues for every cart line.

	Args:
	    items: JSON string of cart lines, each at minimum
	           {item_code, qty, rate, serial_no?}.
	    warehouse: Warehouse the sale will be booked from. Required for
	               non-serialized stock checks; optional for serialized-only
	               carts.

	Returns:
	    {
	        "ok": bool,           # True iff there are no blocking issues
	        "blocking": bool,     # convenience: any issue with blocking=True
	        "issues": [ ... ],    # list of issue dicts, see module docstring
	    }
	"""
	from zevar_core.api.permissions import assert_pos_warehouse_access

	try:
		items_list = frappe.parse_json(items) if isinstance(items, str) else (items or [])
	except Exception:
		items_list = []

	# A foreign warehouse should fail before any item walk so we don't leak
	# Bin counts. Non-serialized lines without a warehouse yield no stock
	# issue (frontend may be checking serial-only carts pre-checkout).
	if warehouse:
		assert_pos_warehouse_access(warehouse)

	issues: list[dict] = []
	for line in items_list:
		issues.extend(_check_cart_item_availability(line, warehouse))
		issues.extend(_check_cart_item_price_drift(line))

	blocking = any(i.get("blocking", True) for i in issues)
	return {"ok": not blocking, "blocking": blocking, "issues": issues}


# ──────────────────────────────────────────────────────────────────────────────
# Held (parked) carts
# ──────────────────────────────────────────────────────────────────────────────

HELD_CARTS_KEY = "pos_held_carts:{user}"


@frappe.whitelist(methods=["POST"])
def hold_cart(
	items: str,
	customer: str | None = None,
	customer_name: str | None = None,
	note: str | None = None,
	warehouse: str | None = None,
) -> dict:
	"""
	Park the current cart so it can be recalled later.

	Stores a snapshot in frappe.cache keyed by user. Each user can hold
	up to 10 carts at a time.

	Args:
		items: JSON-encoded list of cart items
		customer: Customer docname (optional)
		customer_name: Display name for the customer
		note: Short label for the held cart (e.g. "Mrs. Johnson - ring resize")
		warehouse: Current warehouse context
	"""
	from zevar_core.api.permissions import assert_pos_warehouse_access, check_permission

	# Same RBAC envelope as create_pos_invoice — Sales User and up.
	check_permission("pos_access")

	# Multi-store enforcement (Fix #2 contract): a cashier in store A
	# cannot park a cart against store B's warehouse. Skipped when no
	# warehouse is supplied (held carts are warehouse-agnostic).
	if warehouse:
		assert_pos_warehouse_access(warehouse)

	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	if not items_list:
		frappe.throw(_("Cannot hold an empty cart."))

	cart_id = frappe.generate_hash(length=8)
	held_cart = {
		"id": cart_id,
		"items": items_list,
		"customer": customer,
		"customer_name": customer_name or customer,
		"note": note or "",
		"warehouse": warehouse,
		"user": frappe.session.user,
		"held_at": str(frappe.utils.now_datetime()),
		"item_count": len(items_list),
		"total": sum(flt(i.get("amount", 0)) * flt(i.get("qty", 1)) for i in items_list),
	}

	cache_key = HELD_CARTS_KEY.format(user=frappe.session.user)
	existing = frappe.cache().get_value(cache_key) or []

	if len(existing) >= 10:
		frappe.throw(_("Maximum 10 held carts allowed. Please recall or discard one first."))

	existing.append(held_cart)
	frappe.cache().set_value(cache_key, existing, expires_in_sec=86400)  # 24h TTL

	return {"success": True, "cart_id": cart_id, "held_count": len(existing)}


@frappe.whitelist()
def get_held_carts() -> dict:
	"""Return all held carts for the current user."""
	cache_key = HELD_CARTS_KEY.format(user=frappe.session.user)
	carts = frappe.cache().get_value(cache_key) or []
	return {"carts": carts, "count": len(carts)}


@frappe.whitelist(methods=["POST"])
def recall_cart(cart_id: str) -> dict:
	"""
	Retrieve a held cart and remove it from the held list.

	Args:
		cart_id: The unique ID assigned when the cart was held
	"""
	cache_key = HELD_CARTS_KEY.format(user=frappe.session.user)
	existing = frappe.cache().get_value(cache_key) or []

	target = None
	remaining = []
	for c in existing:
		if c.get("id") == cart_id:
			target = c
		else:
			remaining.append(c)

	if not target:
		frappe.throw(_("Held cart not found or already recalled."))

	frappe.cache().set_value(cache_key, remaining, expires_in_sec=86400)
	return {"success": True, "cart": target}


@frappe.whitelist(methods=["POST"])
def discard_held_cart(cart_id: str) -> dict:
	"""Remove a held cart without recalling it."""
	cache_key = HELD_CARTS_KEY.format(user=frappe.session.user)
	existing = frappe.cache().get_value(cache_key) or []
	remaining = [c for c in existing if c.get("id") != cart_id]
	frappe.cache().set_value(cache_key, remaining, expires_in_sec=86400)
	return {"success": True, "remaining": len(remaining)}
