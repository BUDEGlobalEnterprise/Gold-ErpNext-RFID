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

		counts = frappe.db.sql(
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

	stats = frappe.db.sql(
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
	payments = frappe.db.sql(
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


@frappe.whitelist()
def get_daily_sales_heatmap(year: int, month: int, stream: str = "Jewelry Sale") -> list:
	"""
	Get daily sales metrics for a heatmap calendar.
	"""
	frappe.has_permission("Sales Invoice", "read", throw=True)

	# Fetch grouped by date
	data = frappe.db.sql(
		"""
		SELECT
			posting_date as date,
			SUM(grand_total) as gross,
			SUM(total_taxes_and_charges) as tax,
			SUM(base_net_total) as net,
			COUNT(name) as transaction_count,
			SUM(CASE WHEN custom_transaction_stream = 'Repair' THEN 1 ELSE 0 END) as repairs_count
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1
		AND YEAR(posting_date) = %s AND MONTH(posting_date) = %s
		AND custom_transaction_stream = %s
		GROUP BY posting_date
	""",
		(year, month, stream),
		as_dict=True,
	)

	# Also need layaway deposits. Layaway deposits are just Payment Entries where account is liability
	layaway_data = frappe.db.sql(
		"""
		SELECT
			posting_date as date,
			SUM(paid_amount) as layaway_deposits
		FROM `tabPayment Entry`
		WHERE docstatus = 1
		AND paid_to = 'Liability — Layaway Deposits Held - ZJ'
		AND YEAR(posting_date) = %s AND MONTH(posting_date) = %s
		GROUP BY posting_date
	""",
		(year, month),
		as_dict=True,
	)

	layaway_map = {str(d.date): d.layaway_deposits for d in layaway_data}

	for row in data:
		date_str = str(row.date)
		row["layaway_deposits"] = layaway_map.get(date_str, 0.0)
		# ensure floats
		row["gross"] = flt(row.get("gross", 0))
		row["tax"] = flt(row.get("tax", 0))
		row["net"] = flt(row.get("net", 0))

	return data


@frappe.whitelist()
def get_day_drilldown(date: str) -> dict:
	"""
	Get detailed drilldown for a specific day.
	"""
	frappe.has_permission("Sales Invoice", "read", throw=True)

	# Net sales
	net_sales = frappe.db.sql(
		"""
		SELECT SUM(base_net_total)
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s AND custom_transaction_stream = 'Jewelry Sale'
	""",
		(date,),
	)
	net_sales = flt(net_sales[0][0]) if net_sales and net_sales[0][0] else 0.0

	# Repairs
	repairs = frappe.db.sql(
		"""
		SELECT SUM(base_net_total)
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s AND custom_transaction_stream = 'Repair'
	""",
		(date,),
	)
	repairs = flt(repairs[0][0]) if repairs and repairs[0][0] else 0.0

	# Layaway Deposits
	layaways = frappe.db.sql(
		"""
		SELECT SUM(paid_amount)
		FROM `tabPayment Entry`
		WHERE docstatus = 1 AND posting_date = %s AND paid_to = 'Liability — Layaway Deposits Held - ZJ'
	""",
		(date,),
	)
	layaways = flt(layaways[0][0]) if layaways and layaways[0][0] else 0.0

	# Top items
	top_items = frappe.db.sql(
		"""
		SELECT i.item_code, i.item_name, SUM(i.qty) as qty, SUM(i.amount) as amount
		FROM `tabSales Invoice Item` i
		JOIN `tabSales Invoice` s ON i.parent = s.name
		WHERE s.docstatus = 1 AND s.is_pos = 1 AND s.posting_date = %s AND s.custom_transaction_stream = 'Jewelry Sale'
		GROUP BY i.item_code, i.item_name
		ORDER BY amount DESC
		LIMIT 5
	""",
		(date,),
		as_dict=True,
	)

	# Hourly curve
	hourly = frappe.db.sql(
		"""
		SELECT HOUR(posting_time) as hour, SUM(base_net_total) as amount
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s AND custom_transaction_stream = 'Jewelry Sale'
		GROUP BY HOUR(posting_time)
		ORDER BY hour ASC
	""",
		(date,),
		as_dict=True,
	)

	# Tender breakdown
	tender = frappe.db.sql(
		"""
		SELECT p.mode_of_payment as name, SUM(p.amount) as value
		FROM `tabSales Invoice Payment` p
		JOIN `tabSales Invoice` s ON p.parent = s.name
		WHERE s.docstatus = 1 AND s.is_pos = 1 AND s.posting_date = %s
		GROUP BY p.mode_of_payment
		ORDER BY value DESC
	""",
		(date,),
		as_dict=True,
	)

	return {
		"net_sales": net_sales,
		"repairs": repairs,
		"layaway_deposits": layaways,
		"top_items": top_items,
		"hourly_curve": hourly,
		"tender_breakdown": tender,
	}


@frappe.whitelist()
def get_yoy_delta(date: str) -> dict:
	"""
	Get YoY delta for a specific date.
	"""
	frappe.has_permission("Sales Invoice", "read", throw=True)
	from frappe.utils import add_days, getdate

	compare_mode = frappe.db.get_single_value("POS Settings", "custom_yoy_compare_mode") or "Exact Date"

	if compare_mode == "ISO Weekday Matched":
		last_year_date = add_days(date, -364)  # 52 weeks * 7 days = 364 days, matches weekday
	else:
		last_year_date = add_days(date, -365)

	# This year net sales
	this_year = frappe.db.sql(
		"""
		SELECT SUM(base_net_total)
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s AND custom_transaction_stream = 'Jewelry Sale'
	""",
		(date,),
	)
	this_year = flt(this_year[0][0]) if this_year and this_year[0][0] else 0.0

	# Last year net sales
	last_year = frappe.db.sql(
		"""
		SELECT SUM(base_net_total)
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s AND custom_transaction_stream = 'Jewelry Sale'
	""",
		(last_year_date,),
	)
	last_year = flt(last_year[0][0]) if last_year and last_year[0][0] else 0.0

	delta_abs = this_year - last_year
	delta_pct = (delta_abs / last_year * 100) if last_year > 0 else (100 if this_year > 0 else 0)

	return {
		"this_year": this_year,
		"last_year": last_year,
		"delta_abs": delta_abs,
		"delta_pct": delta_pct,
		"last_year_date": str(last_year_date),
	}
