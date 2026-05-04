"""
Data Export API - CSV/Excel export functionality

Provides data export capabilities for reports and analytics.
"""

import csv
import io
import json
from typing import Any

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, now_datetime, today


@frappe.whitelist()
def export_sales_data(
	from_date: str | None = None,
	to_date: str | None = None,
	warehouse: str | None = None,
	format: str = "csv",
	include_items: bool = True,
	include_payments: bool = True,
) -> dict:
	"""
	Export sales data to CSV or Excel.

	Args:
		from_date: Start date
		to_date: End date
		warehouse: Filter by warehouse
		format: Export format ('csv' or 'excel')
		include_items: Include item details
		include_payments: Include payment details

	Returns:
		File URL and export details
	"""
	frappe.only_for(["Sales Manager", "System Manager"])

	if not from_date:
		from_date = add_days(today(), -30)
	if not to_date:
		to_date = today()

	# Get sales data
	sales = frappe.get_all(
		"Sales Invoice",
		filters={
			"is_pos": 1,
			"docstatus": 1,
			"posting_date": ["between", [from_date, to_date]],
		},
		fields=[
			"name",
			"customer",
			"posting_date",
			"posting_time",
			"grand_total",
			"total_taxes_and_charges",
			"discount_amount",
			"outstanding_amount",
			"status",
			"owner",
		],
		order_by="posting_date desc",
		limit_page_length=10000,
	)

	if format == "csv":
		file_url = generate_sales_csv(sales, include_items, include_payments)
	else:
		file_url = generate_sales_excel(sales, include_items, include_payments)

	return {
		"success": True,
		"file_url": file_url,
		"record_count": len(sales),
		"from_date": from_date,
		"to_date": to_date,
	}


def generate_sales_csv(sales: list, include_items: bool, include_payments: bool) -> str:
	"""Generate CSV export of sales data."""
	output = io.StringIO()
	writer = csv.writer(output)

	# Headers
	headers = [
		"Invoice #",
		"Customer",
		"Date",
		"Time",
		"Subtotal",
		"Tax",
		"Discount",
		"Grand Total",
		"Status",
		"Cashier",
	]

	if include_items:
		headers.extend(["Items", "Item Details"])

	if include_payments:
		headers.append("Payment Methods")

	writer.writerow(headers)

	# Batch fetch items and payments to prevent N+1 queries during export
	all_items_map = {}
	all_payments_map = {}

	if sales:
		sale_names = [
			s.dict().get("name") if hasattr(s, "dict") else getattr(s, "name", s.get("name")) for s in sales
		]

		if include_items and sale_names:
			all_items = frappe.get_all(
				"Sales Invoice Item",
				filters={"parent": ("in", sale_names)},
				fields=["parent", "item_code", "qty", "rate", "amount"],
			)
			for i in all_items:
				all_items_map.setdefault(i.parent, []).append(i)

		if include_payments and sale_names:
			all_payments = frappe.get_all(
				"Sales Invoice Payment",
				filters={"parent": ("in", sale_names)},
				fields=["parent", "mode_of_payment", "amount"],
			)
			for p in all_payments:
				all_payments_map.setdefault(p.parent, []).append(p)

	# Data
	for sale in sales:
		row = [
			sale.name,
			sale.customer,
			str(sale.posting_date),
			str(sale.posting_time),
			flt(sale.grand_total) - flt(sale.total_taxes_and_charges),
			flt(sale.total_taxes_and_charges),
			flt(sale.discount_amount),
			flt(sale.grand_total),
			sale.status,
			sale.owner,
		]

		if include_items:
			items = all_items_map.get(sale.name, [])
			item_count = len(items)
			item_details = "; ".join([f"{i.item_code} x{i.qty} @ ${i.rate}" for i in items])
			row.extend([item_count, item_details])

		if include_payments:
			payments = all_payments_map.get(sale.name, [])
			payment_str = "; ".join([f"{p.mode_of_payment}: ${flt(p.amount)}" for p in payments])
			row.append(payment_str)

		writer.writerow(row)

	# Save file
	file_name = f"sales_export_{now_datetime().strftime('%Y%m%d_%H%M%S')}.csv"
	file_path = frappe.get_site_path("public", "files", file_name)

	with open(file_path, "w") as f:  # nosemgrep (safe site-internal file export)
		f.write(output.getvalue())

	return f"/files/{file_name}"


def generate_sales_excel(sales: list, include_items: bool, include_payments: bool) -> str:
	"""Generate Excel export (falls back to CSV for simplicity)."""
	return generate_sales_csv(sales, include_items, include_payments)


@frappe.whitelist()
def export_customer_data(
	customer_group: str | None = None,
	include_transactions: bool = False,
	format: str = "csv",
) -> dict:
	"""
	Export customer data to CSV or Excel.

	Args:
		customer_group: Filter by customer group
		include_transactions: Include transaction history
		format: Export format

	Returns:
		File URL and export details
	"""
	frappe.only_for(["Sales Manager", "System Manager"])

	filters = {}
	if customer_group:
		filters["customer_group"] = customer_group

	customers = frappe.get_all(
		"Customer",
		filters=filters,
		fields=[
			"name",
			"customer_name",
			"customer_group",
			"territory",
			"email_id",
			"mobile_no",
			"creation",
		],
		limit_page_length=10000,
	)

	output = io.StringIO()
	writer = csv.writer(output)

	headers = ["Customer ID", "Name", "Group", "Territory", "Email", "Mobile", "Created"]

	if include_transactions:
		headers.extend(["Total Transactions", "Total Spent", "Last Transaction"])

	writer.writerow(headers)

	if include_transactions and customers:
		customer_names = [c.name for c in customers]
		all_stats = frappe.db.sql(  # nosemgrep
			"""
			SELECT customer, COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total, MAX(posting_date) as last_date
			FROM `tabSales Invoice`
			WHERE customer IN %s AND docstatus = 1
			GROUP BY customer
			""",
			(tuple(customer_names),),
			as_dict=True,
		)
		stats_map = {s.customer: s for s in all_stats}
	else:
		stats_map = {}

	for customer in customers:
		row = [
			customer.name,
			customer.customer_name,
			customer.customer_group,
			customer.territory,
			customer.email_id,
			customer.mobile_no,
			str(customer.creation),
		]

		if include_transactions:
			stats = stats_map.get(customer.name)
			if stats:
				row.extend([stats.count, flt(stats.total), str(stats.last_date or "")])
			else:
				row.extend([0, 0.0, ""])

		writer.writerow(row)

	file_name = f"customer_export_{now_datetime().strftime('%Y%m%d_%H%M%S')}.csv"
	file_path = frappe.get_site_path("public", "files", file_name)

	with open(file_path, "w") as f:  # nosemgrep (safe site-internal file export)
		f.write(output.getvalue())

	return {
		"success": True,
		"file_url": f"/files/{file_name}",
		"record_count": len(customers),
	}


@frappe.whitelist()
def export_inventory_data(
	warehouse: str | None = None,
	item_group: str | None = None,
	include_zero_stock: bool = True,
	format: str = "csv",
) -> dict:
	"""
	Export inventory data to CSV or Excel.

	Args:
		warehouse: Filter by warehouse
		item_group: Filter by item group
		include_zero_stock: Include items with zero stock
		format: Export format

	Returns:
		File URL and export details
	"""
	frappe.only_for(["Stock Manager", "Sales Manager", "System Manager"])

	# Build query
	query = """
		SELECT
			i.name as item_code,
			i.item_name,
			i.item_group,
			b.warehouse,
			b.actual_qty,
			b.reserved_qty,
			b.projected_qty,
			i.standard_rate,
			i.stock_uom
		FROM `tabItem` i
		LEFT JOIN `tabBin` b ON b.item_code = i.item_code
		WHERE i.is_stock_item = 1
			AND i.disabled = 0
	"""

	params = {}

	if warehouse:
		query += " AND b.warehouse = %(warehouse)s"
		params["warehouse"] = warehouse

	if item_group:
		query += " AND i.item_group = %(item_group)s"
		params["item_group"] = item_group

	if not include_zero_stock:
		query += " AND b.actual_qty > 0"

	query += " ORDER BY i.item_name"

	items = frappe.db.sql(query, params, as_dict=True)  # nosemgrep

	output = io.StringIO()
	writer = csv.writer(output)

	writer.writerow(
		[
			"Item Code",
			"Item Name",
			"Item Group",
			"Warehouse",
			"Actual Qty",
			"Reserved Qty",
			"Projected Qty",
			"Standard Rate",
			"UOM",
		]
	)

	for item in items:
		writer.writerow(
			[
				item.item_code,
				item.item_name,
				item.item_group,
				item.warehouse or "",
				flt(item.actual_qty or 0),
				flt(item.reserved_qty or 0),
				flt(item.projected_qty or 0),
				flt(item.standard_rate or 0),
				item.stock_uom,
			]
		)

	file_name = f"inventory_export_{now_datetime().strftime('%Y%m%d_%H%M%S')}.csv"
	file_path = frappe.get_site_path("public", "files", file_name)

	with open(file_path, "w") as f:  # nosemgrep (safe site-internal file export)
		f.write(output.getvalue())

	return {
		"success": True,
		"file_url": f"/files/{file_name}",
		"record_count": len(items),
	}


@frappe.whitelist()
def schedule_backup(backup_type: str = "daily") -> dict:
	"""
	Schedule a backup job.

	Args:
		backup_type: Type of backup ('daily', 'weekly', 'monthly')

	Returns:
		Scheduled job details
	"""
	frappe.only_for("System Manager")

	if frappe.db.exists("DocType", "POS Scheduled Backup"):
		backup = frappe.new_doc("POS Scheduled Backup")
		backup.backup_type = backup_type
		backup.status = "Scheduled"
		backup.scheduled_time = now_datetime()
		backup.insert()

		return {
			"success": True,
			"backup_name": backup.name,
			"message": _("{0} backup scheduled successfully.").format(backup_type.title()),
		}

	frappe.msgprint(
		_("POS Scheduled Backup DocType not found. Running standard backup instead."),
		title=_("Note"),
		indicator="blue",
	)

	from frappe.utils.backups import scheduled_backup

	backup_path = scheduled_backup(
		ignore_conf=True,
		backup_path_db=None,
		backup_path_files=None,
		backup_path_private_files=None,
	)

	return {
		"success": True,
		"backup_name": backup_path,
		"message": _("{0} backup completed (standard backup).").format(backup_type.title()),
	}
