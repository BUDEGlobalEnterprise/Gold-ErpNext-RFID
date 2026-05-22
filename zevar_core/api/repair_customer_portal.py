import secrets

"""
Customer Portal API - Repair System Integration (Phase 11.1)

This module provides public-facing API endpoints for customers to:
- View repair status
- Upload reference photos
- Approve/reject estimates
- View repair history
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import add_to_date, cint, get_url, getdate, now, nowdate, random_string


@frappe.whitelist(allow_guest=True)  # nosemgrep
def customer_lookup(identifier: str, identifier_type: str = "phone") -> dict[str, Any]:
	"""
	Look up customer by phone number or email.

	Returns customer information and a session token for accessing their repairs.
	This is a simplified auth mechanism for customer portal access.
	"""
	if not identifier:
		return {"success": False, "message": "Phone number or email is required"}

	identifier = identifier.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")

	if len(identifier) < 3:
		return {"success": False, "message": "Invalid identifier"}

	# Search for customer by phone or email
	if identifier_type == "email":
		customer = frappe.db.get_value("Customer", {"email_id": ("like", f"%{identifier}%")}, "name")
	else:  # phone
		# Try multiple phone fields
		customer = frappe.db.get_value("Customer", {"phone": ("like", f"%{identifier}%")}, "name")
		if not customer:
			customer = frappe.db.get_value("Customer", {"mobile_no": ("like", f"%{identifier}%")}, "name")

	if not customer:
		return {"success": False, "message": "Customer not found"}

	# Get customer details
	customer_doc = frappe.get_doc("Customer", customer)
	customer_data = {
		"customer_name": customer_doc.customer_name,
		"customer_id": customer_doc.name,
		"email": customer_doc.email_id,
		"phone": customer_doc.phone or customer_doc.mobile_no,
	}

	# Generate a session token (valid for 24 hours)
	import secrets

	session_token = secrets.token_urlsafe(32)
	cache_key = f"customer_portal_session_{session_token}"

	# Store session in cache
	frappe.cache().set_value(cache_key, {"customer": customer, "created": now()}, expires_in_sec=24 * 60 * 60)

	# Send verification code via SMS or email
	verification_code = random_string(6).upper()
	frappe.cache().set_value(
		f"customer_portal_verify_{session_token}", verification_code, expires_in_sec=10 * 60
	)

	# TODO: Send verification code via SMS/email
	# For now, return it for testing (should be sent via SMS in production)
	customer_data["session_token"] = session_token
	customer_data["verification_code"] = verification_code  # Remove in production
	customer_data["message"] = "Verification code sent to your phone/email"

	return {
		"success": True,
		"customer": customer_data,
		"session_token": session_token,
		"message": "Customer found. Verification code sent.",
	}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def verify_session(session_token: str, verification_code: str) -> dict[str, Any]:
	"""
	Verify customer session using the verification code sent via SMS/email.
	Returns an authenticated session token.
	"""
	if not session_token or not verification_code:
		return {"success": False, "message": "Session token and verification code are required"}

	cache_key = f"customer_portal_verify_{session_token}"
	stored_code = frappe.cache().get_value(cache_key)

	if not stored_code:
		return {"success": False, "message": "Invalid or expired session"}

	if stored_code.upper() != verification_code.upper():
		return {"success": False, "message": "Invalid verification code"}

	# Get session data
	session_cache_key = f"customer_portal_session_{session_token}"
	session_data = frappe.cache().get_value(session_cache_key)

	if not session_data:
		return {"success": False, "message": "Session expired"}

	# Clear verification code and create authenticated session
	frappe.cache().delete_value(cache_key)

	authenticated_token = secrets.token_urlsafe(32)
	auth_cache_key = f"customer_portal_auth_{authenticated_token}"
	frappe.cache().set_value(
		auth_cache_key,
		{"customer": session_data["customer"], "verified": True, "created": now()},
		expires_in_sec=7 * 24 * 60 * 60,
	)  # 7 days

	return {"success": True, "auth_token": authenticated_token, "message": "Session verified successfully"}


def _get_customer_from_token(auth_token: str) -> str | None:
	"""Helper to get customer from authenticated token."""
	if not auth_token:
		return None

	cache_key = f"customer_portal_auth_{auth_token}"
	session_data = frappe.cache().get_value(cache_key)

	if not session_data or not session_data.get("verified"):
		return None

	return session_data.get("customer")


@frappe.whitelist(allow_guest=True)  # nosemgrep
def get_customer_repairs(auth_token: str, status: str | None = None, limit: int = 20) -> dict[str, Any]:
	"""
	Get all repair orders for a customer.

	Args:
	    auth_token: Customer authentication token
	    status: Optional filter by status
	    limit: Maximum number of records to return
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	filters = {"customer": customer}
	if status:
		filters["status"] = status

	repairs = frappe.get_all(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"status",
			"priority",
			"repair_type",
			"item_description",
			"item_type",
			"item_brand",
			"received_date",
			"promised_date",
			"completed_date",
			"delivered_date",
			"estimated_cost",
			"total_cost",
			"deposit_amount",
			"balance_due",
			"payment_status",
			"estimate_status",
			"warehouse",
		],
		order_by="received_date desc",
		limit=int(limit),
	)

	# Enrich with related data
	for repair in repairs:
		if repair.get("repair_type"):
			repair["repair_type_name"] = frappe.db.get_value(
				"Repair Type", repair["repair_type"], "repair_name"
			)
		if repair.get("warehouse"):
			wh_name = frappe.db.get_value("Warehouse", repair["warehouse"], "warehouse_name")
			repair["warehouse_name"] = wh_name or repair["warehouse"]

		# Calculate days until promised date
		if repair.get("promised_date"):
			try:
				promised = getdate(repair["promised_date"])
				today = getdate(nowdate())
				repair["days_until_promised"] = (promised - today).days
				repair["is_overdue"] = repair["days_until_promised"] < 0
			except Exception:
				repair["days_until_promised"] = None
				repair["is_overdue"] = False

	# Get customer info
	customer_doc = frappe.get_doc("Customer", customer)

	return {
		"success": True,
		"customer": {
			"name": customer_doc.customer_name,
			"email": customer_doc.email_id,
			"phone": customer_doc.phone or customer_doc.mobile_no,
		},
		"repairs": repairs,
	}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def get_repair_detail(auth_token: str, repair_order: str) -> dict[str, Any]:
	"""
	Get detailed information about a specific repair order.
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify the repair belongs to this customer
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)
	except frappe.DoesNotExistError:
		return {"success": False, "message": "Repair order not found"}

	# Build detailed response
	detail = {
		"success": True,
		"repair_order": {
			"name": doc.name,
			"status": doc.status,
			"priority": doc.priority,
			"received_date": str(doc.received_date) if doc.received_date else None,
			"promised_date": str(doc.promised_date) if doc.promised_date else None,
			"completed_date": str(doc.completed_date) if doc.completed_date else None,
			"delivered_date": str(doc.delivered_date) if doc.delivered_date else None,
		},
		"customer": {
			"name": doc.customer,
			"phone": doc.customer_phone,
		},
		"item": {
			"type": doc.item_type,
			"brand": doc.item_brand,
			"description": doc.item_description,
			"serial_number": doc.serial_number,
			"condition": doc.item_condition,
			"weight": doc.item_weight,
		},
		"metal": {
			"type": doc.metal_type,
			"purity": doc.purity,
			"weight_in": doc.metal_weight_in,
			"weight_out": doc.metal_weight_out,
			"difference": doc.metal_weight_difference,
		},
		"gemstones": [],
		"photos": {
			"primary": doc.item_photo,
			"before": [],
			"after": [],
		},
		"estimate": {
			"status": doc.estimate_status,
			"estimated_cost": float(doc.estimated_cost or 0),
			"labor_cost": float(doc.labor_cost or 0),
			"material_cost": float(doc.material_cost or 0),
			"total_cost": float(doc.total_cost or 0),
			"sent_date": str(doc.estimate_sent_date) if doc.estimate_sent_date else None,
			"approved_date": str(doc.estimate_approved_date) if doc.estimate_approved_date else None,
			"valid_until": str(doc.estimate_valid_until) if doc.estimate_valid_until else None,
			"notes": doc.estimate_notes,
		},
		"payment": {
			"deposit": float(doc.deposit_amount or 0),
			"total_paid": doc.get_total_paid(),
			"balance_due": float(doc.balance_due or 0),
			"status": doc.payment_status,
		},
		"warranty": {
			"months": doc.warranty_months or 0,
			"expiry_date": str(doc.warranty_expiry_date) if doc.warranty_expiry_date else None,
			"terms": doc.warranty_terms,
		},
		"communications": [],
	}

	# Add repair type name
	if doc.repair_type:
		detail["repair_order"]["repair_type"] = doc.repair_type
		detail["repair_order"]["repair_type_name"] = frappe.db.get_value(
			"Repair Type", doc.repair_type, "repair_name"
		)

	# Add gemstones
	if doc.gemstones:
		for stone in doc.gemstones:
			detail["gemstones"].append(
				{
					"type": stone.gemstone_type,
					"quantity": stone.quantity,
					"carat_weight": stone.carat_weight,
					"color": stone.color,
					"clarity": stone.clarity,
					"setting": stone.setting_type,
				}
			)

	# Add photos
	if doc.before_photos:
		for photo in doc.before_photos:
			if photo.file_url:
				detail["photos"]["before"].append(photo.file_url)

	if doc.after_photos:
		for photo in doc.after_photos:
			if photo.file_url:
				detail["photos"]["after"].append(photo.file_url)

	# Add communications (last 10)
	if doc.communications:
		for comm in doc.communications[-10:]:
			detail["communications"].append(
				{
					"type": comm.communication_type,
					"direction": comm.direction,
					"content": comm.content,
					"timestamp": str(comm.timestamp),
				}
			)

	# Add parts/materials
	detail["parts"] = []
	if doc.parts:
		for part in doc.parts:
			detail["parts"].append(
				{
					"item_code": part.item_code,
					"description": part.description,
					"qty": part.qty,
					"rate": float(part.rate or 0),
					"amount": float(part.amount or 0),
				}
			)

	return detail


@frappe.whitelist(allow_guest=True)  # nosemgrep
def upload_reference_photo(
	auth_token: str, repair_order: str, photo_data: str, filename: str | None = None
) -> dict[str, Any]:
	"""
	Upload a reference photo for a repair order.

	Args:
	    auth_token: Customer authentication token
	    repair_order: The repair order to attach the photo to
	    photo_data: Base64 encoded photo data
	    filename: Optional filename
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	if not photo_data:
		return {"success": False, "message": "No photo data provided"}

	try:
		import base64
		import os

		# Decode base64 if needed
		if isinstance(photo_data, str) and photo_data.startswith("data:image"):
			photo_data = photo_data.split(",")[1]

		# Generate filename if not provided
		if not filename:
			filename = f"customer_photo_{repair_order}_{random_string(8)}.jpg"

		# Save file
		from frappe.utils.file_manager import save_file

		file_doc = save_file(
			filename,
			photo_data,
			"Repair Order",
			repair_order,
			decode=True,
			is_private=0,  # Allow customer to view
		)

		# Log communication about photo upload
		doc = frappe.get_doc("Repair Order", repair_order)
		doc._log_communication(
			"Customer Portal", "Incoming", f"Customer uploaded reference photo: {filename}", "Customer Portal"
		)

		return {
			"success": True,
			"message": "Photo uploaded successfully",
			"file_url": file_doc.file_url,
			"file_name": file_doc.file_name,
		}

	except Exception as e:
		frappe.log_error(f"Photo upload failed for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to upload photo: {e!s}"}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def customer_approve_estimate(
	auth_token: str, repair_order: str, customer_name: str, notes: str | None = None
) -> dict[str, Any]:
	"""
	Approve an estimate via customer portal.

	Args:
	    auth_token: Customer authentication token
	    repair_order: The repair order to approve
	    customer_name: Customer's name for verification
	    notes: Optional approval notes
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)
		result = doc.approve_estimate(customer_name, notes)

		# Log portal action
		doc._log_communication(
			"Customer Portal",
			"Incoming",
			f"Estimate approved via customer portal by {customer_name}",
			"Customer Portal",
			"Estimate Approved",
		)

		return result

	except Exception as e:
		frappe.log_error(f"Estimate approval failed for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to approve estimate: {e!s}"}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def customer_reject_estimate(
	auth_token: str, repair_order: str, customer_name: str, reason: str
) -> dict[str, Any]:
	"""
	Reject an estimate via customer portal.

	Args:
	    auth_token: Customer authentication token
	    repair_order: The repair order to reject
	    customer_name: Customer's name for verification
	    reason: Reason for rejection
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	if not reason:
		return {"success": False, "message": "Please provide a reason for rejection"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)
		result = doc.reject_estimate(customer_name, reason)

		# Log portal action
		doc._log_communication(
			"Customer Portal",
			"Incoming",
			f"Estimate rejected via customer portal by {customer_name}. Reason: {reason}",
			"Customer Portal",
			"Estimate Rejected",
		)

		return result

	except Exception as e:
		frappe.log_error(f"Estimate rejection failed for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to reject estimate: {e!s}"}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def request_repair_update(auth_token: str, repair_order: str, message: str) -> dict[str, Any]:
	"""
	Send a message/update request to the store about a repair order.

	Args:
	    auth_token: Customer authentication token
	    repair_order: The repair order
	    message: Customer's message
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	if not message:
		return {"success": False, "message": "Message is required"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)

		# Log the customer message
		doc._log_communication("Customer Portal", "Incoming", message, "Customer Portal", "Customer Message")

		# Notify store staff
		from frappe.desk.doctype.notification.log import add_notification_log

		# Get users to notify
		users_to_notify = []
		if doc.handled_by:
			users_to_notify.append(doc.handled_by)

		# Add sales users
		sales_users = frappe.get_all("Has Role", filters={"role": "Sales User"}, pluck="parent")
		users_to_notify.extend(sales_users[:5])  # Limit to first 5

		for user in users_to_notify:
			try:
				add_notification_log(
					{
						"subject": f"Customer Message - {doc.name}",
						"for_user": user,
						"type": "Alert",
						"document_type": "Repair Order",
						"document_name": doc.name,
						"message": f"Customer sent a message: {message[:100]}",
					}
				)
			except Exception:
				pass

		return {"success": True, "message": "Message sent successfully"}

	except Exception as e:
		frappe.log_error(f"Failed to send customer message for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to send message: {e!s}"}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def get_repair_history(auth_token: str, include_warranty: bool = True) -> dict[str, Any]:
	"""
	Get complete repair history for a customer, including warranty information.

	Args:
	    auth_token: Customer authentication token
	    include_warranty: Whether to include warranty details
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Get all repairs (delivered and active)
	repairs = frappe.get_all(
		"Repair Order",
		filters={"customer": customer},
		fields=[
			"name",
			"status",
			"repair_type",
			"item_description",
			"received_date",
			"delivered_date",
			"total_cost",
			"warranty_months",
			"warranty_expiry_date",
			"is_warranty_repair",
			"original_repair_order",
		],
		order_by="received_date desc",
	)

	history = []
	today = getdate(nowdate())

	for repair in repairs:
		repair_data = {
			"repair_number": repair["name"],
			"status": repair["status"],
			"repair_type": repair.get("repair_type"),
			"item_description": repair.get("item_description"),
			"received_date": str(repair["received_date"]) if repair["received_date"] else None,
			"delivered_date": str(repair["delivered_date"]) if repair["delivered_date"] else None,
			"total_cost": float(repair.get("total_cost") or 0),
		}

		# Add repair type name
		if repair.get("repair_type"):
			repair_data["repair_type_name"] = frappe.db.get_value(
				"Repair Type", repair["repair_type"], "repair_name"
			)

		# Add warranty info if requested
		if include_warranty:
			warranty_info = {
				"has_warranty": bool(repair.get("warranty_months") and repair.get("warranty_months") > 0),
				"warranty_months": repair.get("warranty_months") or 0,
				"warranty_expiry_date": str(repair["warranty_expiry_date"])
				if repair["warranty_expiry_date"]
				else None,
			}

			# Check if warranty is still valid
			if repair.get("warranty_expiry_date"):
				try:
					expiry = getdate(repair["warranty_expiry_date"])
					warranty_info["is_valid"] = today <= expiry
					warranty_info["days_remaining"] = max(0, (expiry - today).days)
				except Exception:
					warranty_info["is_valid"] = False
					warranty_info["days_remaining"] = 0

			repair_data["warranty"] = warranty_info

		# Mark if this is a warranty repair
		if repair.get("is_warranty_repair"):
			repair_data["is_warranty_repair"] = True
			repair_data["original_repair_order"] = repair.get("original_repair_order")

		history.append(repair_data)

	# Get customer info
	customer_doc = frappe.get_doc("Customer", customer)

	return {
		"success": True,
		"customer": {
			"name": customer_doc.customer_name,
			"email": customer_doc.email_id,
			"phone": customer_doc.phone or customer_doc.mobile_no,
		},
		"history": history,
		"total_repairs": len(history),
	}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def schedule_pickup(
	auth_token: str,
	repair_order: str,
	pickup_date: str,
	pickup_time: str | None = None,
	notes: str | None = None,
) -> dict[str, Any]:
	"""
	Schedule a pickup for a completed repair.

	Args:
	    auth_token: Customer authentication token
	    repair_order: The repair order to schedule pickup for
	    pickup_date: Desired pickup date
	    pickup_time: Optional preferred time
	    notes: Optional notes
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	# Check if repair is ready for pickup
	status = frappe.db.get_value("Repair Order", repair_order, "status")
	if status not in ["Ready for Pickup", "Delivered"]:
		return {"success": False, "message": f"Repair is not ready for pickup (current status: {status})"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)

		# Log the pickup request
		message = f"Pickup scheduled for {pickup_date}"
		if pickup_time:
			message += f" at {pickup_time}"
		if notes:
			message += f". Notes: {notes}"

		doc._log_communication("Customer Portal", "Incoming", message, "Customer Portal", "Pickup Scheduled")

		# Notify store staff
		from frappe.desk.doctype.notification.log import add_notification_log

		users_to_notify = [doc.handled_by] if doc.handled_by else []
		sales_users = frappe.get_all("Has Role", filters={"role": "Sales User"}, pluck="parent")
		users_to_notify.extend(sales_users[:5])

		for user in users_to_notify:
			try:
				add_notification_log(
					{
						"subject": f"Pickup Scheduled - {doc.name}",
						"for_user": user,
						"type": "Information",
						"document_type": "Repair Order",
						"document_name": doc.name,
						"message": f"Customer scheduled pickup for {pickup_date}",
					}
				)
			except Exception:
				pass

		return {"success": True, "message": "Pickup scheduled successfully"}

	except Exception as e:
		frappe.log_error(f"Failed to schedule pickup for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to schedule pickup: {e!s}"}

@frappe.whitelist(allow_guest=True)  # nosemgrep
def initiate_repair_payment(auth_token: str, repair_order: str, provider: str = "stripe") -> dict[str, Any]:
	"""
	Initiate an online payment for the repair order balance.
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)
		balance = doc.balance_due or 0
		
		if balance <= 0:
			return {"success": False, "message": "No balance due"}
			
		# In a real app, this would integrate with Stripe or Square API
		# For MVP, we simulate a payment link creation
		
		payment_id = frappe.generate_hash()[:10]
		
		# Log the attempt
		doc._log_communication(
			"Customer Portal", 
			"Incoming", 
			f"Customer initiated online payment via {provider} for ${balance}", 
			"Customer Portal", 
			"Payment Initiated"
		)
		
		# Return a simulated payment URL
		# Usually: return stripe.checkout.Session.create(...)['url']
		domain = frappe.utils.get_url()
		simulated_url = f"{domain}/api/method/zevar_core.api.repair_customer_portal.simulate_payment_success?repair={repair_order}&amount={balance}&ref={payment_id}"
		
		return {
			"success": True, 
			"payment_url": simulated_url,
			"message": "Payment link generated"
		}

	except Exception as e:
		frappe.log_error(f"Failed to initiate payment for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to initiate payment: {e!s}"}

@frappe.whitelist(allow_guest=True)  # nosemgrep
def simulate_payment_success(repair: str, amount: float, ref: str) -> str:
	"""
	Simulate a successful payment webhook callback.
	"""
	try:
		doc = frappe.get_doc("Repair Order", repair)
		
		# Add deposit/payment
		current_deposit = doc.deposit_amount or 0
		doc.deposit_amount = current_deposit + float(amount)
		doc.payment_status = "Fully Paid" if doc.deposit_amount >= doc.total_cost else "Partially Paid"
		doc.save(ignore_permissions=True)
		
		# Log success
		doc._log_communication(
			"System", 
			"Incoming", 
			f"Online payment of ${amount} received (Ref: {ref})", 
			"System", 
			"Payment Received"
		)
		
		# Broadcast to live monitor
		from zevar_core.api.live_monitor import publish_repair_event
		publish_repair_event("payment_received", {
			"repair": doc.name,
			"customer": doc.customer_name,
			"amount": float(amount),
			"warehouse": doc.warehouse
		})
		
		return f"Payment successful! You can close this window and return to the portal."
		
	except Exception as e:
		return f"Payment recording failed: {e!s}"


@frappe.whitelist(allow_guest=True)  # nosemgrep
def submit_repair_review(auth_token: str, repair_order: str, rating: int, comments: str | None = None) -> dict[str, Any]:
	"""
	Submit a post-repair review and rating.
	"""
	customer = _get_customer_from_token(auth_token)
	if not customer:
		return {"success": False, "message": "Invalid or expired authentication"}

	# Verify ownership
	repair_customer = frappe.db.get_value("Repair Order", repair_order, "customer")
	if repair_customer != customer:
		return {"success": False, "message": "Repair order not found"}

	try:
		doc = frappe.get_doc("Repair Order", repair_order)
		
		# Set custom fields for review if they exist, else log it
		try:
			doc.db_set('custom_review_rating', int(rating))
			if comments:
				doc.db_set('custom_review_comments', comments)
		except Exception:
			# Fields might not exist yet
			pass
			
		# Always log it as communication
		doc._log_communication(
			"Customer Portal", 
			"Incoming", 
			f"Customer rated repair {rating}/5 stars.\nComments: {comments or 'None'}", 
			"Customer Portal", 
			"Review Submitted"
		)
		
		# Alert staff if it's a poor review
		if int(rating) <= 2:
			from frappe.desk.doctype.notification.log import add_notification_log
			
			users_to_notify = [doc.handled_by] if doc.handled_by else []
			managers = frappe.get_all("Has Role", filters={"role": "Store Manager"}, pluck="parent")
			users_to_notify.extend(managers)
			
			for user in set(users_to_notify):
				if not user: continue
				try:
					add_notification_log({
						"subject": f"Poor Review ({rating} stars) - {doc.name}",
						"for_user": user,
						"type": "Alert",
						"document_type": "Repair Order",
						"document_name": doc.name,
						"message": f"Customer gave a low rating. Comments: {comments}"
					})
				except Exception:
					pass
					
		return {"success": True, "message": "Review submitted successfully"}

	except Exception as e:
		frappe.log_error(f"Failed to submit review for {repair_order}: {e}")
		return {"success": False, "message": f"Failed to submit review: {e!s}"}
