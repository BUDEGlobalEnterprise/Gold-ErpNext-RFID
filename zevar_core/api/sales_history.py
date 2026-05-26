"""
Sales History API - Query and view past transactions

Provides endpoints for:
- Listing sales with filtering and pagination
- Getting sales summary statistics
- Getting detailed transaction information
"""

import frappe
from frappe import _
from frappe.utils import add_days, cstr, flt, getdate


@frappe.whitelist()
def get_repair_payments_history(
	from_date: str | None = None,
	to_date: str | None = None,
	search: str | None = None,
	page: int = 1,
	page_size: int = 20,
) -> dict:
	"""
	Get repair payments history with filtering and pagination.
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not from_date:
		from_date = add_days(getdate(), -30)
	if not to_date:
		to_date = getdate()

	query = """
		SELECT
			rp.name,
			rp.parent as repair_order,
			rp.creation as payment_date,
			rp.amount,
			rp.mode_of_payment,
			rp.reference_no,
			ro.customer,
			ro.customer_name,
			ro.status as repair_status
		FROM `tabRepair Payment` rp
		JOIN `tabRepair Order` ro ON rp.parent = ro.name
		WHERE DATE(rp.creation) >= %s AND DATE(rp.creation) <= %s
	"""
	params = [cstr(from_date), cstr(to_date)]

	if search:
		query += " AND (rp.parent LIKE %s OR ro.customer_name LIKE %s)"
		params.extend([f"%{search}%", f"%{search}%"])

	query += " ORDER BY rp.creation DESC"

	# Get total count
	count_query = f"SELECT COUNT(*) as count FROM ({query}) as subq"
	total_count = frappe.db.sql(count_query, tuple(params))[0][0]  # nosemgrep

	# Calculate pagination
	total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
	offset = (page - 1) * page_size

	# Get page data
	query += " LIMIT %s OFFSET %s"
	params.extend([page_size, offset])

	payments = frappe.db.sql(query, tuple(params), as_dict=True)  # nosemgrep

	return {
		"payments": payments,
		"pagination": {
			"page": page,
			"total_pages": total_pages,
			"total_count": total_count,
			"page_size": page_size,
		},
	}



@frappe.whitelist()
def get_sales_history(
	from_date: str | None = None,
	to_date: str | None = None,
	customer: str | None = None,
	status: str | None = None,
	search: str | None = None,
	page: int = 1,
	page_size: int = 20,
	owner: str | None = None,
) -> dict:
	"""
	Get sales history with filtering and pagination.

	Args:
		from_date: Start date filter (default: 30 days ago)
		to_date: End date filter (default: today)
		customer: Customer name filter
		status: Invoice status filter (Paid, Unpaid, Overdue, Cancelled)
		search: Search term for invoice number
		page: Page number for pagination
		page_size: Number of records per page
		owner: Filter by owner (email) - for non-admin users to see their own sales only

	Returns:
		dict: Contains 'sales' list and 'pagination' info
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	# Set default date range
	if not from_date:
		from_date = add_days(getdate(), -30)
	if not to_date:
		to_date = getdate()

	# Build filters
	filters = {
		"docstatus": 1,
		"is_pos": 1,
		"posting_date": ["between", [cstr(from_date), cstr(to_date)]],
	}

	# Add owner filter for non-admin users
	if owner:
		filters["owner"] = owner

	if customer:
		filters["customer"] = ["like", f"%{customer}%"]

	if status:
		if status == "Overdue":
			filters["status"] = "Overdue"
		else:
			filters["status"] = status

	if search:
		filters["name"] = ["like", f"%{search}%"]

	# Get total count for pagination
	total_count = frappe.db.count("Sales Invoice", filters=filters)

	# Calculate pagination
	total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
	offset = (page - 1) * page_size

	# Get sales invoices
	sales = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"posting_time",
			"grand_total",
			"outstanding_amount",
			"status",
			"currency",
			"owner",
			"pos_profile",
		],
		order_by="posting_date desc, posting_time desc",
		start=offset,
		page_length=page_size,
	)

	# Enrich sales data using batch fetching to avoid N+1 queries
	if sales:
		sale_names = [s.name for s in sales]

		counts = frappe.db.sql(  # nosemgrep
			"""SELECT parent, count(name) as count
			   FROM `tabSales Invoice Item`
			   WHERE parent IN %s
			   GROUP BY parent""",
			(tuple(sale_names),),
			as_dict=True,
		)
		item_counts = {c.parent: c.count for c in counts}

		customer_ids = list({s.customer for s in sales if not s.get("customer_name")})
		customer_names = {}
		if customer_ids:
			customers = frappe.get_all(
				"Customer", filters={"name": ("in", customer_ids)}, fields=["name", "customer_name"]
			)
			customer_names = {c.name: c.customer_name for c in customers}

		for sale in sales:
			sale["item_count"] = item_counts.get(sale.name, 0)
			if not sale.get("customer_name"):
				sale["customer_name"] = customer_names.get(sale.customer) or sale.customer

	return {
		"sales": sales,
		"pagination": {
			"page": page,
			"total_pages": total_pages,
			"total_count": total_count,
			"page_size": page_size,
		},
	}


@frappe.whitelist()
def get_sales_summary(
	from_date: str | None = None,
	to_date: str | None = None,
	owner: str | None = None,
) -> dict:
	"""
	Get sales summary statistics for a date range.

	Args:
		from_date: Start date filter (default: 30 days ago)
		to_date: End date filter (default: today)
		owner: Filter by owner (email) - for non-admin users to see their own sales only

	Returns:
		dict: Contains 'summary' with transaction_count, total_sales, average_sale, unique_customers
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	# Set default date range
	if not from_date:
		from_date = add_days(getdate(), -30)
	if not to_date:
		to_date = getdate()

	# Get sales statistics
	query = """
		SELECT
			COUNT(*) as transaction_count,
			COALESCE(SUM(grand_total), 0) as total_sales,
			COUNT(DISTINCT customer) as unique_customers
		FROM `tabSales Invoice`
		WHERE docstatus = 1
		AND is_pos = 1
		AND posting_date >= %s
		AND posting_date <= %s
	"""
	params = [cstr(from_date), cstr(to_date)]

	# Add owner filter if specified
	if owner:
		query += " AND owner = %s"
		params.append(owner)

	stats = frappe.db.sql(  # nosemgrep
		query,
		tuple(params),
		as_dict=True,
	)

	if not stats or not stats[0]:
		return {
			"summary": {
				"transaction_count": 0,
				"total_sales": 0,
				"average_sale": 0,
				"unique_customers": 0,
			}
		}

	transaction_count = stats[0].get("transaction_count", 0) or 0
	total_sales = flt(stats[0].get("total_sales", 0))
	unique_customers = stats[0].get("unique_customers", 0) or 0

	# Calculate average sale
	average_sale = total_sales / transaction_count if transaction_count > 0 else 0

	return {
		"summary": {
			"transaction_count": transaction_count,
			"total_sales": flt(total_sales),
			"average_sale": flt(average_sale),
			"unique_customers": unique_customers,
		}
	}


@frappe.whitelist()
def get_transaction_details(invoice_name: str) -> dict:
	"""
	Get detailed information about a specific transaction.

	Args:
		invoice_name: Name of the Sales Invoice

	Returns:
		dict: Contains 'invoice', 'items', 'payments' details
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not invoice_name or not frappe.db.exists("Sales Invoice", invoice_name):
		frappe.throw(_("Invoice '{0}' not found.").format(invoice_name or ""))

	# Get invoice details
	invoice = frappe.get_doc("Sales Invoice", invoice_name)

	# Check permission - user should have access to this invoice
	user = frappe.session.user
	user_roles = frappe.get_roles(user)

	# Allow if user created the invoice or is a manager
	if invoice.owner != user and "Sales Manager" not in user_roles and "System Manager" not in user_roles:
		frappe.throw(_("You don't have permission to view this invoice."))

	# Get items
	items = []
	for item in invoice.items:
		items.append(
			{
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": flt(item.qty),
				"rate": flt(item.rate),
				"amount": flt(item.amount),
				"warehouse": item.warehouse,
			}
		)

	# Get payments
	payments = []
	if hasattr(invoice, "payments") and invoice.payments:
		for payment in invoice.payments:
			payments.append(
				{
					"mode_of_payment": payment.mode_of_payment,
					"amount": flt(payment.amount),
					"reference_no": payment.reference_no or "",
				}
			)

	# Get salespersons from child table or fallback to legacy custom fields if present
	salespersons = []
	if hasattr(invoice, "custom_salesperson_splits") and invoice.custom_salesperson_splits:
		for row in invoice.custom_salesperson_splits:
			salespersons.append({"employee": row.employee, "split": flt(row.split_percent)})
	else:
		# Fallback for old records before the migration
		for i in range(1, 5):
			sp_field = f"custom_salesperson_{i}"
			split_field = f"custom_salesperson_{i}_split"
			if hasattr(invoice, sp_field):
				sp = getattr(invoice, sp_field)
				if sp:
					salespersons.append(
						{
							"employee": sp,
							"split": flt(getattr(invoice, split_field, 0)),
						}
					)

	# Get totals
	subtotal = sum(flt(item.amount) for item in invoice.items)
	discount = flt(invoice.discount_amount) if hasattr(invoice, "discount_amount") else 0
	tax = flt(invoice.total_taxes_and_charges) if hasattr(invoice, "total_taxes_and_charges") else 0

	return {
		"invoice": {
			"name": invoice.name,
			"customer": invoice.customer,
			"customer_name": invoice.customer_name,
			"posting_date": str(invoice.posting_date),
			"posting_time": str(invoice.posting_time) if hasattr(invoice, "posting_time") else "",
			"status": invoice.status,
			"currency": invoice.currency,
			"subtotal": flt(subtotal),
			"discount": flt(discount),
			"tax": flt(tax),
			"grand_total": flt(invoice.grand_total),
			"outstanding_amount": flt(invoice.outstanding_amount),
			"owner": invoice.owner,
			"pos_profile": invoice.pos_profile if hasattr(invoice, "pos_profile") else "",
		},
		"items": items,
		"payments": payments,
		"salespersons": salespersons,
	}


@frappe.whitelist()
def get_sales_by_payment_mode(
	from_date: str | None = None,
	to_date: str | None = None,
) -> dict:
	"""
	Get sales breakdown by payment mode.

	Args:
		from_date: Start date filter
		to_date: End date filter

	Returns:
		dict: Payment mode breakdown with amounts
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	if not from_date:
		from_date = add_days(getdate(), -30)
	if not to_date:
		to_date = getdate()

	# Get payment breakdown from Sales Invoice payments
	payments = frappe.db.sql(  # nosemgrep
		"""
		SELECT
			sip.mode_of_payment,
			COUNT(*) as transaction_count,
			SUM(sip.amount) as total_amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1
		AND si.is_pos = 1
		AND si.posting_date >= %s
		AND si.posting_date <= %s
		GROUP BY sip.mode_of_payment
		ORDER BY total_amount DESC
		""",
		(cstr(from_date), cstr(to_date)),
		as_dict=True,
	)

	return {
		"payments": payments,
		"from_date": cstr(from_date),
		"to_date": cstr(to_date),
	}


@frappe.whitelist()
def export_sales_history(
	from_date: str | None = None,
	to_date: str | None = None,
	format: str = "csv",
) -> str:
	"""
	Export sales history to CSV or Excel format.

	Args:
		from_date: Start date filter
		to_date: End date filter
		format: Export format (csv or excel)

	Returns:
		str: Download URL or file content
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "Employee", "Employee Self Service"])

	# Get sales data
	result = get_sales_history(
		from_date=from_date,
		to_date=to_date,
		page=1,
		page_size=10000,  # Large page size for export
	)

	sales = result.get("sales", [])

	if not sales:
		frappe.throw(_("No sales data found for the selected date range."))

	# Generate CSV content
	if format == "csv":
		import csv
		import io

		output = io.StringIO()
		writer = csv.writer(output)

		# Header
		writer.writerow(
			[
				"Invoice #",
				"Date",
				"Time",
				"Customer",
				"Items",
				"Total",
				"Status",
				"Salesperson",
			]
		)

		# Data rows
		for sale in sales:
			writer.writerow(
				[
					sale.get("name", ""),
					str(sale.get("posting_date", "")),
					str(sale.get("posting_time", "")),
					sale.get("customer_name", sale.get("customer", "")),
					sale.get("item_count", 0),
					flt(sale.get("grand_total", 0)),
					sale.get("status", ""),
					sale.get("owner", ""),
				]
			)

		return output.getvalue()

	frappe.throw(_("Unsupported export format: {0}").format(format))
