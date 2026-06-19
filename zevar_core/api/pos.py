"""
POS API - Invoice creation and settings
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.constants import DEFAULT_TAX_RATES, PAYMENT_MODES


@frappe.whitelist(methods=["POST"])
def initiate_online_checkout(reference_doctype: str, reference_name: str, gateway: str) -> dict:
	"""
	Generates an online checkout URL (e.g., Stripe, Square) for a given document.
	"""
	frappe.only_for(["Sales User", "Sales Manager", "Store Manager", "System Manager"])

	doc = frappe.get_doc(reference_doctype, reference_name)
	
	amount = doc.outstanding_amount if hasattr(doc, "outstanding_amount") else doc.grand_total
	if amount <= 0:
		frappe.throw(_("No outstanding amount to pay."))

	payment_gateway = frappe.db.get_value("Payment Gateway", {"gateway_name": gateway})
	if not payment_gateway:
		frappe.throw(_("Payment Gateway '{0}' not found.").format(gateway))

	pr = frappe.new_doc("Payment Request")
	pr.reference_doctype = reference_doctype
	pr.reference_name = reference_name
	pr.payment_gateway_account = gateway
	pr.payment_request_type = "Inward"
	pr.message = "Payment for POS Order"
	pr.insert(ignore_permissions=True)
	pr.submit()

	# The get_payment_url is natively handled by frappe/payments based on gateway controller
	payment_url = pr.get_payment_url()

	return {
		"success": True,
		"payment_request_name": pr.name,
		"checkout_url": payment_url
	}

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
	idempotency_key: str | None = None,
	irs_8300_details: str | None = None,
	online_checkout_gateway: str | None = None,
) -> dict:
	frappe.only_for(
		["Sales User", "Sales Manager", "Store Manager", "POS Manager", "Employee", "System Manager"]
	)

	# Handle idempotency to prevent duplicate charges
	if idempotency_key:
		existing = frappe.db.get_value(
			"Idempotency Record", {"name": idempotency_key}, ["sales_invoice", "status"], as_dict=True
		)
		if existing and existing.status == "Completed":
			return {
				"success": True,
				"invoice_name": existing.sales_invoice,
				"message": f"Duplicate request — invoice {existing.sales_invoice} already created",
			}

	try:
		return _create_pos_invoice_internal(
			items,
			payments,
			customer,
			warehouse,
			discount_amount,
			tax_exempt,
			salespersons,
			layaway_reference,
			trade_ins,
			gift_card_number,
			override_reference,
			idempotency_key,
			irs_8300_details,
			online_checkout_gateway,
		)
	except Exception:
		frappe.log_error(title="POS Invoice Sync Failed", message=frappe.get_traceback())
		raise


def _create_pos_invoice_internal(
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
	idempotency_key: str | None = None,
	irs_8300_details: str | None = None,
	online_checkout_gateway: str | None = None,
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

	def checkout_bouncer(msg: str, event_type: str = "invoice_failed"):
		frappe.log_error(title="POS Invoice Validation Error", message=f"{msg}\n\n{frappe.get_traceback()}")
		frappe.db.commit()
		from zevar_core.api.audit_log import log_event_safely

		try:
			log_event_safely(
				event_type=event_type,
				details={"error": msg},
				reference_document="Offline Transaction",
			)
		except Exception:
			pass
		frappe.throw(
			msg, frappe.ValidationError if "permission" not in event_type else frappe.PermissionError
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

	if not payments_list and not online_checkout_gateway:
		checkout_bouncer(_("At least one payment mode is required."), "invoice_failed")

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

	# Fall back to a valid warehouse if the provided one doesn't exist
	if not warehouse or not frappe.db.exists("Warehouse", warehouse):
		fallback_wh = None
		# 1. Try active POS Opening Entry profile warehouse
		active_pos = frappe.db.get_value(
			"POS Opening Entry",
			filters={"user": frappe.session.user, "docstatus": 1, "status": "Open"},
			fieldname="pos_profile",
			order_by="creation desc",
		)
		if active_pos:
			fallback_wh = frappe.db.get_value("POS Profile", active_pos, "warehouse")

		# 2. Try global default warehouse
		if not fallback_wh or not frappe.db.exists("Warehouse", fallback_wh):
			fallback_wh = frappe.db.get_single_value("Global Defaults", "default_warehouse")

		# 3. Try first available warehouse for the company
		if not fallback_wh or not frappe.db.exists("Warehouse", fallback_wh):
			company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
				"Global Defaults", "default_company"
			)
			if company:
				fallback_wh = frappe.db.get_value(
					"Warehouse",
					{"company": company, "is_group": 0, "disabled": 0},
					"name",
				)

		if fallback_wh and frappe.db.exists("Warehouse", fallback_wh):
			warehouse = fallback_wh

	if not warehouse:
		checkout_bouncer(
			_("No store selected. Please select a store location from the dropdown before making a sale."),
			"invoice_failed",
		)

	if not frappe.db.exists("Warehouse", warehouse):
		checkout_bouncer(
			_("Warehouse '{0}' not found. Please ensure a valid warehouse is configured.").format(warehouse),
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
				_("Gift Card balance insufficient. Available: {0}, Requested: {1}").format(
					flt(gc_doc.balance), gc_payment_amount
				),
				"invoice_failed",
			)

	# Validate stock availability before creating invoice
	for item in items_list:
		item_code = item.get("item_code")
		qty_needed = flt(item.get("qty", 1))
		serial_no = item.get("serial_no")

		# For serial-numbered items, verify the serial exists in this warehouse
		if serial_no:
			for sn in serial_no.split("\n"):
				sn = sn.strip()
				if not sn:
					continue
				sn_warehouse = frappe.db.get_value("Serial No", sn, "warehouse")
				if sn_warehouse != warehouse:
					checkout_bouncer(
						_("Serial No {0} is not available in {1}. It is in {2}.").format(
							sn, warehouse, sn_warehouse or "no warehouse"
						),
						"invoice_failed",
					)
		else:
			# For non-serial items, check Bin qty
			actual_qty = flt(
				frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
			)
			if actual_qty < qty_needed:
				allow_negative = frappe.db.get_single_value("Stock Settings", "allow_negative_stock")
				if not allow_negative:
					checkout_bouncer(
						_("Insufficient stock for {0} in {1}. Available: {2}, Required: {3}").format(
							item_code, warehouse, actual_qty, qty_needed
						),
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
			if store_info.get("pos_profile") and frappe.db.exists("POS Profile", store_info.get("pos_profile")):
				si.pos_profile = store_info.get("pos_profile")
			tax_template = store_info.get("tax_template")

		if not si.pos_profile:
			active_pos_profile = frappe.db.get_value(
				"POS Opening Entry",
				filters={"user": frappe.session.user, "docstatus": 1, "status": "Open"},
				fieldname="pos_profile",
				order_by="creation desc",
			)
			if active_pos_profile and frappe.db.exists("POS Profile", active_pos_profile):
				si.pos_profile = active_pos_profile

		for item in items_list:
			item_code = item.get("item_code")
			item_doc = frappe.get_cached_doc("Item", item_code)
			si.append(
				"items",
				{
					"item_code": item_code,
					"qty": flt(item.get("qty", 1)),
					"rate": flt(item.get("rate")),
					"warehouse": warehouse,
					"uom": item_doc.stock_uom,
					"conversion_factor": 1.0,
					"stock_uom": item_doc.stock_uom,
					"serial_no": item.get("serial_no") or "",
					"allow_zero_valuation_rate": 1,
				},
			)

		if flt(discount_amount) > 0:
			si.apply_discount_on = "Grand Total"
			si.discount_amount = flt(discount_amount)

			# Validate discount against active Discount Rules
			if not override_reference:
				from zevar_core.api.discount import validate_discount

				subtotal_val = sum(flt(item.get("rate", 0)) * flt(item.get("qty", 1)) for item in items_list)
				discount_pct = (
					(flt(discount_amount) / flt(subtotal_val) * 100) if flt(subtotal_val) > 0 else 0
				)
				result = validate_discount(
					discount_amount=flt(discount_amount),
					discount_pct=discount_pct,
					subtotal=subtotal_val,
					customer=customer,
				)
				if not result["valid"]:
					frappe.throw(_(result["reason"]))

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

		# Add trade-in credit as a payment entry
		total_trade_in_credit = (
			sum(flt(ti.get("trade_in_value")) for ti in trade_in_list) if trade_in_list else 0
		)

		si.set_missing_values()
		si.calculate_taxes_and_totals()

		# set_missing_values() overwrites item warehouses with POS Profile default
		# and replaces payments with POS Profile defaults (all 0.0).
		# We must restore the correct warehouse and set actual payments AFTER that call.
		for item in si.items:
			item.warehouse = warehouse

		si.payments = []
		if total_trade_in_credit > 0:
			si.append(
				"payments",
				{
					"mode_of_payment": "Trade-In",
					"amount": flt(total_trade_in_credit),
				},
			)

		for pay in payments_list:
			si.append(
				"payments",
				{
					"mode_of_payment": pay.get("mode_of_payment") or pay.get("mode"),
					"amount": flt(pay.get("amount")),
				},
			)

		si.set_account_for_mode_of_payment()
		si.calculate_taxes_and_totals()

		# Auto-correct small rounding differences (e.g., tax rounding mismatches)
		total_payments = sum(flt(p.amount) for p in si.payments)
		difference = flt(si.grand_total) - total_payments

		if si.payments and abs(difference) <= 2.0 and abs(difference) > 0:
			si.payments[-1].amount = flt(si.payments[-1].amount) + difference
			si.calculate_taxes_and_totals()

		si.insert(ignore_permissions=True)

		# Diagnostic: log item state before submit to track stock deduction
		for _diag_item in si.items:
			if flt(_diag_item.stock_qty) != flt(_diag_item.qty):
				frappe.log_error(
					title=f"POS Stock Diagnostic: {si.name}",
					message=(
						f"Item {_diag_item.item_code}: qty={_diag_item.qty}, "
						f"stock_qty={_diag_item.stock_qty}, "
						f"conversion_factor={_diag_item.conversion_factor}, "
						f"uom={_diag_item.uom}, stock_uom={_diag_item.stock_uom}"
					),
				)

		# Check IRS Form 8300 Compliance before submit (so it doesn't double count)
		cash_amount = sum(flt(p.amount) for p in si.payments if p.mode_of_payment == "Cash")
		form_8300_triggered = False
		if cash_amount > 0:
			from zevar_core.api.compliance import check_cash_transaction_for_8300, trigger_form_8300

			if check_cash_transaction_for_8300(si.customer, cash_amount):
				form_8300_triggered = True

		si.submit()

		if form_8300_triggered:
			try:
				details_dict = {"invoice": si.name}
				if irs_8300_details:
					details_dict["irs_8300_details"] = frappe.parse_json(irs_8300_details)
				trigger_form_8300(si.customer, cash_amount, details_dict)
			except Exception:
				frappe.log_error("Failed to trigger IRS Form 8300", frappe.get_traceback())

		# Deduct gift card balance only after successful invoice submission
		if gc_payment_amount > 0 and gift_card_number:
			gc_doc = frappe.get_doc("Gift Card", gift_card_number)
			gc_doc.balance = flt(gc_doc.balance) - gc_payment_amount
			if gc_doc.balance <= 0:
				gc_doc.status = "Used"
			gc_doc.save(ignore_permissions=True)

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

		if gc_payment_amount > 0 and gift_card_number:
			log_gift_card_used(gc_doc, gc_payment_amount, source_reference=si.name)

		# Record idempotency log so duplicate syncs are rejected
		if idempotency_key:
			try:
				sync_log = frappe.new_doc("POS Sync Log")
				sync_log.idempotency_key = idempotency_key
				sync_log.sales_invoice = si.name
				sync_log.terminal_user = frappe.session.user
				sync_log.response_payload = frappe.as_json(
					{
						"invoice_name": si.name,
						"grand_total": flt(si.grand_total),
						"status": si.status,
					}
				)
				sync_log.insert(ignore_permissions=True)
			except Exception:
				frappe.log_error("POS Sync Log Creation Failed", frappe.get_traceback())

		checkout_url = None
		payment_request_name = None
		if online_checkout_gateway:
			try:
				from zevar_core.api.pos import initiate_online_checkout
				online_res = initiate_online_checkout("Sales Invoice", si.name, online_checkout_gateway)
				checkout_url = online_res.get("checkout_url")
				payment_request_name = online_res.get("payment_request_name")
			except Exception as e:
				frappe.log_error("Online Checkout Failed", frappe.get_traceback())
				frappe.throw(f"Failed to generate online checkout link: {e}")

		return {
			"success": True,
			"invoice_name": si.name,
			"status": si.status,
			"grand_total": si.grand_total,
			"outstanding_amount": si.outstanding_amount,
			"form_8300_triggered": form_8300_triggered,
			"checkout_url": checkout_url,
			"payment_request_name": payment_request_name,
			"message": f"Successfully created invoice {si.name}",
		}

	except frappe.ValidationError as e:
		frappe.db.rollback()
		frappe.log_error("POS Invoice Validation Error", frappe.get_traceback())
		# Re-raise with clear message
		frappe.throw(
			str(e) or _("Validation error occurred. Please check the form data."), frappe.ValidationError
		)
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("POS Invoice Creation Failed", frappe.get_traceback())
		# Extract meaningful error message
		error_msg = str(e)
		if "ValidationError" in error_msg or "validation" in error_msg.lower():
			frappe.throw(_("Validation error: {0}").format(error_msg), frappe.ValidationError)
		frappe.throw(_("Failed to create POS Invoice: {0}").format(error_msg))


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


@frappe.whitelist()
def get_pos_profile(name: str | None = None):
	"""Return POS profile info including available warehouses."""
	profile_name = name or frappe.db.get_single_value("POS Settings", "default_pos_profile")
	if not profile_name:
		return {"warehouses": []}
	profile = frappe.get_doc("POS Profile", profile_name)
	warehouses = []
	if profile.get("companies"):
		for c in profile.companies:
			if c.get("warehouse"):
				warehouses.append(c.warehouse)
	elif profile.get("warehouse"):
		warehouses.append(profile.warehouse)
	return {"warehouses": warehouses, "name": profile_name}


@frappe.whitelist(allow_guest=True)
def serve_sw():
	"""Serve the POS service worker with correct headers for scope."""
	import os

	from werkzeug.wrappers import Response

	sw_path = frappe.get_app_path("zevar_core", "public", "pos", "sw.js")
	if not os.path.exists(sw_path):
		frappe.throw("Service worker not found", frappe.DoesNotExistError)

	with open(sw_path) as f:
		sw_content = f.read()

	resp = Response(sw_content, content_type="text/javascript; charset=utf-8")
	resp.headers["Service-Worker-Allowed"] = "/"
	resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	return resp


# ---------------------------------------------------------------------------
# Held Cart Management
# ---------------------------------------------------------------------------

_HELD_CART_CACHE_PREFIX = "pos_held_carts:"
_MAX_HELD_CARTS = 10


def _get_held_cart_key():
	return f"{_HELD_CART_CACHE_PREFIX}{frappe.session.user}"


@frappe.whitelist()
def hold_cart(items: str, customer: str | None = None, warehouse: str | None = None, note: str | None = None):
	import json
	import secrets

	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	if not items_list:
		frappe.throw(_("Cannot hold an empty cart."), frappe.ValidationError)

	cache_key = _get_held_cart_key()
	carts = frappe.cache().get_value(cache_key) or []

	if len(carts) >= _MAX_HELD_CARTS:
		frappe.throw(
			_("Maximum of {0} held carts reached. Please recall or discard one first.").format(
				_MAX_HELD_CARTS
			),
			frappe.ValidationError,
		)

	total = sum(flt(i.get("amount", 0)) * flt(i.get("qty", 1)) for i in items_list)
	cart_id = secrets.token_hex(4)

	cart = {
		"id": cart_id,
		"items": items_list,
		"customer": customer or "Walk-In Customer",
		"warehouse": warehouse or "",
		"note": note or "",
		"item_count": len(items_list),
		"total": flt(total),
		"held_at": str(frappe.utils.now_datetime()),
		"held_by": frappe.session.user,
	}

	carts.append(cart)
	frappe.cache().set_value(cache_key, carts)

	return {"success": True, "cart_id": cart_id, "held_count": len(carts)}


@frappe.whitelist()
def get_held_carts():
	cache_key = _get_held_cart_key()
	carts = frappe.cache().get_value(cache_key) or []
	return {"carts": carts, "count": len(carts)}


@frappe.whitelist()
def recall_cart(cart_id: str):
	cache_key = _get_held_cart_key()
	carts = frappe.cache().get_value(cache_key) or []

	matched = [c for c in carts if c["id"] == cart_id]
	if not matched:
		frappe.throw(_("Held cart {0} not found.").format(cart_id), frappe.ValidationError)

	cart = matched[0]
	remaining = [c for c in carts if c["id"] != cart_id]
	frappe.cache().set_value(cache_key, remaining)

	return {"success": True, "cart": cart}


@frappe.whitelist()
def discard_held_cart(cart_id: str):
	cache_key = _get_held_cart_key()
	carts = frappe.cache().get_value(cache_key) or []

	remaining = [c for c in carts if c["id"] != cart_id]
	if len(remaining) == len(carts):
		frappe.throw(_("Held cart {0} not found.").format(cart_id), frappe.ValidationError)

	frappe.cache().set_value(cache_key, remaining)
	return {"success": True, "remaining": len(remaining)}


# ---------------------------------------------------------------------------
# Pre-Submit Cart Validator
# ---------------------------------------------------------------------------


@frappe.whitelist()
def validate_pos_cart(items: str, warehouse: str | None = None):
	import json

	items_list = frappe.parse_json(items) if isinstance(items, str) else items
	issues = []

	for line in items_list:
		item_code = line.get("item_code")
		qty = flt(line.get("qty", 0))
		rate = flt(line.get("rate", 0))

		if not item_code or not frappe.db.exists("Item", item_code):
			issues.append(
				{
					"type": "item_missing",
					"item_code": item_code,
					"blocking": True,
					"message": f"Item {item_code} not found",
				}
			)
			continue

		item = frappe.get_cached_doc("Item", item_code)

		if item.disabled:
			issues.append(
				{
					"type": "item_disabled",
					"item_code": item_code,
					"blocking": True,
					"message": f"Item {item_code} is disabled",
				}
			)

		if qty <= 0:
			issues.append(
				{
					"type": "qty_invalid",
					"item_code": item_code,
					"blocking": True,
					"message": f"Item {item_code}: quantity must be positive",
				}
			)

		if rate <= 0:
			issues.append(
				{
					"type": "rate_invalid",
					"item_code": item_code,
					"blocking": True,
					"message": f"Item {item_code}: rate must be positive",
				}
			)

		# Stock check
		if warehouse and qty > 0:
			actual_qty = flt(
				frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
				or 0
			)
			if actual_qty < qty:
				issues.append(
					{
						"type": "out_of_stock",
						"item_code": item_code,
						"blocking": True,
						"message": f"Insufficient stock for {item_code}: need {qty}, have {actual_qty}",
					}
				)

		# Price drift check (non-blocking)
		current_price = flt(item.standard_rate)
		if rate > 0 and current_price > 0 and abs(rate - current_price) > 0.005:
			pct_drift = abs(rate - current_price) / current_price * 100
			issues.append(
				{
					"type": "price_drift",
					"item_code": item_code,
					"blocking": False,
					"message": f"Price drift: cart {rate} vs current {current_price} ({pct_drift:.1f}%)",
					"details": {
						"cart_rate": rate,
						"current_price": current_price,
						"drift_pct": flt(pct_drift, 1),
					},
				}
			)

	blocking = any(i.get("blocking") for i in issues)
	return {"ok": not blocking, "issues": issues}

@frappe.whitelist(methods=["POST"])
def cancel_pos_invoice(invoice_name: str):
	frappe.only_for(["Sales User", "Sales Manager", "Store Manager", "System Manager", "Employee"])
	
	try:
		doc = frappe.get_doc("Sales Invoice", invoice_name)
		if doc.status == "Cancelled":
			return {"success": True, "message": "Already cancelled."}
		doc.cancel()
		
		# Also cancel any linked Payment Request
		prs = frappe.get_all("Payment Request", filters={"reference_name": invoice_name, "docstatus": 1})
		for pr in prs:
			pr_doc = frappe.get_doc("Payment Request", pr.name)
			pr_doc.cancel()
			
		return {"success": True, "message": "Invoice and pending payment requests cancelled successfully."}
	except Exception as e:
		frappe.log_error("POS Invoice Cancel Failed", frappe.get_traceback())
		frappe.throw(f"Failed to cancel invoice: {str(e)}")

def on_payment_request_update(doc, method):
	"""Listen for payment requests linked to POS invoices becoming Paid"""
	if doc.status == "Paid" and doc.reference_doctype == "Sales Invoice":
		invoice = frappe.get_doc("Sales Invoice", doc.reference_name)
		if invoice.is_pos:
			# Notify the frontend POS session that this invoice was paid via QR code
			frappe.publish_realtime(
				event="payment_received",
				message={"invoice": doc.reference_name, "amount": doc.grand_total},
				user=invoice.owner
			)


@frappe.whitelist(methods=["POST"])
def simulate_payment_success(payment_request_name: str):
	"""
	DEV ONLY: Simulates a webhook from Stripe/Square by marking a Payment Request as Paid.
	This will trigger the on_payment_request_update hook and send the socket event.
	"""
	frappe.only_for(["System Manager", "Administrator"])
	
	try:
		pr = frappe.get_doc("Payment Request", payment_request_name)
		if pr.status != "Paid":
			# Simulate what the gateway's webhook does
			frappe.db.set_value("Payment Request", pr.name, "status", "Paid")
			
			# We must also create a dummy Payment Entry to satisfy accounting
			pe = frappe.new_doc("Payment Entry")
			pe.payment_type = "Receive"
			pe.party_type = "Customer"
			pe.party = pr.reference_name # Need to get customer from the Sales Invoice
			
			invoice = frappe.get_doc("Sales Invoice", pr.reference_name)
			pe.party = invoice.customer
			pe.paid_amount = pr.grand_total
			pe.received_amount = pr.grand_total
			pe.mode_of_payment = "Wire Transfer" # Mock
			
			pe.append("references", {
				"reference_doctype": "Sales Invoice",
				"reference_name": invoice.name,
				"allocated_amount": pr.grand_total
			})
			pe.insert(ignore_permissions=True)
			pe.submit()
			
			# Manually trigger the hook since we used db.set_value
			from zevar_core.api.pos import on_payment_request_update
			pr.status = "Paid"
			on_payment_request_update(pr, "on_update")
			
		return {"success": True, "message": "Payment simulated successfully"}
	except Exception as e:
		frappe.log_error("Simulated Payment Failed", frappe.get_traceback())
		frappe.throw(f"Failed to simulate payment: {str(e)}")
