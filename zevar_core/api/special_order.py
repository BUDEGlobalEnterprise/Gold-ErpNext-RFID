"""
Special Order API - CRUD, deposit, fulfillment, and pickup workflow

Provides endpoints for:
- Creating special orders from POS
- Recording deposit payments
- Marking items received from vendor
- Sending arrival notifications
- Creating pickup invoices
- Listing/searching orders
"""

import json

import frappe
from frappe import _
from frappe.utils import cint, flt


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@frappe.whitelist()
def create_special_order(
	customer: str,
	items_json: str,
	expected_delivery_date: str | None = None,
	deposit_amount: float = 0,
	supplier: str | None = None,
	store_location: str | None = None,
	sales_person: str | None = None,
	notes: str | None = None,
) -> dict:
	frappe.has_permission("Special Order", ptype="create", throw=True)

	items = json.loads(items_json)
	doc = frappe.new_doc("Special Order")
	doc.customer = customer
	doc.expected_delivery_date = expected_delivery_date
	doc.deposit_amount = flt(deposit_amount)
	doc.supplier = supplier
	doc.store_location = store_location
	doc.sales_person = sales_person
	doc.notes = notes

	for item in items:
		doc.append(
			"items",
			{
				"item_code": item["item_code"],
				"qty": cint(item.get("qty", 1)),
				"rate": flt(item.get("rate", 0)),
				"vendor_item_code": item.get("vendor_item_code"),
				"description": item.get("description"),
			},
		)

	doc.insert()
	return {"success": True, "name": doc.name, "status": doc.status, "total_amount": doc.total_amount}


@frappe.whitelist()
def get_special_order(order_name: str) -> dict:
	frappe.has_permission("Special Order", ptype="read", throw=True)
	doc = frappe.get_doc("Special Order", order_name)
	return {
		"name": doc.name,
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"order_date": doc.order_date,
		"expected_delivery_date": doc.expected_delivery_date,
		"status": doc.status,
		"total_amount": doc.total_amount,
		"deposit_amount": doc.deposit_amount,
		"deposit_paid": doc.deposit_paid,
		"balance_due": doc.balance_due,
		"supplier": doc.supplier,
		"store_location": doc.store_location,
		"sales_person": doc.sales_person,
		"tracking_number": doc.tracking_number,
		"items": [
			{
				"name": i.name,
				"item_code": i.item_code,
				"item_name": i.item_name,
				"qty": i.qty,
				"qty_filled": i.qty_filled,
				"rate": i.rate,
				"amount": i.amount,
				"vendor_item_code": i.vendor_item_code,
			}
			for i in doc.items
		],
	}


@frappe.whitelist()
def get_special_orders(
	status: str | None = None,
	customer: str | None = None,
	page: int = 1,
	page_size: int = 20,
) -> dict:
	frappe.has_permission("Special Order", ptype="read", throw=True)

	filters = {"docstatus": ["!=", 2]}
	if status:
		filters["status"] = status
	if customer:
		filters["customer"] = customer

	orders = frappe.get_all(
		"Special Order",
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_name",
			"order_date",
			"expected_delivery_date",
			"status",
			"total_amount",
			"deposit_paid",
			"balance_due",
			"supplier",
		],
		order_by="order_date desc",
		limit_page_length=cint(page_size),
		limit_start=(cint(page) - 1) * cint(page_size),
	)

	total = frappe.db.count("Special Order", filters=filters)

	return {
		"orders": orders,
		"page": cint(page),
		"page_size": cint(page_size),
		"total": total,
	}


# ---------------------------------------------------------------------------
# Lifecycle actions
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["POST"])
def record_deposit(order_name: str, amount: float, mode_of_payment: str = "Cash") -> dict:
	frappe.has_permission("Special Order", ptype="write", throw=True)
	doc = frappe.get_doc("Special Order", order_name)
	if doc.docstatus != 1:
		frappe.throw(_("Order must be submitted before recording deposits."))
	doc.record_deposit(flt(amount), mode_of_payment)
	return {"success": True, "status": doc.status, "deposit_paid": doc.deposit_paid, "balance_due": doc.balance_due}


@frappe.whitelist(methods=["POST"])
def mark_received(order_name: str, received_items_json: str) -> dict:
	frappe.has_permission("Special Order", ptype="write", throw=True)
	doc = frappe.get_doc("Special Order", order_name)
	if doc.docstatus != 1:
		frappe.throw(_("Order must be submitted before marking received."))
	received_items = json.loads(received_items_json)
	doc.mark_received(received_items)
	return {
		"success": True,
		"status": doc.status,
		"qty_ordered": doc.qty_ordered,
		"qty_received": doc.qty_received,
	}


@frappe.whitelist(methods=["POST"])
def send_arrival_notification(order_name: str) -> dict:
	frappe.has_permission("Special Order", ptype="write", throw=True)
	doc = frappe.get_doc("Special Order", order_name)
	if doc.status not in ("Received at Store", "Partially Received"):
		frappe.throw(_("Order must be received before sending notification."))
	doc.send_arrival_notification()
	return {"success": True, "status": doc.status}


@frappe.whitelist(methods=["POST"])
def mark_picked_up(order_name: str) -> dict:
	frappe.has_permission("Special Order", ptype="write", throw=True)
	doc = frappe.get_doc("Special Order", order_name)
	doc.mark_picked_up()
	return {"success": True, "status": doc.status}


@frappe.whitelist(methods=["POST"])
def close_order(order_name: str) -> dict:
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])
	doc = frappe.get_doc("Special Order", order_name)
	doc.close_order()
	return {"success": True, "status": doc.status}


# ---------------------------------------------------------------------------
# Pickup Invoice
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["POST"])
def create_pickup_invoice(order_name: str) -> dict:
	frappe.has_permission("Sales Invoice", ptype="create", throw=True)
	order = frappe.get_doc("Special Order", order_name)
	if order.status not in ("Customer Notified", "Received at Store", "Partially Received"):
		frappe.throw(_("Order must be received before creating pickup invoice."))

	invoice = frappe.new_doc("Sales Invoice")
	invoice.customer = order.customer
	invoice.is_pos = 1

	for item in order.items:
		invoice.append(
			"items",
			{
				"item_code": item.item_code,
				"qty": item.qty_filled or item.qty,
				"rate": item.rate,
			},
		)

	invoice.insert()
	return {"success": True, "invoice": invoice.name}


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_special_order_stats() -> dict:
	frappe.has_permission("Special Order", ptype="read", throw=True)
	statuses = [
		"Pending Deposit",
		"Ordered from Vendor",
		"Partially Received",
		"Received at Store",
		"Customer Notified",
		"Picked Up",
	]
	stats = {}
	for s in statuses:
		stats[s] = frappe.db.count("Special Order", {"status": s, "docstatus": 1})

	stats["overdue"] = frappe.db.count(
		"Special Order",
		{
			"docstatus": 1,
			"expected_delivery_date": ["<", frappe.utils.today()],
			"status": ["not in", ["Picked Up", "Closed", "Cancelled"]],
		},
	)
	return stats
