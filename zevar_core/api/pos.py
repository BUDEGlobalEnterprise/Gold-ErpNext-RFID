"""
POS API - Invoice creation and settings
"""

import frappe
from frappe import _
from frappe.utils import flt

from zevar_core.constants import DEFAULT_TAX_RATES, PAYMENT_MODES


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
		frappe.throw(
			_(
				"You do not have permission to create POS Invoices. Required role: Sales User, Employee, or equivalent."
			),
			frappe.PermissionError,
		)

	if not items_list:
		frappe.throw(_("At least one item is required."), frappe.ValidationError)

	if not payments_list:
		frappe.throw(_("At least one payment mode is required."), frappe.ValidationError)

	# Validate all items before creating invoice
	for item in items_list:
		if not item.get("item_code"):
			frappe.throw(_("Each item must have an item_code."), frappe.ValidationError)
		if flt(item.get("qty", 0)) <= 0:
			frappe.throw(
				_("Item {0}: quantity must be greater than zero.").format(item.get("item_code")),
				frappe.ValidationError,
			)
		if flt(item.get("rate", 0)) <= 0:
			frappe.throw(
				_("Item {0}: rate must be greater than zero.").format(item.get("item_code")),
				frappe.ValidationError,
			)
		# Verify item exists in the system
		if not frappe.db.exists("Item", item.get("item_code")):
			frappe.throw(
				_("Item '{0}' not found in the system.").format(item.get("item_code")), frappe.ValidationError
			)

	if not warehouse:
		# Try to get warehouse from active store location
		store_loc = frappe.db.get_value("Store Location", {"is_active": 1}, "default_warehouse")
		if store_loc:
			warehouse = store_loc
		else:
			# Try to get default warehouse from company
			company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
				"Global Defaults", "default_company"
			)
			if company:
				warehouse = frappe.db.get_value("Company", company, "default_warehouse")

	if not warehouse:
		frappe.throw(
			_("Warehouse is required. Please select a store location or configure a default warehouse."),
			frappe.ValidationError,
		)

	if not frappe.db.exists("Warehouse", warehouse):
		frappe.throw(
			_("Warehouse '{0}' not found. Please ensure a valid warehouse is configured.").format(warehouse),
			frappe.ValidationError,
		)

	salesperson_data = []
	if salespersons:
		salesperson_data = frappe.parse_json(salespersons) if isinstance(salespersons, str) else salespersons
		# Validate each salesperson exists
		for sp in salesperson_data[:4]:
			emp = sp.get("salesperson") or sp.get("employee")
			if emp and not frappe.db.exists("Employee", emp):
				frappe.throw(_("Salesperson '{0}' not found.").format(emp), frappe.ValidationError)
		total_split = sum(flt(sp.get("split")) for sp in salesperson_data[:4])
		if salesperson_data and abs(total_split - 100) > 0.01:
			frappe.throw(
				_("Salesperson splits must total 100%. Current total: {0}%").format(total_split),
				frappe.ValidationError,
			)

	is_tax_exempt = str(tax_exempt).lower() in ["true", "1", "t", "y", "yes"]

	if not customer:
		customer = frappe.db.get_single_value("Global Defaults", "default_customer") or "Walk-In Customer"

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
			frappe.throw(_("Customer '{0}' not found.").format(customer), frappe.ValidationError)

	# Validate gift card before creating invoice
	gc_payment_amount = 0
	for pay in payments_list:
		mode = pay.get("mode_of_payment") or pay.get("mode", "")
		if mode == "Gift Card":
			gc_payment_amount = flt(pay.get("amount"))
			break

	if gc_payment_amount > 0:
		if not gift_card_number:
			frappe.throw(
				_("Gift Card number is required when using Gift Card payment."), frappe.ValidationError
			)
		if not frappe.db.exists("Gift Card", gift_card_number):
			frappe.throw(_("Gift Card '{0}' not found.").format(gift_card_number), frappe.ValidationError)

		from frappe.utils import getdate, today

		gc_doc = frappe.get_doc("Gift Card", gift_card_number)
		if gc_doc.status != "Active":
			frappe.throw(
				_("Gift Card is {0}. Cannot process payment.").format(gc_doc.status), frappe.ValidationError
			)
		if gc_doc.expiry_date and getdate(gc_doc.expiry_date) < getdate(today()):
			frappe.throw(_("Gift Card has expired."), frappe.ValidationError)
		if gc_payment_amount > flt(gc_doc.balance):
			frappe.throw(
				_("Gift Card balance insufficient. Available: {0}, Requested: {1}").format(
					flt(gc_doc.balance), gc_payment_amount
				),
				frappe.ValidationError,
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
				},
			)

		if flt(discount_amount) > 0:
			si.apply_discount_on = "Grand Total"
			si.discount_amount = flt(discount_amount)

		if is_tax_exempt:
			# Clear any existing taxes and set override flag
			si.taxes = []
			si.custom_no_tax_override = 1
		elif tax_template:
			si.taxes_and_charges = tax_template
			si.custom_no_tax_override = 0
		else:
			# Prevent auto-fetching company default if store has no tax template
			si.taxes = []
			si.taxes_and_charges = ""
			si.custom_no_tax_override = 1

		for i, sp in enumerate(salesperson_data):
			emp = sp.get("salesperson") or sp.get("employee")
			split = flt(sp.get("split"))
			si.append(
				"custom_salesperson_splits",
				{
					"employee": emp,
					"split_percent": split,
				},
			)
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

		if layaway_reference:
			si.custom_layaway_reference = layaway_reference

		for ti in trade_in_list:
			trade_in_item = {
				"trade_in_value": flt(ti.get("trade_in_value")),
				"new_item_value": flt(ti.get("new_item_value")),
				"manager_override": ti.get("manager_override"),
				"override_reason": ti.get("override_reason"),
			}
			# Use first item from cart as new_item_code if not provided
			if not ti.get("new_item_code") and items_list:
				trade_in_item["new_item_code"] = items_list[0].get("item_code")

			# Map description to original_item_code if it's a valid item code, though it's optional now
			if ti.get("original_item_code"):
				trade_in_item["original_item_code"] = ti.get("original_item_code")
			elif ti.get("description"):
				# If description is provided but not a valid item code, we can't put it in original_item_code (Link)
				# but we can log it or put it in override_reason if blank
				if not trade_in_item.get("override_reason"):
					trade_in_item["override_reason"] = f"Trade-In Item: {ti.get('description')}"

			si.append("custom_trade_ins", trade_in_item)

		# Add trade-in credit as a payment entry
		total_trade_in_credit = (
			sum(flt(ti.get("trade_in_value")) for ti in trade_in_list) if trade_in_list else 0
		)
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
