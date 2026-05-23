"""
Repair API - Repair orders, types, and customer repair history
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import escape_html


@frappe.whitelist(allow_guest=False)
def get_repair_types(active_only: bool = True) -> list[dict[str, Any]]:
	frappe.has_permission("Repair Type", ptype="read", throw=True)

	filters = {"is_active": 1} if active_only else {}
	return frappe.get_all(
		"Repair Type",
		filters=filters,
		fields=["name", "repair_name", "category", "base_price", "estimated_days", "description"],
		order_by="category asc, repair_name asc",
	)


@frappe.whitelist(allow_guest=False)
def get_repair_orders(
	status: str | None = None,
	warehouse: str | None = None,
	search_term: str | None = None,
	start: int = 0,
	page_length: int = 20,
	customer: str | None = None,
	handled_by: str | None = None,
	priority: str | None = None,
	assigned_to: str | None = None,
	date_from: str | None = None,
	date_to: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
) -> list[dict[str, Any]]:
	frappe.has_permission("Repair Order", ptype="read", throw=True)

	date_from = date_from or from_date
	date_to = date_to or to_date

	filters = []
	if status:
		filters.append(["status", "=", status])
	if warehouse:
		filters.append(["warehouse", "=", warehouse])
	if customer:
		filters.append(["customer", "=", customer])
	if handled_by:
		filters.append(["handled_by", "=", handled_by])
	if priority:
		filters.append(["priority", "=", priority])
	if assigned_to:
		filters.append(["assigned_to", "=", assigned_to])
	if date_from:
		filters.append(["received_date", ">=", date_from])
	if date_to:
		filters.append(["received_date", "<=", f"{date_to} 23:59:59"])

	# Build search filter - search by repair #, customer name, or phone
	or_filters = None
	if search_term:
		# Also search customer names by linking to Customer table
		customer_matches = frappe.get_all(
			"Customer",
			or_filters={
				"customer_name": ("like", f"%{search_term}%"),
				"mobile_no": ("like", f"%{search_term}%"),
			},
			pluck="name",
		)
		or_filters = [
			{"name": ("like", f"%{search_term}%")},
			{"customer_phone": ("like", f"%{search_term}%")},
		]
		if customer_matches:
			or_filters.append({"customer": ("in", customer_matches)})

	orders = frappe.get_list(
		"Repair Order",
		filters=filters or None,
		or_filters=or_filters,
		fields=[
			"name",
			"creation",
			"status",
			"priority",
			"customer",
			"customer_phone",
			"customer_id_type",
			"handled_by",
			"repair_type",
			"item_description",
			"item_type",
			"item_brand",
			"serial_number",
			"item_weight",
			"stone_weight",
			"metal_type",
			"purity",
			"metal_weight_difference",
			"estimated_cost",
			"total_cost",
			"payment_status",
			"received_date",
			"promised_date",
			"completed_date",
			"delivered_date",
			"assigned_to",
			"warehouse",
			"warranty_months",
			"warranty_expiry_date",
			"is_warranty_repair",
			"original_repair_order",
		],
		order_by="modified desc",
		start=int(start),
		page_length=int(page_length),
	)

	# Enrichment
	for o in orders:
		if o.get("customer"):
			o["customer_name"] = frappe.db.get_value("Customer", o["customer"], "customer_name")
		if o.get("repair_type"):
			o["repair_type_name"] = frappe.db.get_value("Repair Type", o["repair_type"], "repair_name")
		if o.get("handled_by"):
			o["handled_by_name"] = frappe.db.get_value("User", o["handled_by"], "full_name")

	return orders


@frappe.whitelist(allow_guest=False)
def get_repair_stats(warehouse: str | None = None) -> dict[str, int]:
	frappe.has_permission("Repair Order", ptype="read", throw=True)

	filters = {}
	if warehouse:
		filters["warehouse"] = warehouse

	statuses = [
		"Received",
		"Estimated",
		"Approved",
		"In Progress",
		"Waiting for Parts",
		"Quality Check",
		"Ready for Pickup",
		"Delivered",
		"Cancelled",
	]
	counts = {}
	for s in statuses:
		counts[s] = frappe.db.count("Repair Order", filters={**filters, "status": s})
	counts["total"] = frappe.db.count("Repair Order", filters=filters)
	return counts


@frappe.whitelist(allow_guest=False)
def create_repair_order(
	customer: str,
	repair_type: str,
	item_description: str | None = None,
	customer_phone: str | None = None,
	handled_by: str | None = None,
	warehouse: str | None = None,
	customer_notes: str | None = None,
	estimated_cost: float | None = None,
	priority: str = "Medium",
	**kwargs: Any,
) -> dict[str, Any]:
	frappe.has_permission("Repair Order", ptype="create", throw=True)

	doc = frappe.new_doc("Repair Order")
	doc.customer = customer
	doc.repair_type = repair_type
	doc.status = "Received"
	doc.item_description = item_description
	doc.customer_phone = customer_phone
	doc.handled_by = handled_by or frappe.session.user
	doc.warehouse = warehouse
	doc.customer_notes = customer_notes
	doc.estimated_cost = estimated_cost
	doc.priority = priority

	for key, value in kwargs.items():
		if hasattr(doc, key):
			if isinstance(value, list):
				doc.set(key, value)
			else:
				setattr(doc, key, value)

	doc.insert()

	# Send received notification
	try:
		doc.send_status_notification()
	except Exception as e:
		frappe.log_error(f"Failed to send notification for new repair {doc.name}: {e}")

	return {"name": doc.name, "status": doc.status}


@frappe.whitelist(allow_guest=False)
def update_repair_status(name: str, status: str, work_notes: str | None = None) -> dict[str, str]:
	frappe.has_permission("Repair Order", ptype="write", doc=name, throw=True)

	doc = frappe.get_doc("Repair Order", name)
	old_status = doc.status
	doc.status = status

	if work_notes is not None:
		doc.work_notes = (doc.work_notes or "") + "\n" + work_notes if doc.work_notes else work_notes

	if status == "Delivered":
		from frappe.utils import now

		doc.delivered_date = now()

	# Set completed_date when repair work is completed (Ready for Pickup)
	if status == "Ready for Pickup" and not doc.completed_date:
		from frappe.utils import now

		doc.completed_date = now()

	doc.save()

	# Send notification on status change
	if old_status != status:
		doc.send_status_notification(old_status)

	return {"name": doc.name, "status": doc.status}


@frappe.whitelist(allow_guest=False)
def get_repair_order_details(name: str) -> dict[str, Any]:
	frappe.has_permission("Repair Order", ptype="read", doc=name, throw=True)

	doc = frappe.get_doc("Repair Order", name)
	doc_dict = doc.as_dict()

	if doc_dict.get("customer"):
		doc_dict["customer_name"] = frappe.db.get_value("Customer", doc_dict["customer"], "customer_name")
	if doc_dict.get("repair_type"):
		doc_dict["repair_type_name"] = frappe.db.get_value(
			"Repair Type", doc_dict["repair_type"], "repair_name"
		)
	if doc_dict.get("handled_by"):
		doc_dict["handled_by_name"] = frappe.db.get_value("User", doc_dict["handled_by"], "full_name")

	# Keep a stable alias for older POS codepaths that still read `description`.
	doc_dict["description"] = doc.item_description
	doc_dict["item_description"] = doc.item_description

	# Include jewelry-specific fields
	doc_dict["item_type"] = doc.item_type
	doc_dict["item_brand"] = doc.item_brand
	doc_dict["serial_number"] = doc.serial_number
	doc_dict["item_condition"] = doc.item_condition
	doc_dict["item_weight"] = doc.item_weight
	doc_dict["stone_weight"] = doc.stone_weight
	doc_dict["metal_type"] = doc.metal_type
	doc_dict["purity"] = doc.purity
	doc_dict["metal_weight_in"] = doc.metal_weight_in
	doc_dict["metal_weight_out"] = doc.metal_weight_out
	doc_dict["metal_weight_difference"] = doc.metal_weight_difference
	doc_dict["estimated_weight_before"] = doc.estimated_weight_before
	doc_dict["estimated_weight_after"] = doc.estimated_weight_after

	# Include warranty fields
	doc_dict["warranty_months"] = doc.warranty_months
	doc_dict["warranty_expiry_date"] = str(doc.warranty_expiry_date) if doc.warranty_expiry_date else None
	doc_dict["warranty_terms"] = doc.warranty_terms
	doc_dict["original_repair_order"] = doc.original_repair_order
	doc_dict["is_warranty_repair"] = doc.is_warranty_repair
	doc_dict["warranty_claim_type"] = doc.warranty_claim_type

	return doc_dict


@frappe.whitelist()
def get_customer_repair_history(customer: str, limit: int = 20) -> list[dict[str, Any]]:
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions to access Repair History"), frappe.PermissionError)

	orders = frappe.get_all(
		"Repair Order",
		filters={"customer": customer},
		fields=[
			"name",
			"status",
			"repair_type",
			"item_description",
			"total_cost",
			"received_date",
			"delivered_date",
		],
		order_by="received_date desc",
		limit=int(limit),
	)
	for o in orders:
		if o.get("repair_type"):
			o["repair_type_name"] = frappe.db.get_value("Repair Type", o["repair_type"], "repair_name")
	return orders


@frappe.whitelist()
def get_repair_receipt_html(name: str) -> str:
	"""Return HTML for repair claim ticket / receipt (for print)."""
	if not frappe.has_permission("Repair Order", "read", doc=name):
		frappe.throw(_("Insufficient permissions to view receipt"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", name)
	d = doc.as_dict()
	d["customer_name"] = (
		frappe.db.get_value("Customer", doc.customer, "customer_name") if doc.customer else ""
	)
	d["repair_type_name"] = (
		frappe.db.get_value("Repair Type", doc.repair_type, "repair_name") if doc.repair_type else ""
	)
	d["handled_by_name"] = frappe.db.get_value("User", doc.handled_by, "full_name") if doc.handled_by else ""

	# Escape all user-provided fields to prevent XSS
	safe = {k: escape_html(str(v)) if v else "" for k, v in d.items()}

	html = f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Repair Receipt - {safe.get("name")}</title>
<style>
body {{ font-family: sans-serif; max-width: 400px; margin: 20px auto; padding: 16px; }}
h1 {{ font-size: 18px; border-bottom: 2px solid #333; padding-bottom: 8px; }}
table {{ width: 100%; border-collapse: collapse; }}
td {{ padding: 4px 0; }}
.label {{ font-weight: bold; color: #555; }}
</style></head><body>
<h1>ZEVAR JEWELERS - REPAIR CLAIM TICKET</h1>
<p><span class="label">Repair #:</span> {safe.get("name")}</p>
<p><span class="label">Date:</span> {safe.get("received_date")}</p>
<p><span class="label">Customer:</span> {safe.get("customer_name")}</p>
<p><span class="label">Phone:</span> {safe.get("customer_phone") or "-"}</p>
<p><span class="label">Repair Type:</span> {safe.get("repair_type_name")}</p>
<p><span class="label">Item:</span> {safe.get("item_description") or "-"}</p>
<p><span class="label">Estimated Cost:</span> ${float(d.get("estimated_cost") or 0):.2f}</p>
<p><span class="label">Handled By:</span> {safe.get("handled_by_name") or "-"}</p>
<p style="margin-top: 24px; font-size: 12px; color: #666;">Keep this ticket to pick up your item.</p>
</body></html>
"""
	return html


@frappe.whitelist()
def initiate_store_transfer(repair_order: str) -> dict[str, Any]:
	"""Initiate store-to-store transfer for a repair order"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.initiate_store_transfer()
	return result


@frappe.whitelist()
def confirm_store_receipt(repair_order: str) -> dict[str, Any]:
	"""Confirm receipt of repair item at destination store"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.confirm_store_receipt()
	return result


@frappe.whitelist()
def get_multi_store_stats() -> list[dict[str, Any]]:
	"""Get repair statistics across all stores for manager dashboard"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions to access Repair Stats"), frappe.PermissionError)

	# Get all warehouses
	warehouses = frappe.get_all("Warehouse", fields=["name", "warehouse_name"], filters={"is_group": 0})

	stats = []
	for wh in warehouses:
		# Get counts by status for this warehouse
		statuses = [
			"Received",
			"In Progress",
			"Waiting for Parts",
			"Ready for Pickup",
			"Delivered",
		]

		store_stat = {
			"warehouse": wh.name,
			"warehouse_name": wh.warehouse_name or wh.name,
			"status_counts": {},
			"total_active": 0,
		}

		for status in statuses:
			count = frappe.db.count(
				"Repair Order",
				filters={"receiving_store": wh.name, "status": status},
			)
			store_stat["status_counts"][status] = count
			if status not in ["Delivered", "Cancelled"]:
				store_stat["total_active"] += count

		# Get pending transfers count
		pending_transfers = frappe.db.count(
			"Repair Order",
			filters={
				"repair_store": wh.name,
				"store_transfer_status": ["in", ["Pending", "In Transit"]],
			},
		)
		store_stat["pending_incoming_transfers"] = pending_transfers

		stats.append(store_stat)

	return stats


@frappe.whitelist()
def get_store_transfers(
	status: str | None = None,
	warehouse: str | None = None,
) -> list[dict[str, Any]]:
	"""Get list of repair orders with active store transfers"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions to access Repair Orders"), frappe.PermissionError)

	filters = [
		["store_transfer_status", "in", ["Pending", "In Transit"]],
	]

	if status:
		filters.append(["store_transfer_status", "=", status])
	if warehouse:
		filters.append(
			["repair_store", "=", warehouse],
		)

	transfers = frappe.get_list(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"status",
			"customer",
			"repair_type",
			"receiving_store",
			"repair_store",
			"store_transfer_status",
			"received_date",
			"promised_date",
		],
		order_by="received_date desc",
	)

	# Enrich with customer and repair type names
	for t in transfers:
		if t.get("customer"):
			t["customer_name"] = frappe.db.get_value("Customer", t["customer"], "customer_name")
		if t.get("repair_type"):
			t["repair_type_name"] = frappe.db.get_value("Repair Type", t["repair_type"], "repair_name")

	return transfers


@frappe.whitelist()
def log_manual_communication(
	repair_order: str,
	comm_type: str,
	direction: str,
	content: str,
	sent_via: str | None = None,
	subject: str | None = None,
) -> dict[str, Any]:
	"""Log a manual communication entry (phone call, in-person, etc.)"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	comm = doc.log_manual_communication(comm_type, direction, content, sent_via, subject)

	return {
		"success": True,
		"communication": comm.as_dict() if comm else None,
	}


@frappe.whitelist()
def get_communications(
	repair_order: str,
) -> list[dict[str, Any]]:
	"""Get all communications for a repair order"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions to access Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	if not doc.communications:
		return []

	communications = []
	for comm in doc.communications:
		comm_dict = comm.as_dict()
		if comm_dict.get("user"):
			comm_dict["user_name"] = frappe.db.get_value("User", comm.user, "full_name")
		communications.append(comm_dict)

	return communications


@frappe.whitelist()
def send_manual_notification(
	repair_order: str,
	notification_type: str,
	message: str | None = None,
) -> dict[str, Any]:
	"""Manually trigger a notification for a repair order"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)

	notification_map = {
		"Received": doc._send_received_notification,
		"Estimated": doc._send_estimate_notification,
		"Approved": doc._send_approved_notification,
		"In Progress": doc._send_in_progress_notification,
		"Waiting for Parts": doc._send_waiting_parts_notification,
		"Ready for Pickup": doc._send_ready_pickup_notification,
		"Delivered": doc._send_delivered_notification,
		"Overdue": doc._send_overdue_notification,
	}

	if notification_type not in notification_map:
		frappe.throw(_("Invalid notification type"), frappe.ValidationError)

	notification_map[notification_type]()

	return {
		"success": True,
		"message": f"{notification_type} notification sent",
	}


@frappe.whitelist()
def approve_estimate(
	repair_order: str, approved_by: str | None = None, approval_notes: str | None = None
) -> dict[str, Any]:
	"""Approve a repair estimate"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.approve_estimate(approved_by or "Customer", approval_notes)

	return result


@frappe.whitelist()
def reject_estimate(repair_order: str, reason: str | None = None) -> dict[str, Any]:
	"""Reject a repair estimate"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.reject_estimate("Customer", reason)

	return result


@frappe.whitelist()
def send_for_approval(repair_order: str) -> dict[str, Any]:
	"""Send estimate to customer for approval"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.send_for_approval()

	return result


@frappe.whitelist()
def revise_estimate(
	repair_order: str, new_total_cost: float, revision_notes: str | None = None
) -> dict[str, Any]:
	"""Revise an estimate with new cost"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.revise_estimate(new_total_cost, revision_notes)

	return result


@frappe.whitelist()
def get_estimate_pdf(repair_order: str) -> dict[str, Any]:
	"""Generate and return PDF for estimate"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions to access Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.generate_estimate_pdf()

	return result


@frappe.whitelist(allow_guest=True)  # nosemgrep
def public_estimate_approval(
	token: str, action: str, customer_name: str, notes: str | None = None
) -> dict[str, Any]:
	"""Public endpoint for customers to approve/reject estimates via email link"""

	# Verify token from cache
	cache_key = f"estimate_approval_{token}"
	cached_data = frappe.cache().get_value(cache_key)

	if not cached_data:
		return {"success": False, "message": "Invalid or expired approval link"}

	repair_order_name = cached_data.get("repair_order")
	if not repair_order_name:
		return {"success": False, "message": "Invalid approval link"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order_name)

		if action == "approve":
			result = doc.approve_estimate(customer_name, notes)
		elif action == "reject":
			if not notes:
				return {"success": False, "message": "Please provide a reason for rejection"}
			result = doc.reject_estimate(customer_name, notes)
		else:
			return {"success": False, "message": "Invalid action"}

		# Clear the token after use
		frappe.cache().delete_value(cache_key)

		return result

	except Exception as e:
		frappe.log_error(f"Public estimate approval failed: {e}")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def get_estimate_details_for_approval(token: str) -> dict[str, Any]:
	"""Public endpoint to get estimate details for approval page"""

	# Verify token from cache
	cache_key = f"estimate_approval_{token}"
	cached_data = frappe.cache().get_value(cache_key)

	if not cached_data:
		return {"success": False, "message": "Invalid or expired approval link"}

	repair_order_name = cached_data.get("repair_order")
	if not repair_order_name:
		return {"success": False, "message": "Invalid approval link"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order_name)

		# Check if estimate is still valid
		validity_check = doc.check_estimate_validity()
		if not validity_check["valid"]:
			return {"success": False, "message": validity_check["message"]}

		# Get details
		details = {
			"success": True,
			"repair_number": doc.name,
			"customer": doc.customer,
			"customer_name": frappe.db.get_value("Customer", doc.customer, "customer_name")
			if doc.customer
			else "",
			"repair_type": doc.repair_type,
			"repair_type_name": frappe.db.get_value("Repair Type", doc.repair_type, "repair_name")
			if doc.repair_type
			else "",
			"item_description": doc.item_description,
			"labor_cost": float(doc.labor_cost or 0),
			"material_cost": float(doc.material_cost or 0),
			"total_cost": float(doc.total_cost or 0),
			"promised_date": str(doc.promised_date) if doc.promised_date else "",
			"estimate_sent_date": str(doc.estimate_sent_date) if doc.estimate_sent_date else "",
			"estimate_valid_until": str(doc.estimate_valid_until) if doc.estimate_valid_until else "",
			"estimate_notes": doc.estimate_notes,
		}

		return details

	except Exception as e:
		frappe.log_error(f"Failed to get estimate details: {e}")
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def create_repair_invoice(repair_order: str) -> dict[str, Any]:
	"""Create Sales Invoice from Repair Order"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.create_sales_invoice()

	return result


@frappe.whitelist()
def add_repair_payment(
	repair_order: str,
	amount: float,
	payment_method: str,
	payment_date: str | None = None,
	reference: str | None = None,
	notes: str | None = None,
) -> dict[str, Any]:
	"""Add a payment to a repair order"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions to update Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.add_payment(amount, payment_method, payment_date, reference, notes)

	return result


@frappe.whitelist()
def get_payment_summary(repair_order: str) -> dict[str, Any]:
	"""Get payment summary for a repair order"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions to access Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)

	return {
		"repair_order": doc.name,
		"total_cost": float(doc.total_cost or 0),
		"deposit_amount": float(doc.deposit_amount or 0),
		"deposit_date": str(doc.deposit_date) if doc.deposit_date else None,
		"deposit_payment_method": doc.deposit_payment_method,
		"total_payments": doc.get_total_payments(),
		"total_paid": doc.get_total_paid(),
		"balance_due": float(doc.balance_due or 0),
		"payment_status": doc.payment_status,
		"sales_invoice": doc.sales_invoice,
		"payments": [
			{
				"payment_date": str(p.payment_date),
				"amount": float(p.amount or 0),
				"payment_method": p.payment_method,
				"reference": p.reference,
				"received_by": p.received_by,
				"notes": p.notes,
			}
			for p in (doc.payments or [])
		],
	}


@frappe.whitelist()
def check_warranty_status(repair_order: str) -> dict[str, Any]:
	"""Check warranty status for a repair order"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions to access Repair Order"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)

	from frappe.utils import getdate, today

	result = {
		"repair_order": doc.name,
		"has_warranty": bool(doc.warranty_months and doc.warranty_months > 0),
		"warranty_months": doc.warranty_months or 0,
		"warranty_expiry_date": str(doc.warranty_expiry_date) if doc.warranty_expiry_date else None,
		"warranty_terms": doc.warranty_terms or "",
		"is_valid": False,
		"days_remaining": 0,
		"message": "",
	}

	if not result["has_warranty"]:
		result["message"] = "This repair has no warranty"
		return result

	if not doc.warranty_expiry_date:
		result["message"] = "Warranty expiry date not set"
		return result

	if doc.status != "Delivered":
		result["message"] = f"Warranty will start when repair is delivered (current status: {doc.status})"
		return result

	today_date = getdate(today())
	expiry_date = getdate(doc.warranty_expiry_date)

	if today_date > expiry_date:
		result["message"] = f"Warranty expired on {doc.warranty_expiry_date}"
	else:
		result["is_valid"] = True
		result["days_remaining"] = (expiry_date - today_date).days
		result["message"] = (
			f"Warranty valid until {doc.warranty_expiry_date} ({result['days_remaining']} days remaining)"
		)

	return result


@frappe.whitelist()
def get_warranty_repairs(original_repair_order: str) -> list[dict[str, Any]]:
	"""Get all warranty/re-repair orders linked to an original repair"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions to access Repair Orders"), frappe.PermissionError)

	repairs = frappe.get_all(
		"Repair Order",
		filters={"original_repair_order": original_repair_order},
		fields=[
			"name",
			"status",
			"is_warranty_repair",
			"warranty_claim_type",
			"received_date",
			"total_cost",
			"delivered_date",
		],
		order_by="received_date desc",
	)

	return repairs


@frappe.whitelist()
def get_customer_warranties(customer: str, active_only: bool = True) -> list[dict[str, Any]]:
	"""Get all active warranties for a customer"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions to access Repair Orders"), frappe.PermissionError)

	from frappe.utils import getdate, today

	filters = {
		"customer": customer,
		"status": "Delivered",
	}

	if active_only:
		filters["warranty_months"] = [">", 0]

	repairs = frappe.get_all(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"repair_type",
			"item_description",
			"delivered_date",
			"warranty_months",
			"warranty_expiry_date",
			"warranty_terms",
		],
		order_by="delivered_date desc",
	)

	# Filter for active warranties and calculate days remaining
	active_warranties = []
	for repair in repairs:
		if repair.get("warranty_expiry_date"):
			expiry_date = getdate(repair["warranty_expiry_date"])
			today_date = getdate(today())

			if not active_only or today_date <= expiry_date:
				repair["is_valid"] = today_date <= expiry_date
				repair["days_remaining"] = max(0, (expiry_date - today_date).days)
				active_warranties.append(repair)

	return active_warranties


@frappe.whitelist()
def get_dashboard_stats(warehouse: str | None = None) -> dict[str, Any]:
	"""Get repair dashboard statistics for POS terminal"""
	from .repair_dashboard import get_repair_dashboard_stats

	return get_repair_dashboard_stats(warehouse)


@frappe.whitelist()
def get_chart_data(warehouse: str | None = None, period: int = 30) -> dict[str, Any]:
	"""Get repair chart data for dashboard visualization"""
	from .repair_dashboard import get_repair_chart_data

	return get_repair_chart_data(warehouse, period)


@frappe.whitelist()
def get_thermal_receipt_html(name: str) -> str:
	"""Return HTML for 80mm thermal printer receipt"""
	if not frappe.has_permission("Repair Order", "read", doc=name):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", name)
	d = doc.as_dict()

	# Get customer details
	d["customer_name"] = (
		frappe.db.get_value("Customer", doc.customer, "customer_name") if doc.customer else ""
	)
	d["repair_type_name"] = (
		frappe.db.get_value("Repair Type", doc.repair_type, "repair_name") if doc.repair_type else ""
	)
	d["warehouse_name"] = (
		frappe.db.get_value("Warehouse", doc.warehouse, "warehouse_name") if doc.warehouse else ""
	)

	# Escape user-provided fields
	safe = {k: escape_html(str(v)) if v else "" for k, v in d.items()}

	html = f"""
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="utf-8">
		<title>Repair Receipt - {safe.get("name")}</title>
		<style>
		@page {{ margin: 0; padding: 0; }}
		body {{ font-family: 'Courier New', monospace; font-size: 12px; margin: 0; padding: 10px; width: 80mm; }}
		.center {{ text-align: center; }}
		.right {{ text-align: right; }}
		.bold {{ font-weight: bold; }}
		.divider {{ border-top: 1px dashed #000; margin: 8px 0; }}
		.section {{ margin-bottom: 8px; }}
		.label {{ color: #666; }}
		.footer {{ font-size: 10px; text-align: center; margin-top: 15px; color: #666; }}
		</style>
	</head>
	<body>
		<div class="center bold">
			<h2 style="margin: 0;">ZEVAR JEWELERS</h2>
			<p style="margin: 5px 0;">{safe.get("warehouse_name")}</p>
		</div>

		<div class="divider"></div>

		<div class="center bold">
			<p style="margin: 0; font-size: 16px;">REPAIR CLAIM TICKET</p>
		</div>

		<div class="divider"></div>

		<div class="section">
			<p class="bold" style="margin: 0;">Repair #: {safe.get("name")}</p>
			<p style="margin: 3px 0;" class="label">Date: {safe.get("received_date")}</p>
			<p style="margin: 3px 0;" class="label">Status: {safe.get("status")}</p>
		</div>

		<div class="divider"></div>

		<div class="section">
			<p class="bold" style="margin: 0;">{safe.get("customer_name")}</p>
			<p style="margin: 3px 0;" class="label">{safe.get("customer_phone") or ""}</p>
		</div>

		<div class="divider"></div>

		<div class="section">
			<p class="bold" style="margin: 0;">{safe.get("repair_type_name")}</p>
			<p style="margin: 3px 0;" class="label">{safe.get("item_description") or "N/A"}</p>
		</div>

		<div class="divider"></div>

		<div class="section">
			<table style="width: 100%; border-collapse: collapse;">
				<tr>
					<td class="label">Est. Cost:</td>
					<td class="right bold">${float(safe.get("estimated_cost") or 0):.2f}</td>
				</tr>
				<tr>
					<td class="label">Deposit:</td>
					<td class="right">${float(safe.get("deposit_amount") or 0):.2f}</td>
				</tr>
				<tr>
					<td class="label">Balance Due:</td>
					<td class="right bold">${float(safe.get("balance_due") or 0):.2f}</td>
				</tr>
			</table>
		</div>

		<div class="divider"></div>

		<div class="section">
			<p class="label" style="margin: 0;">Promised Date: {safe.get("promised_date") or "TBD"}</p>
		</div>

		<div class="divider"></div>

		<div class="center">
			<p style="margin: 0; font-size: 14px; letter-spacing: 2px;">SCAN TO CHECK STATUS</p>
		</div>

		<div class="center">
			<!-- QR Code Placeholder -->
			<div style="width: 100px; height: 100px; margin: 10px auto; border: 1px solid #ccc; display: flex; align-items: center; justify-content: center; font-size: 10px;">
				QR CODE
			</div>
			<p style="margin: 5px 0; font-size: 10px;">{safe.get("name")}</p>
		</div>

		<div class="divider"></div>

		<div class="footer">
			<p style="margin: 0;">Keep this ticket for pickup</p>
			<p style="margin: 3px 0;">Questions? Call our store</p>
		</div>
	</body>
	</html>
	"""
	return html


@frappe.whitelist()
def attach_repair_photo(
	repair_order: str,
	photo_data: str,
	photo_type: str = "before",
) -> dict[str, Any]:
	"""Attach a captured photo to a repair order.

	This currently stores the latest captured image as the primary item photo so
	the richer POS repair UI can complete its flow without failing on a missing
	endpoint.
	"""
	frappe.has_permission("Repair Order", ptype="write", doc=repair_order, throw=True)

	if not photo_data:
		frappe.throw(_("Photo data is required"), frappe.ValidationError)

	doc = frappe.get_doc("Repair Order", repair_order)
	doc.item_photo = photo_data
	doc.save()

	return {
		"success": True,
		"repair_order": doc.name,
		"photo_type": photo_type,
		"item_photo": doc.item_photo,
	}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def lookup_repair_by_number(repair_number: str) -> dict[str, Any] | None:
	"""Public lookup for repair by number (customer-facing)"""
	repair_number = repair_number.strip().upper()

	try:
		doc = frappe.get_doc("Repair Order", repair_number)
	except frappe.DoesNotExistError:
		return None

	if not doc.published:
		# Only show published repairs to public
		return None

	return {
		"name": doc.name,
		"status": doc.status,
		"repair_type": doc.repair_type,
		"repair_type_name": frappe.db.get_value("Repair Type", doc.repair_type, "repair_name")
		if doc.repair_type
		else "",
		"item_type": doc.item_type,
		"item_description": doc.item_description,
		"estimated_cost": float(doc.estimated_cost or 0),
		"total_cost": float(doc.total_cost or 0),
		"deposit_amount": float(doc.deposit_amount or 0),
		"balance_due": float(doc.balance_due or 0),
		"received_date": str(doc.received_date) if doc.received_date else None,
		"promised_date": str(doc.promised_date) if doc.promised_date else None,
		"delivered_date": str(doc.delivered_date) if doc.delivered_date else None,
		"estimate_status": doc.estimate_status,
		"estimate_token": frappe.utils.generate_hash(doc.name),  # Simple token for estimate approval
	}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def lookup_repair_by_phone(phone: str) -> list[dict[str, Any]] | None:
	"""Public lookup for repairs by phone number (returns most recent)"""
	phone = phone.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")

	if not phone or len(phone) < 3:
		return None

	# Search by phone number
	repairs = frappe.get_all(
		"Repair Order",
		filters={"customer_phone": ("like", f"%{phone}%")},
		fields=[
			"name",
			"status",
			"customer",
			"received_date",
			"promised_date",
			"repair_type",
			"estimated_cost",
			"balance_due",
			"estimate_status",
		],
		order_by="received_date desc",
		limit=5,
	)

	if not repairs:
		return None

	# Enrich with details
	result = []
	for r in repairs:
		r["customer_name"] = (
			frappe.db.get_value("Customer", r["customer"], "customer_name") if r.get("customer") else ""
		)
		r["repair_type_name"] = (
			frappe.db.get_value("Repair Type", r["repair_type"], "repair_name")
			if r.get("repair_type")
			else ""
		)
		result.append(r)

	return result


# ====================
# Compliance & Security API (Phase 10)
# ====================


@frappe.whitelist()
def verify_customer_id(
	repair_order: str,
	id_type: str,
	id_number: str,
	id_state: str | None = None,
) -> dict[str, Any]:
	"""Verify customer identification for JVC compliance"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.verify_customer_id(id_type, id_number, id_state)

	return result


@frappe.whitelist()
def sign_intake_checklist(
	repair_order: str,
	signature_data: str,
) -> dict[str, Any]:
	"""Sign the intake checklist with customer signature"""
	if not frappe.has_permission("Repair Order", "write", doc=repair_order):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	result = doc.sign_intake_checklist(signature_data)

	return result


@frappe.whitelist()
def get_compliance_summary(repair_order: str) -> dict[str, Any]:
	"""Get compliance status summary for a repair order"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	return doc.get_compliance_summary()


@frappe.whitelist()
def get_audit_trail(repair_order: str, limit: int = 100) -> dict[str, Any]:
	"""Get comprehensive audit trail for a repair order"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	return doc.get_audit_trail(limit=int(limit))


@frappe.whitelist()
def get_compliance_report(repair_order: str) -> dict[str, Any]:
	"""Generate comprehensive compliance report for a repair order"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)
	return doc.get_compliance_report()


@frappe.whitelist()
def get_compliance_dashboard(
	warehouse: str | None = None,
	start_date: str | None = None,
	end_date: str | None = None,
) -> dict[str, Any]:
	"""Get compliance dashboard statistics for management"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	from frappe.utils import getdate

	# Build filters
	filters = {}
	if warehouse:
		filters["warehouse"] = warehouse
	if start_date:
		filters["received_date"] = [">=", getdate(start_date)]
	if end_date:
		if "received_date" in filters:
			filters["received_date"].append("<=", getdate(end_date))
		else:
			filters["received_date"] = ["<=", getdate(end_date)]

	# Get all repair orders in scope
	repairs = frappe.get_all(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"customer_id_verified",
			"intake_checklist_signed",
			"gemstone_disclosure",
			"precious_metals_disclosure",
			"received_date",
			"status",
			"warranty_months",
		],
	)

	# Calculate compliance metrics
	total_repairs = len(repairs)
	id_verified_count = sum(1 for r in repairs if r.get("id_verified_by"))
	intake_signed_count = sum(1 for r in repairs if r.get("intake_checklist_signed"))
	has_gemstone_disclosure = sum(1 for r in repairs if r.get("gemstone_disclosure"))
	has_metals_disclosure = sum(1 for r in repairs if r.get("precious_metals_disclosure"))

	# Get recent audit events
	from frappe.model.version import get_versions

	audit_summary = {
		"total_repairs": total_repairs,
		"id_verified_count": id_verified_count,
		"id_verified_percentage": round(
			(id_verified_count / total_repairs * 100) if total_repairs > 0 else 0, 2
		),
		"intake_signed_count": intake_signed_count,
		"intake_signed_percentage": round(
			(intake_signed_count / total_repairs * 100) if total_repairs > 0 else 0, 2
		),
		"gemstone_disclosure_count": has_gemstone_disclosure,
		"metals_disclosure_count": has_metals_disclosure,
		"compliance_score": 0,
	}

	# Calculate overall compliance score
	checkpoints = [
		audit_summary["id_verified_percentage"],
		audit_summary["intake_signed_percentage"],
	]
	audit_summary["compliance_score"] = round(sum(checkpoints) / len(checkpoints), 2) if checkpoints else 0

	# Get non-compliant repairs
	non_compliant = frappe.get_all(
		"Repair Order",
		filters={**filters, "customer_id_type": ("=", "")},
		fields=["name", "customer", "received_date", "status"],
		limit=20,
	)

	audit_summary["non_compliant_repairs"] = non_compliant
	audit_summary["non_compliant_count"] = len(non_compliant)

	return audit_summary
