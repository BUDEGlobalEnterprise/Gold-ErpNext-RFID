import json

import frappe
from frappe.utils import cint, cstr, flt, today

QUOTE_STATUSES = {"Draft", "Open", "Replied", "Ordered", "Lost", "Cancelled", "Expired"}


def _parse_status_filter(status):
	if not status:
		return None

	if isinstance(status, str):
		value = cstr(status).strip()
		if not value:
			return None
		if value.startswith("["):
			try:
				status = json.loads(value)
			except json.JSONDecodeError:
				frappe.throw("Invalid quotation status filter")
		else:
			if value not in QUOTE_STATUSES:
				frappe.throw("Invalid quotation status")
			return value

	if isinstance(status, (list, tuple)):
		if len(status) != 2 or status[0] != "in" or not isinstance(status[1], (list, tuple)):
			frappe.throw("Invalid quotation status filter")
		statuses = [cstr(value).strip() for value in status[1]]
		if not statuses or any(value not in QUOTE_STATUSES for value in statuses):
			frappe.throw("Invalid quotation status")
		return ["in", statuses]

	frappe.throw("Invalid quotation status filter")


@frappe.whitelist(allow_guest=False)
def get_quotations(status=None, customer=None, from_date=None, to_date=None, page=1, page_size=20):
	"""List Quotations with filters and pagination."""
	frappe.has_permission("Quotation", ptype="read", throw=True)

	filters = {"docstatus": ["!=", 2]}
	status_filter = _parse_status_filter(status)
	if status_filter:
		filters["status"] = status_filter
	if customer:
		filters["party_name"] = customer
	if from_date and to_date:
		filters["transaction_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["transaction_date"] = [">=", from_date]
	elif to_date:
		filters["transaction_date"] = ["<=", to_date]

	page = max(1, cint(page))
	page_size = min(100, max(1, cint(page_size)))
	limit_start = (page - 1) * page_size

	quotes = frappe.get_all(
		"Quotation",
		filters=filters,
		fields=[
			"name",
			"party_name",
			"customer_name",
			"transaction_date",
			"valid_till",
			"status",
			"grand_total",
			"currency",
			"docstatus",
			"order_type",
		],
		order_by="transaction_date desc",
		limit_start=limit_start,
		limit=page_size,
	)
	total = frappe.db.count("Quotation", filters)

	return {"success": True, "quotes": quotes, "total": total, "page": page, "page_size": page_size}


@frappe.whitelist(allow_guest=False)
def get_quotation_detail(name):
	"""Get detailed quotation with line items."""
	frappe.has_permission("Quotation", ptype="read", throw=True)
	name = cstr(name).strip()
	if not frappe.db.exists("Quotation", name):
		frappe.throw("Quotation not found")

	doc = frappe.get_doc("Quotation", name)
	items = []
	for row in doc.items:
		items.append(
			{
				"item_code": row.item_code,
				"item_name": row.item_name,
				"description": row.description,
				"qty": row.qty,
				"rate": row.rate,
				"amount": row.amount,
				"uom": row.uom,
			}
		)

	return {
		"success": True,
		"quote": {
			"name": doc.name,
			"party_name": doc.party_name,
			"customer_name": doc.customer_name,
			"transaction_date": str(doc.transaction_date),
			"valid_till": str(doc.valid_till) if doc.valid_till else "",
			"status": doc.status,
			"grand_total": flt(doc.grand_total),
			"net_total": flt(doc.net_total),
			"total_taxes_and_charges": flt(doc.total_taxes_and_charges),
			"currency": doc.currency,
			"docstatus": doc.docstatus,
			"order_type": doc.order_type,
			"terms": doc.terms,
			"items": items,
		},
	}


@frappe.whitelist(allow_guest=False)
def create_quotation(customer, items_json, valid_till=None, order_type="Sales"):
	"""Create a new Quotation."""
	frappe.has_permission("Quotation", ptype="create", throw=True)

	customer = cstr(customer).strip()
	if not customer:
		frappe.throw("Customer is required")

	items = json.loads(items_json) if isinstance(items_json, str) else items_json
	if not items or not isinstance(items, list):
		frappe.throw("At least one item is required")

	quotation = frappe.new_doc("Quotation")
	quotation.quotation_to = "Customer"
	quotation.party_name = customer
	quotation.transaction_date = today()
	quotation.valid_till = valid_till
	quotation.order_type = order_type

	for item in items:
		item_code = cstr(item.get("item_code", "")).strip()
		if not item_code:
			continue
		quotation.append(
			"items",
			{
				"item_code": item_code,
				"qty": max(1, flt(item.get("qty", 1))),
				"rate": flt(item.get("rate", 0)),
			},
		)

	if not quotation.items:
		frappe.throw("No valid items provided")

	quotation.insert()
	return {"success": True, "name": quotation.name, "status": quotation.status}


@frappe.whitelist(allow_guest=False)
def submit_quotation(name):
	"""Submit a draft quotation."""
	frappe.has_permission("Quotation", ptype="submit", throw=True)
	name = cstr(name).strip()
	doc = frappe.get_doc("Quotation", name)
	doc.submit()
	return {"success": True, "name": doc.name, "status": doc.status}


@frappe.whitelist(allow_guest=False)
def update_quotation_status(name, status):
	"""Set quotation status to Ordered or Lost."""
	frappe.has_permission("Quotation", ptype="write", throw=True)
	name = cstr(name).strip()
	status = cstr(status).strip()

	if status not in ("Ordered", "Lost"):
		frappe.throw("Status must be 'Ordered' or 'Lost'")

	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 1:
		frappe.throw("Quotation must be submitted first")

	doc.set_status(update=True, status=status)
	return {"success": True, "name": doc.name, "status": status}


@frappe.whitelist(allow_guest=False)
def convert_to_order(name):
	"""Convert a Quotation to a Sales Order."""
	frappe.has_permission("Quotation", ptype="write", throw=True)
	frappe.has_permission("Sales Order", ptype="create", throw=True)

	name = cstr(name).strip()
	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 1:
		frappe.throw("Quotation must be submitted before converting")

	from erpnext.selling.doctype.quotation.quotation import make_sales_order

	so = make_sales_order(name)
	so.insert()
	return {"success": True, "sales_order": so.name, "message": f"Sales Order {so.name} created"}


@frappe.whitelist(allow_guest=False)
def convert_to_invoice(name):
	"""Convert a Quotation directly to a Sales Invoice."""
	frappe.has_permission("Quotation", ptype="write", throw=True)
	frappe.has_permission("Sales Invoice", ptype="create", throw=True)

	name = cstr(name).strip()
	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 1:
		frappe.throw("Quotation must be submitted before converting")

	from erpnext.selling.doctype.quotation.quotation import make_sales_invoice

	si = make_sales_invoice(name)
	si.insert()
	return {"success": True, "sales_invoice": si.name, "message": f"Sales Invoice {si.name} created"}


@frappe.whitelist(allow_guest=False)
def cancel_quotation(name):
	"""Cancel a quotation."""
	frappe.has_permission("Quotation", ptype="cancel", throw=True)
	name = cstr(name).strip()
	doc = frappe.get_doc("Quotation", name)
	doc.cancel()
	return {"success": True, "name": doc.name, "status": "Cancelled"}
