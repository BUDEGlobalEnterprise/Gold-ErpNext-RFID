"""
Customer API - Customer search, details, recent, and edit
"""

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

# Roles allowed to search/select customers in POS (broad access)
POS_CUSTOMER_ROLES = [
	"Sales User",
	"Sales Manager",
	"Sales Master Manager",
	"System Manager",
	"Store Manager",
	"Accounts Manager",
	"Employee",
	"ESS",
]

# Roles allowed to EDIT customer details (admin/manager only)
CUSTOMER_EDIT_ROLES = [
	"System Manager",
	"Store Manager",
	"Accounts Manager",
	"Sales Manager",
	"Sales Master Manager",
]


def _check_pos_customer_role():
	"""Check if current user has POS customer access. Throws if not."""
	user_roles = frappe.get_roles()
	for role in POS_CUSTOMER_ROLES:
		if role in user_roles:
			return
	frappe.throw(
		_("You do not have permission to access customer information."),
		frappe.PermissionError,
	)


def _check_customer_edit_role():
	"""Check if current user can edit customer details. Throws if not."""
	user_roles = frappe.get_roles()
	for role in CUSTOMER_EDIT_ROLES:
		if role in user_roles:
			return
	frappe.throw(
		_("Only admin/manager roles can edit customer details."),
		frappe.PermissionError,
	)


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def search_customers(query: str):
	"""
	Search customers by name, phone, or email.
	Accessible to POS roles (Employee, ESS, Sales User, etc.).
	"""
	_check_pos_customer_role()

	if not query or len(query) < 2:
		customers = frappe.db.sql(
			"""
			SELECT
				name as customer_name,
				customer_name as display_name,
				mobile_no,
				email_id,
				customer_group,
				territory
			FROM `tabCustomer`
			WHERE disabled = 0
			ORDER BY customer_name
			LIMIT 100
		""",
			as_dict=True,
		)
		return customers

	query_lower = f"%{query.lower()}%"

	customers = frappe.db.sql(  # nosemgrep
		"""
        SELECT
            name as customer_name,
            customer_name as display_name,
            mobile_no,
            email_id,
            customer_group,
            territory
        FROM `tabCustomer`
        WHERE (
            LOWER(name) LIKE %(query)s
            OR LOWER(customer_name) LIKE %(query)s
            OR LOWER(mobile_no) LIKE %(query)s
            OR LOWER(email_id) LIKE %(query)s
        )
        AND disabled = 0
        ORDER BY customer_name
        LIMIT 20
    """,
		{"query": query_lower},
		as_dict=True,
	)

	return customers


@frappe.whitelist()
def get_customer_details(customer_name: str) -> dict:
	"""
	Fetch full customer details including preferences, sizes, and extra info.
	Accessible to POS roles (Employee, ESS, Sales User, etc.).
	"""
	_check_pos_customer_role()

	if not customer_name or not frappe.db.exists("Customer", customer_name):
		frappe.throw(_("Customer '{0}' not found.").format(customer_name))

	customer = frappe.get_doc("Customer", customer_name)
	customer_meta = frappe.get_meta("Customer")

	result = {
		"name": customer.name,
		"customer_name": customer.customer_name,
		"display_name": customer.customer_name,
		"mobile_no": customer.mobile_no or "",
		"email_id": customer.email_id or "",
		"customer_type": customer.customer_type or "Individual",
	}

	def safe_get(doc, field, default=""):
		try:
			return doc.get(field) or default
		except Exception:
			return default

	if customer_meta.has_field("gender"):
		result["gender"] = safe_get(customer, "gender")
	if customer_meta.has_field("custom_birth_date"):
		result["birth_date"] = safe_get(customer, "custom_birth_date")
	if customer_meta.has_field("custom_profession"):
		result["profession"] = safe_get(customer, "custom_profession")
	if customer_meta.has_field("custom_partner_name"):
		result["partner_name"] = safe_get(customer, "custom_partner_name")
	if customer_meta.has_field("custom_partner_phone"):
		result["partner_phone"] = safe_get(customer, "custom_partner_phone")
	if customer_meta.has_field("custom_partner_email"):
		result["partner_email"] = safe_get(customer, "custom_partner_email")
	if customer_meta.has_field("custom_marriage_date"):
		result["marriage_date"] = safe_get(customer, "custom_marriage_date")
	if customer_meta.has_field("custom_spouse_name"):
		result["spouse_name"] = safe_get(customer, "custom_spouse_name")
	if customer_meta.has_field("custom_anniversary"):
		result["anniversary"] = safe_get(customer, "custom_anniversary")
	if customer_meta.has_field("custom_ring_size"):
		result["ring_size"] = safe_get(customer, "custom_ring_size")
	if customer_meta.has_field("custom_preferred_metal"):
		result["preferred_metal"] = safe_get(customer, "custom_preferred_metal")
	if customer_meta.has_field("custom_preferred_purity"):
		result["preferred_purity"] = safe_get(customer, "custom_preferred_purity")
	if customer_meta.has_field("exempt_from_sales_tax"):
		result["tax_exempt"] = safe_get(customer, "exempt_from_sales_tax")
	if customer_meta.has_field("custom_phone2"):
		result["phone2"] = safe_get(customer, "custom_phone2")
	if customer_meta.has_field("custom_internal_notes"):
		result["internal_notes"] = safe_get(customer, "custom_internal_notes")
	if customer_meta.has_field("custom_accepts_marketing"):
		result["accepts_marketing"] = safe_get(customer, "custom_accepts_marketing")

	size_fields = [
		"custom_ring_left_size",
		"custom_ring_right_size",
		"custom_middle_left_size",
		"custom_middle_right_size",
		"custom_index_left_size",
		"custom_index_right_size",
		"custom_pink_left_size",
		"custom_pink_right_size",
		"custom_thumb_left_size",
		"custom_thumb_right_size",
		"custom_wrist_size",
		"custom_neck_size",
	]
	for sf in size_fields:
		if customer_meta.has_field(sf):
			key = sf.replace("custom_", "")
			result[key] = safe_get(customer, sf)

	address_rows = frappe.get_all(
		"Address",
		filters={
			"name": [
				"in",
				[
					d.parent
					for d in frappe.get_all(
						"Dynamic Link",
						filters={"link_name": customer_name, "parenttype": "Address"},
						fields=["parent"],
					)
				],
			]
		},
		fields=[
			"name",
			"address_line1",
			"address_line2",
			"city",
			"state",
			"pincode",
			"country",
			"phone",
			"is_primary_address",
			"is_shipping_address",
		],
	)
	if address_rows:
		# Prefer primary for billing, otherwise the first row.
		billing = next(
			(a for a in address_rows if a.is_primary_address),
			address_rows[0],
		)
		shipping = next(
			(a for a in address_rows if a.is_shipping_address),
			None,
		)
		result["address"] = billing.address_line1 or ""
		result["city"] = billing.city or ""
		result["state"] = billing.state or ""
		result["zip"] = billing.pincode or ""
		result["country"] = billing.country or ""

		result["ship_address_line1"] = (shipping or billing).address_line1 or ""
		result["ship_city"] = (shipping or billing).city or ""
		result["ship_state"] = (shipping or billing).state or ""
		result["ship_pincode"] = (shipping or billing).pincode or ""
		result["ship_country"] = (shipping or billing).country or ""
		result["same_as_billing"] = shipping is None

	recent_orders = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer_name, "docstatus": 1},
		fields=["name", "posting_date", "grand_total"],
		order_by="posting_date desc",
		limit=5,
	)
	result["recent_orders"] = recent_orders
	result["total_spent"] = sum(order.grand_total for order in recent_orders)

	return result


@frappe.whitelist()
def get_recent_customers(limit: int = 10) -> list:
	"""
	Return the N most recently purchased customers for quick access in POS.
	Uses Sales Invoice data to find customers with recent transactions.
	Accessible to all POS roles (Employee, ESS, etc.).
	"""
	_check_pos_customer_role()

	# Find distinct customers with completed invoices, ordered by most recent
	customer_names = frappe.db.sql(
		"""
		SELECT DISTINCT si.customer, si.posting_date, si.grand_total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
			AND si.customer IS NOT NULL
			AND si.customer != ''
			AND si.is_return = 0
		ORDER BY si.posting_date DESC, si.creation DESC
		LIMIT %(limit)s
		""",
		{"limit": int(limit)},
		as_dict=True,
	)

	if not customer_names:
		return []

	# Fetch customer details in bulk
	names = [c.customer for c in customer_names]
	customers = frappe.db.get_all(
		"Customer",
		filters={"name": ["in", names], "disabled": 0},
		fields=[
			"name",
			"customer_name",
			"mobile_no",
			"email_id",
			"customer_type",
			"customer_group",
			"territory",
		],
	)

	# Build a lookup for invoice data
	invoice_map = {}
	for c in customer_names:
		if c.customer not in invoice_map:
			invoice_map[c.customer] = {
				"last_sale_date": c.posting_date,
				"last_sale_total": c.grand_total,
			}

	# Merge customer data with invoice info
	result = []
	for cust in customers:
		invoice_info = invoice_map.get(cust.name, {})
		result.append(
			{
				"name": cust.name,
				"customer_name": cust.customer_name,
				"display_name": cust.customer_name,
				"mobile_no": cust.mobile_no or "",
				"email_id": cust.email_id or "",
				"customer_type": cust.customer_type or "Individual",
				"customer_group": cust.customer_group or "Standard",
				"territory": cust.territory or "",
				"last_sale_date": invoice_info.get("last_sale_date"),
				"last_sale_total": invoice_info.get("last_sale_total", 0),
			}
		)

	return result


def _update_customer_address(customer_name, address_type, addr_fields):
	try:
		existing = None
		links = frappe.get_all(
			"Dynamic Link",
			filters={"link_name": customer_name, "parenttype": "Address"},
			fields=["parent"],
		)
		for link in links:
			addr_type = frappe.db.get_value("Address", link.parent, "address_type")
			if addr_type == address_type:
				existing = link.parent
				break

		if existing:
			addr = frappe.get_doc("Address", existing)
			for key, value in addr_fields.items():
				if value:
					addr.set(key, value)
			addr.save()
		else:
			addr = frappe.get_doc(
				{
					"doctype": "Address",
					"address_title": customer_name,
					"address_type": address_type,
					**addr_fields,
					"links": [{"link_doctype": "Customer", "link_name": customer_name}],
				}
			)
			addr.insert()
	except Exception as e:
		frappe.log_error(
			title=f"Failed to update {address_type} address for {customer_name}",
			message=frappe.get_traceback() + "\n\nError: " + str(e),
		)
		raise


@frappe.whitelist()
def get_customer_edit_info(customer_name: str) -> dict:
	"""
	Fetch full customer details for the edit form.
	Admin/manager only.
	"""
	_check_pos_customer_role()

	return get_customer_details(customer_name)


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60)
def update_customer(
	customer_name: str,
	customer_type: str | None = None,
	mobile_no: str | None = None,
	email_id: str | None = None,
	gender: str | None = None,
	birth_date: str | None = None,
	profession: str | None = None,
	partner_name: str | None = None,
	partner_phone: str | None = None,
	partner_email: str | None = None,
	marriage_date: str | None = None,
	spouse_name: str | None = None,
	anniversary: str | None = None,
	ring_size: str | None = None,
	preferred_metal: str | None = None,
	preferred_purity: str | None = None,
	tags: str | None = None,
	internal_notes: str | None = None,
	phone2: str | None = None,
	accepts_marketing: int = 0,
	tax_exempt: int = 0,
	ring_left_size: str | None = None,
	ring_right_size: str | None = None,
	middle_left_size: str | None = None,
	middle_right_size: str | None = None,
	index_left_size: str | None = None,
	index_right_size: str | None = None,
	pink_left_size: str | None = None,
	pink_right_size: str | None = None,
	thumb_left_size: str | None = None,
	thumb_right_size: str | None = None,
	wrist_size: str | None = None,
	neck_size: str | None = None,
	customer_group: str | None = None,
	territory: str | None = None,
	address_line1: str | None = None,
	address_line2: str | None = None,
	city: str | None = None,
	state: str | None = None,
	pincode: str | None = None,
	country: str | None = None,
	same_as_billing: int = 1,
	ship_address_line1: str | None = None,
	ship_city: str | None = None,
	ship_state: str | None = None,
	ship_pincode: str | None = None,
	ship_country: str | None = None,
	display_name: str | None = None,
):
	"""
	Update an existing customer's details.
	Admin/manager only (System Manager, Store Manager, Accounts Manager,
	Sales Manager, Sales Master Manager).
	ESS and Employee roles are explicitly excluded.
	"""
	_check_customer_edit_role()

	if not customer_name:
		frappe.throw(_("Customer name is required"))

	if not frappe.db.exists("Customer", customer_name):
		frappe.throw(_("Customer '{0}' not found.").format(customer_name))

	customer = frappe.get_doc("Customer", customer_name)
	customer_meta = frappe.get_meta("Customer")

	def safe_set(field_name, value, default=""):
		"""Set field only if it exists on the DocType and value is provided."""
		if customer_meta.has_field(field_name) and value and value != default:
			customer.set(field_name, value)

	# Core fields
	if customer_type:
		customer.customer_type = customer_type
	if mobile_no:
		customer.mobile_no = mobile_no
	if email_id:
		customer.email_id = email_id
	if customer_group:
		customer.customer_group = customer_group
	if territory:
		customer.territory = territory
		if display_name:
			customer.customer_name = display_name

	# Custom fields
	safe_set("gender", gender)
	safe_set("birth_date", birth_date)
	safe_set("custom_birth_date", birth_date)
	safe_set("custom_profession", profession)
	safe_set("spouse_name", partner_name)
	safe_set("custom_partner_name", partner_name)
	safe_set("custom_partner_phone", partner_phone)
	safe_set("custom_partner_email", partner_email)
	safe_set("anniversary_date", marriage_date)
	safe_set("custom_marriage_date", marriage_date)
	safe_set("custom_anniversary", marriage_date)
	safe_set("custom_spouse_name", spouse_name)
	safe_set("custom_anniversary", anniversary)
	safe_set("custom_ring_size", ring_size)
	safe_set("custom_preferred_metal", preferred_metal)
	safe_set("custom_preferred_purity", preferred_purity)
	safe_set("custom_phone2", phone2)
	safe_set("custom_internal_notes", internal_notes)

	if tags:
		customer.set("__tags", tags)

	if customer_meta.has_field("custom_accepts_marketing"):
		customer.custom_accepts_marketing = accepts_marketing == 1

	if customer_meta.has_field("exempt_from_sales_tax"):
		customer.exempt_from_sales_tax = tax_exempt == 1

	# Ring sizes
	safe_set("custom_ring_left_size", ring_left_size)
	safe_set("custom_ring_right_size", ring_right_size)
	safe_set("custom_middle_left_size", middle_left_size)
	safe_set("custom_middle_right_size", middle_right_size)
	safe_set("custom_index_left_size", index_left_size)
	safe_set("custom_index_right_size", index_right_size)
	safe_set("custom_pink_left_size", pink_left_size)
	safe_set("custom_pink_right_size", pink_right_size)
	safe_set("custom_thumb_left_size", thumb_left_size)
	safe_set("custom_thumb_right_size", thumb_right_size)
	safe_set("custom_wrist_size", wrist_size)
	safe_set("custom_neck_size", neck_size)

	customer.save()

	# Update or create billing address
	if address_line1 or city:
		_update_customer_address(
			customer_name,
			"Billing",
			{
				"address_line1": address_line1,
				"address_line2": address_line2,
				"city": city,
				"state": state,
				"pincode": pincode,
				"country": country or "United States",
			},
		)

	# Update or create shipping address
	if not same_as_billing and (ship_address_line1 or ship_city):
		_update_customer_address(
			customer_name,
			"Shipping",
			{
				"address_line1": ship_address_line1,
				"city": ship_city,
				"state": ship_state,
				"pincode": ship_pincode,
				"country": ship_country or "United States",
			},
		)

	return {
		"success": True,
		"customer_name": customer.name,
		"display_name": customer.customer_name,
		"message": _("Customer '{0}' updated successfully.").format(customer_name),
	}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60)
def quick_create_customer(
	customer_name: str,
	customer_type: str = "Individual",
	mobile_no: str | None = None,
	email_id: str | None = None,
	address_line1: str | None = None,
	address_line2: str | None = None,
	city: str | None = None,
	state: str | None = None,
	pincode: str | None = None,
	country: str | None = None,
	gender: str | None = None,
	birth_date: str | None = None,
	partner_name: str | None = None,
	partner_phone: str | None = None,
	partner_email: str | None = None,
	marriage_date: str | None = None,
	profession: str | None = None,
	tags: str | None = None,
	internal_notes: str | None = None,
	phone2: str | None = None,
	accepts_marketing: int = 0,
	tax_exempt: int = 0,
	ring_left_size: str | None = None,
	ring_right_size: str | None = None,
	middle_left_size: str | None = None,
	middle_right_size: str | None = None,
	index_left_size: str | None = None,
	index_right_size: str | None = None,
	pink_left_size: str | None = None,
	pink_right_size: str | None = None,
	thumb_left_size: str | None = None,
	thumb_right_size: str | None = None,
	wrist_size: str | None = None,
	neck_size: str | None = None,
	same_as_billing: int = 1,
	ship_address_line1: str | None = None,
	ship_city: str | None = None,
	ship_state: str | None = None,
	ship_pincode: str | None = None,
	ship_country: str | None = None,
):
	"""
	Quick create a new customer from POS with full details.
	"""
	if not customer_name:
		frappe.throw(_("Customer name is required"))

	customer_group = frappe.db.get_single_value("Selling Settings", "customer_group") or frappe.db.get_value(
		"Customer Group", {"is_group": 0}, "name", order_by="creation asc"
	)
	if not customer_group:
		if not frappe.db.exists("Customer Group", "Individual"):
			group = frappe.get_doc(
				{
					"doctype": "Customer Group",
					"customer_group_name": "Individual",
					"is_group": 0,
				}
			)
			group.insert(ignore_permissions=True)
		customer_group = "Individual"

	territory = frappe.db.get_single_value("Selling Settings", "territory") or frappe.db.get_value(
		"Territory", {"is_group": 0}, "name", order_by="creation asc"
	)
	if not territory:
		territory = frappe.db.get_value("Territory", {"name": "All Territories"}, "name")
		if not territory:
			territory = frappe.db.get_value("Territory", {}, "name", order_by="creation asc")

	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_type": customer_type,
			"customer_group": customer_group,
			"territory": territory,
			"mobile_no": mobile_no,
			"email_id": email_id,
		}
	)

	customer_meta = frappe.get_meta("Customer")

	def set_if_exists(field_name, value):
		if customer_meta.has_field(field_name) and value:
			customer.set(field_name, value)

	set_if_exists("gender", gender)
	set_if_exists("birth_date", birth_date)
	set_if_exists("custom_birth_date", birth_date)
	set_if_exists("custom_profession", profession)
	set_if_exists("spouse_name", partner_name)
	set_if_exists("custom_partner_name", partner_name)
	set_if_exists("custom_partner_phone", partner_phone)
	set_if_exists("custom_partner_email", partner_email)
	set_if_exists("anniversary_date", marriage_date)
	set_if_exists("custom_marriage_date", marriage_date)
	set_if_exists("custom_anniversary", marriage_date)
	set_if_exists("custom_phone2", phone2)
	set_if_exists("custom_internal_notes", internal_notes)

	if tags:
		customer.set("__tags", tags)

	set_if_exists("custom_ring_left_size", ring_left_size)
	set_if_exists("custom_ring_right_size", ring_right_size)
	set_if_exists("custom_middle_left_size", middle_left_size)
	set_if_exists("custom_middle_right_size", middle_right_size)
	set_if_exists("custom_index_left_size", index_left_size)
	set_if_exists("custom_index_right_size", index_right_size)
	set_if_exists("custom_pink_left_size", pink_left_size)
	set_if_exists("custom_pink_right_size", pink_right_size)
	set_if_exists("custom_thumb_left_size", thumb_left_size)
	set_if_exists("custom_thumb_right_size", thumb_right_size)
	set_if_exists("custom_wrist_size", wrist_size)
	set_if_exists("custom_neck_size", neck_size)

	if customer_meta.has_field("custom_accepts_marketing"):
		customer.custom_accepts_marketing = accepts_marketing == 1

	if customer_meta.has_field("exempt_from_sales_tax"):
		customer.exempt_from_sales_tax = tax_exempt == 1

	customer.insert()

	if address_line1 or city:
		try:
			address = frappe.get_doc(
				{
					"doctype": "Address",
					"address_title": customer_name,
					"address_type": "Billing",
					"address_line1": address_line1,
					"address_line2": address_line2,
					"city": city,
					"state": state,
					"pincode": pincode,
					"country": country or "United States",
					"links": [{"link_doctype": "Customer", "link_name": customer.name}],
				}
			)
			address.insert()
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Failed to create billing address for {customer_name}",
			)

	if not same_as_billing and (ship_address_line1 or ship_city):
		try:
			ship_address = frappe.get_doc(
				{
					"doctype": "Address",
					"address_title": customer_name,
					"address_type": "Shipping",
					"address_line1": ship_address_line1,
					"city": ship_city,
					"state": ship_state,
					"pincode": ship_pincode,
					"country": ship_country or "United States",
					"links": [{"link_doctype": "Customer", "link_name": customer.name}],
				}
			)
			ship_address.insert()
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Failed to create shipping address for {customer_name}",
			)

	return {
		"success": True,
		"customer_name": customer.name,
		"display_name": customer.customer_name,
		"mobile_no": customer.mobile_no,
		"email_id": customer.email_id,
		"customer_group": customer.customer_group,
		"territory": customer.territory,
	}
