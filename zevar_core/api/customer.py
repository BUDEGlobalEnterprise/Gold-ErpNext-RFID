"""
Customer API - Customer search and details
"""

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit


@frappe.whitelist()
@rate_limit(limit=100, seconds=60)
def search_customers(query: str):
	"""
	Search customers by name, phone, or email.

	Args:
	    query: Search query string

	Returns:
	    List of matching customers
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not query or len(query) < 2:
		# Return all active customers (limited) when no query provided
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
@rate_limit(limit=100, seconds=60)
def get_customer_details(customer_name: str):
	"""
	Fetch full customer details including preferences.

	Args:
	    customer_name: Customer ID

	Returns:
	    Customer details dictionary
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	customer = frappe.get_doc("Customer", customer_name)

	# Get recent purchase history
	recent_orders = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer_name, "docstatus": 1},
		fields=["name", "posting_date", "grand_total"],
		order_by="posting_date desc",
		limit=5,
	)

	return {
		"customer_name": customer.name,
		"display_name": customer.customer_name,
		"mobile_no": customer.mobile_no,
		"email_id": customer.email_id,
		"customer_group": customer.customer_group,
		"territory": customer.territory,
		# Custom fields
		"spouse_name": customer.custom_spouse_name,
		"anniversary": customer.custom_anniversary,
		"ring_size": customer.custom_ring_size,
		"preferred_metal": customer.custom_preferred_metal,
		"preferred_purity": customer.custom_preferred_purity,
		"tax_exempt": customer.exempt_from_sales_tax,
		# Purchase history
		"recent_orders": recent_orders,
		"total_spent": sum(order.grand_total for order in recent_orders),
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
	ring_size: str | None = None,
	preferred_metal: str | None = None,
	preferred_purity: str | None = None,
	spouse_name: str | None = None,
	anniversary: str | None = None,
	tax_exempt: int = 0,
):
	"""
	Quick create a new customer from POS.

	Args:
	    customer_name: Customer full name (required)
	    customer_type: Customer Type (Individual/Company)
	    mobile_no: Phone number
	    email_id: Email address
	    address_line1: Street address
	    address_line2: Apartment/suite
	    city: City
	    state: State/province
	    pincode: ZIP/postal code
	    ring_size: Customer's ring size preference
	    preferred_metal: Preferred metal type
	    preferred_purity: Preferred gold purity
	    spouse_name: Spouse name for gifting
	    anniversary: Wedding anniversary date
	    tax_exempt: Whether customer is tax exempt (1 or 0)

	Returns:
	    Dict with success status and customer details
	"""
	# Validate required field
	if not customer_name:
		frappe.throw(_("Customer name is required"))

	# Get default customer_group - try multiple sources
	customer_group = frappe.db.get_single_value("Selling Settings", "customer_group") or frappe.db.get_value(
		"Customer Group", {"is_group": 0}, "name", order_by="creation asc"
	)
	if not customer_group:
		# Create Individual group if it doesn't exist
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

	# Get default territory - try multiple sources
	territory = frappe.db.get_single_value("Selling Settings", "territory") or frappe.db.get_value(
		"Territory", {"is_group": 0}, "name", order_by="creation asc"
	)
	if not territory:
		# Get All Territories or first available
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

	# Set custom fields only if they exist in the doctype
	customer_meta = frappe.get_meta("Customer")
	custom_fields = {
		"custom_ring_size": ring_size,
		"custom_preferred_metal": preferred_metal,
		"custom_preferred_purity": preferred_purity,
		"custom_spouse_name": spouse_name,
		"custom_anniversary": anniversary,
	}

	for field_name, value in custom_fields.items():
		if customer_meta.has_field(field_name) and value:
			customer.set(field_name, value)

	# Set tax exempt if field exists
	if customer_meta.has_field("exempt_from_sales_tax"):
		customer.exempt_from_sales_tax = tax_exempt == 1

	customer.insert()

	# Create address if provided
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
					"links": [{"link_doctype": "Customer", "link_name": customer.name}],
				}
			)
			address.insert()
		except Exception:
			# Log address creation error but don't fail customer creation
			frappe.log_error(frappe.get_traceback(), f"Failed to create address for {customer_name}")

	return {
		"success": True,
		"customer_name": customer.name,
		"display_name": customer.customer_name,
		"mobile_no": customer.mobile_no,
		"email_id": customer.email_id,
		"customer_group": customer.customer_group,
		"territory": customer.territory,
	}
