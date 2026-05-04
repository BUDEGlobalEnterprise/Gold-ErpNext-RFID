# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PaymentStatus:
	"""Payment status constants"""

	UNPAID = "Unpaid"
	PARTIAL = "Partial"
	PAID = "Paid"


class PaymentMethod:
	"""Payment method constants"""

	CASH = "Cash"
	CREDIT_CARD = "Credit Card"
	CHECK = "Check"
	OTHER = "Other"


class RepairOrder(Document):  # nosemgrep
	def validate(self):
		self.track_critical_changes()
		self.set_total_cost()
		self.update_payment_and_balance()
		self.calculate_metal_weight_difference()
		self.calculate_stone_weight()
		self.auto_set_receiving_store()
		self.validate_store_transfer()
		self.set_warranty_defaults()
		self.validate_warranty_repair()
		self.calculate_warranty_expiry()  # nosemgrep  # nosemgrep
		self.track_id_verification()

	def auto_set_receiving_store(self):
		if not self.receiving_store and self.warehouse:
			self.receiving_store = self.warehouse

	def validate_store_transfer(self):
		"""Validate store transfer configuration"""
		if self.repair_store and self.repair_store == self.receiving_store:
			# Same store - no transfer needed
			self.store_transfer_status = "Not Required"
		elif self.repair_store and self.repair_store != self.receiving_store:
			# Different store - transfer needed
			if not self.store_transfer_status or self.store_transfer_status == "Not Required":
				self.store_transfer_status = "Pending"

	def track_critical_changes(self):
		"""Track critical field changes for audit trail"""
		if not self.get_doc_before_save():
			return

		doc_before_save = self.get_doc_before_save()

		# Track status changes
		if doc_before_save.status != self.status:
			self._log_audit_event(
				"status_change",
				{"old_value": doc_before_save.status, "new_value": self.status, "field": "status"},
			)

		# Track cost changes (total_cost, labor_cost, material_cost)
		cost_fields = ["total_cost", "labor_cost", "material_cost"]
		for field in cost_fields:
			old_value = getattr(doc_before_save, field, None)
			new_value = getattr(self, field, None)
			if old_value != new_value:
				self._log_audit_event(
					"cost_change", {"field": field, "old_value": old_value, "new_value": new_value}
				)

		# Track assignment changes
		if doc_before_save.assigned_to != self.assigned_to:
			self._log_audit_event(
				"assignment_change",
				{
					"old_value": doc_before_save.assigned_to,
					"new_value": self.assigned_to,
					"field": "assigned_to",
				},
			)

		# Track priority changes
		if doc_before_save.priority != self.priority:
			self._log_audit_event(
				"priority_change",
				{"old_value": doc_before_save.priority, "new_value": self.priority, "field": "priority"},
			)

		# Track warranty repair status changes
		if doc_before_save.is_warranty_repair != self.is_warranty_repair:
			self._log_audit_event(
				"warranty_status_change",
				{
					"old_value": doc_before_save.is_warranty_repair,
					"new_value": self.is_warranty_repair,
					"field": "is_warranty_repair",
				},
			)

	def track_id_verification(self):
		"""Track ID verification for compliance"""
		# If ID fields are being set for the first time and verified_by is set
		if self.customer_id_type and self.customer_id_number and self.id_verified_by:
			if not self.id_verified_date:
				from frappe.utils import now

				self.id_verified_date = now()

				# Log the verification
				self._log_audit_event(
					"id_verification",
					{
						"id_type": self.customer_id_type,
						"id_number": "***"
						+ (
							self.customer_id_number[-4:] if len(self.customer_id_number) > 4 else "****"
						),  # Only store last 4 chars
						"id_state": self.customer_id_state,
						"verified_by": self.id_verified_by,
					},
				)

	def _log_audit_event(self, event_type, event_data):
		"""Log an audit event to the version history and communication log"""
		from frappe.utils import now

		# Create a formatted audit message
		audit_messages = {
			"status_change": f"Status changed from '{event_data.get('old_value')}' to '{event_data.get('new_value')}'",
			"cost_change": f"{event_data.get('field')} changed from {event_data.get('old_value')} to {event_data.get('new_value')}",
			"assignment_change": f"Assignment changed from '{event_data.get('old_value')}' to '{event_data.get('new_value')}'",
			"priority_change": f"Priority changed from '{event_data.get('old_value')}' to '{event_data.get('new_value')}'",
			"warranty_status_change": f"Warranty repair status changed to {event_data.get('new_value')}",
			"id_verification": f"ID Verified: {event_data.get('id_type')} from {event_data.get('id_state')} by {event_data.get('verified_by')}",
		}

		message = audit_messages.get(event_type, f"{event_type}: {event_data}")

		# Add to work notes (appears in timeline)
		if hasattr(self, "work_notes"):
			audit_note = f"[Audit] {message} - {now()}"
			if not self.work_notes:
				self.work_notes = audit_note
			else:
				self.work_notes += f"\n{audit_note}"

		# Add to communication log for structured tracking
		try:
			self._log_communication(comm_type="Audit", direction="System", content=message, sent_via="System")
		except Exception:
			# If communication log fails, still log to version history
			pass

	def get_audit_trail(self, limit=100):
		"""Get comprehensive audit trail for this repair order"""
		from frappe.model.version import get_versions

		audit_trail = {
			"repair_order": self.name,
			"customer": self.customer,
			"version_history": [],
			"communication_log": [],
			"status_timeline": [],
		}

		# Get version history
		try:
			versions = get_versions(self.name)
			for version in versions[:limit]:
				audit_trail["version_history"].append(
					{
						"version": version.get("name"),
						"modified": version.get("modified"),
						"modified_by": version.get("modified_by"),
						"creation": version.get("creation"),
					}
				)
		except Exception as e:
			frappe.log_error(f"Failed to get version history for {self.name}: {e}")

		# Get communication log (includes audit events)
		if hasattr(self, "communications") and self.communications:
			for comm in self.communications:
				if comm.communication_type == "Audit":
					audit_trail["communication_log"].append(
						{
							"timestamp": comm.timestamp,
							"user": comm.user,
							"content": comm.content,
							"direction": comm.direction,
						}
					)

		# Build status timeline
		status_transitions = []
		for comm in self.communications or []:
			if comm.communication_type == "Audit" and "status changed" in comm.content.lower():
				status_transitions.append(
					{"timestamp": comm.timestamp, "user": comm.user, "event": comm.content}
				)

		audit_trail["status_timeline"] = sorted(
			status_transitions, key=lambda x: x["timestamp"], reverse=True
		)

		return audit_trail

	def get_compliance_summary(self):
		"""Get compliance status summary for this repair order"""
		compliance = {
			"repair_order": self.name,
			"customer_id_verified": bool(self.id_verified_by and self.id_verified_date),
			"intake_checklist_signed": bool(self.intake_checklist_signed),
			"has_gemstone_disclosure": bool(self.gemstone_disclosure),
			"has_metals_disclosure": bool(self.precious_metals_disclosure),
			"has_signature": bool(self.intake_checklist_signature),
			"verified_by": self.id_verified_by,
			"verified_date": self.id_verified_date,
			"id_type": self.customer_id_type,
			"compliance_score": 0,
		}

		# Calculate compliance score (0-100)
		score = 0
		max_score = 5  # Total number of compliance checkpoints

		if compliance["customer_id_verified"]:
			score += 1
		if compliance["intake_checklist_signed"]:
			score += 1
		if compliance["has_gemstone_disclosure"] and self.gemstones:
			score += 1
		if compliance["has_metals_disclosure"] and self.metal_type:
			score += 1
		if compliance["has_signature"]:
			score += 1

		compliance["compliance_score"] = int((score / max_score) * 100) if max_score > 0 else 0
		compliance["is_compliant"] = compliance["compliance_score"] >= 80

		return compliance

	def set_total_cost(self):
		parts_total = sum((row.amount or 0.0) for row in (self.parts or []))
		if parts_total:
			self.material_cost = parts_total

		# Ensure we treat None as 0.0 for calculations
		labor = self.labor_cost or 0.0
		material = self.material_cost or 0.0
		self.total_cost = labor + material

		if not self.received_date and self.is_new():
			from frappe.utils import now

			self.received_date = now()

	def calculate_metal_weight_difference(self):
		"""Calculate net metal difference: (Weight Out + Scrap) - Weight In"""
		weight_in = self.metal_weight_in or 0.0
		weight_out = self.metal_weight_out or 0.0
		scrap = self.metal_scrap or 0.0

		# Net difference: what goes out (including scrap) minus what came in
		# Positive = metal added, Negative = metal lost
		self.metal_weight_difference = (weight_out + scrap) - weight_in

	def calculate_stone_weight(self):
		"""Calculate total stone weight from gemstones child table"""
		if not self.gemstones:
			self.stone_weight = 0.0
			return

		total_carats = sum((row.carat_weight or 0.0) for row in self.gemstones)
		self.stone_weight = total_carats

	def update_payment_and_balance(self):
		"""Calculate balance due and update payment status in single pass"""
		total = self.total_cost or 0.0
		deposit = self.deposit_amount or 0.0
		payments_total = sum((row.amount or 0.0) for row in (self.payments or []))
		total_paid = deposit + payments_total

		self.balance_due = total - total_paid

		if total <= 0:
			self.payment_status = PaymentStatus.UNPAID
		elif total_paid >= total:
			self.payment_status = PaymentStatus.PAID
		elif total_paid > 0:
			self.payment_status = PaymentStatus.PARTIAL
		else:
			self.payment_status = PaymentStatus.UNPAID

	def create_sales_invoice(self):
		"""Create Sales Invoice from Repair Order"""
		if self.sales_invoice:
			frappe.throw(_("Sales Invoice already exists: {0}").format(self.sales_invoice))

		if not self.customer:
			frappe.throw(_("Customer is required to create Sales Invoice"))

		if not self.total_cost or self.total_cost <= 0:
			frappe.throw(_("Total cost must be greater than zero to create Sales Invoice"))

		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)

		if not company:
			frappe.throw(_("No company configured"))

		# Create Sales Invoice
		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = self.customer
		invoice.company = company
		invoice.due_date = self.promised_date or frappe.utils.nowdate()
		invoice.repair_order = self.name

		# Add repair service item
		repair_item_code = (
			frappe.db.get_single_value("Repair Settings", "repair_service_item_code") or "REPAIR-SERVICE"
		)

		invoice.append(
			"items",
			{
				"item_code": repair_item_code,
				"qty": 1,
				"rate": self.total_cost,
				"amount": self.total_cost,
				"description": f"Repair Service: {self.repair_type}\nItem: {self.item_description or 'N/A'}",
				"income_account": f"Income — Repair Services - {frappe.get_cached_value('Company', company, 'abbr')}",
			},
		)

		invoice.custom_transaction_stream = "Repair"

		# Set warehouse
		if self.warehouse:
			invoice.set_warehouse = self.warehouse

		# Handle deposit as advance payment
		if self.deposit_amount and self.deposit_amount > 0:
			invoice.debit_to = frappe.db.get_value("Customer", self.customer, "debit_to")

		invoice.flags.ignore_permissions = True
		invoice.insert()
		invoice.submit()

		# Link invoice to repair order
		self.sales_invoice = invoice.name
		self.db_set("sales_invoice", invoice.name)

		# Update payment status
		self.update_payment_status()

		return {
			"success": True,
			"invoice": invoice.name,
			"message": _("Sales Invoice {0} created successfully").format(invoice.name),
		}

	def add_payment(self, amount, payment_method, payment_date=None, reference=None, notes=None):
		"""Add a payment entry to the payments child table"""
		if not amount or amount <= 0:
			frappe.throw(_("Payment amount must be greater than zero"))

		if not payment_method:
			frappe.throw(_("Payment method is required"))

		from frappe.utils import now

		payment = {
			"doctype": "Repair Payment",
			"payment_date": payment_date or now(),
			"amount": amount,
			"payment_method": payment_method,
			"received_by": frappe.session.user,
		}

		if reference:
			payment["reference"] = reference
		if notes:
			payment["notes"] = notes

		self.append("payments", payment)

		# Log the payment as communication
		self._log_communication(
			"Payment", "Incoming", f"Payment of ${amount:.2f} received via {payment_method}", "In-Person"
		)

		self.save()

		return {
			"success": True,
			"message": _("Payment of {0} recorded successfully").format(f"${amount:.2f}"),
		}

	def get_total_payments(self):
		"""Get total of all payments recorded"""
		return sum((row.amount or 0.0) for row in (self.payments or []))

	def get_total_paid(self):
		"""Get total amount paid (deposit + payments)"""
		deposit = self.deposit_amount or 0.0
		payments_total = self.get_total_payments()
		return deposit + payments_total

	def on_submit(self):
		"""Called when document is submitted."""
		# Set initial status to Received if not set
		if not self.status or self.status == "Draft":
			self.status = "Received"
		self.db_set("status", self.status)

	def on_cancel(self):
		"""Called when document is cancelled."""
		self.status = "Cancelled"
		self.db_set("status", "Cancelled")

	def on_update(self):
		# When status is Delivered, create Stock Entry (Material Issue) for parts consumed (once)
		if self.status == "Delivered" and self.parts and not self.get("parts_stock_created"):
			self._create_parts_stock_entry()

		# Calculate warranty expiry when status changes to Delivered
		if self.status == "Delivered":
			self.calculate_warranty_expiry()
			if self.warranty_expiry_date:
				self.db_set("warranty_expiry_date", self.warranty_expiry_date)


	def _create_parts_stock_entry(self):
		"""Create Material Issue stock entry for parts consumed in this repair."""
		if not self.parts:
			return
		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		if not company:
			return
		warehouse = self.warehouse
		items = []
		for row in self.parts:
			wh = row.warehouse or warehouse
			if not wh or not row.item_code or (row.qty or 0) <= 0:
				continue
			items.append(
				{
					"item_code": row.item_code,
					"qty": row.qty,
					"warehouse": wh,
				}
			)
		if not items:
			return
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.company = company
		for it in items:
			se.append(
				"items",
				{
					"item_code": it["item_code"],
					"qty": it["qty"],
					"s_warehouse": it["warehouse"],
				},
			)
		se.flags.ignore_permissions = True
		se.submit()
		frappe.db.set_value("Repair Order", self.name, "parts_stock_created", 1)

	def initiate_store_transfer(self):
		"""Create Material Transfer stock entry for store-to-store repair transfer"""
		if not self.repair_store or self.repair_store == self.receiving_store:
			return {"success": False, "message": "No transfer needed or repair store not set"}

		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		if not company:
			return {"success": False, "message": "No company configured"}

		# Create Stock Entry for Material Transfer
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		se.company = company
		se.from_warehouse = self.receiving_store
		se.to_warehouse = self.repair_store

		# Add item to transfer (use a placeholder item or track as service)
		# For jewelry repairs, we track the customer's item as inventory
		item_code = frappe.db.get_single_value("Repair Settings", "repair_item_code") or "REPAIR-ITEM"

		se.append(
			"items",
			{
				"item_code": item_code,
				"qty": 1,
				"s_warehouse": self.receiving_store,
				"t_warehouse": self.repair_store,
			},
		)

		se.flags.ignore_permissions = True
		se.submit()

		# Update transfer status
		self.store_transfer_status = "In Transit"
		self.db_set("store_transfer_status", "In Transit")

		# Notify receiving store
		self._notify_receiving_store()

		return {
			"success": True,
			"message": f"Transfer initiated to {self.repair_store}",
			"stock_entry": se.name,
		}

	def confirm_store_receipt(self):
		"""Confirm receipt of repair item at destination store"""
		if self.store_transfer_status != "In Transit":
			return {"success": False, "message": "Transfer is not in transit"}

		self.store_transfer_status = "Received"
		self.warehouse = self.repair_store  # Update current warehouse
		self.db_set("warehouse", self.repair_store)
		self.db_set("store_transfer_status", "Received")

		return {
			"success": True,
			"message": f"Repair item received at {self.repair_store}",
		}

	def _notify_receiving_store(self):
		"""Send notification to receiving store about incoming repair"""
		# TODO: Implement notification system
		# This could be:
		# - Email to store manager
		# - System notification
		# - SMS notification
		try:
			# Get users associated with the target warehouse/store
			store_users = frappe.get_all(
				"User",
				filters={"default_warehouse": self.repair_store},
				pluck="email",
			)

			if store_users:
				from frappe.desk.doctype.notification.log import add_notification_log

				for user_email in store_users:
					add_notification_log(
						{
							"subject": f"Incoming Repair Transfer: {self.name}",
							"for_user": user_email,
							"type": "Alert",
							"document_type": "Repair Order",
							"document_name": self.name,
							"from_user": frappe.session.user,
						}
					)
		except Exception as e:
			frappe.log_error(f"Failed to notify receiving store: {e}")

	def send_status_notification(self, old_status=None):
		"""Send notification based on status change"""
		if not self.customer_phone and not self.get_customer_email():
			return

		status_notification_map = {
			"Received": self._send_received_notification,
			"Estimated": self._send_estimate_notification,
			"Approved": self._send_approved_notification,
			"In Progress": self._send_in_progress_notification,
			"Waiting for Parts": self._send_waiting_parts_notification,
			"Ready for Pickup": self._send_ready_pickup_notification,
			"Delivered": self._send_delivered_notification,
		}

		notification_func = status_notification_map.get(self.status)
		if notification_func:
			try:
				notification_func()
			except Exception as e:
				frappe.log_error(
					f"Failed to send notification for {self.name} status {self.status}: {e}",
					"Repair Notification Error",
				)

	def _send_received_notification(self):
		"""Send notification when repair is received"""
		message = f"We've received your repair request. Repair #: {self.name}. We'll contact you with an estimate soon."
		subject = f"Repair Received - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_received_email_body())

	def _send_estimate_notification(self):
		"""Send notification when estimate is ready"""
		self.estimate_status = "Sent"
		self.estimate_sent_date = frappe.utils.now()
		self.db_set({"estimate_status": "Sent", "estimate_sent_date": self.estimate_sent_date})

		amount = f"${self.total_cost:.2f}" if self.total_cost else "TBD"
		message = f"Estimate ready for {self.name}: {amount}. Reply APPROVE to proceed or call us to discuss."
		subject = f"Repair Estimate Ready - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_estimate_email_body())

	def _send_approved_notification(self):
		"""Send notification when estimate is approved"""
		self.estimate_status = "Approved"
		self.estimate_approved_date = frappe.utils.now()
		self.db_set({"estimate_status": "Approved", "estimate_approved_date": self.estimate_approved_date})

		message = f"Great news! Your repair {self.name} has been approved. We'll begin work shortly."
		subject = f"Repair Approved - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_approved_email_body())

	def _send_in_progress_notification(self):
		"""Send notification when work begins"""
		message = f"Work has started on your repair {self.name}. We'll update you on progress."
		subject = f"Repair In Progress - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_in_progress_email_body())

	def _send_waiting_parts_notification(self):
		"""Send notification when waiting for parts"""
		message = f"Your repair {self.name} is waiting for parts. We'll notify you when they arrive."
		subject = f"Repair Waiting for Parts - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_waiting_parts_email_body())

	def _send_ready_pickup_notification(self):
		"""Send notification when repair is ready"""
		message = f"Your repair {self.name} is ready for pickup! Visit us during store hours."
		subject = f"Repair Ready for Pickup - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_ready_pickup_email_body())

	def _send_delivered_notification(self):
		"""Send notification when repair is delivered"""
		message = f"Thank you! Your repair {self.name} has been delivered. We appreciate your business."
		subject = f"Repair Completed - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_delivered_email_body())

	def _send_overdue_notification(self):
		"""Send notification when repair is overdue"""
		message = f"Your repair {self.name} is past the promised date. We apologize for the delay and will update you soon."
		subject = f"Repair Update - {self.name}"

		self._send_sms(message)
		self._send_email(subject, self._get_overdue_email_body())

	def _send_sms(self, message):
		"""Send SMS notification using Twilio or Frappe SMS Settings"""
		if not self.customer_phone or not self.enable_sms_notifications:
			return None

		# Log the communication attempt
		comm_log = self._log_communication("SMS", "Outgoing", message, self.customer_phone)

		try:
			# Try Twilio first if configured
			twilio_settings = frappe.get_single("Twilio Settings", cache=True)
			if twilio_settings and twilio_settings.get("enabled"):
				return self._send_via_twilio(message, comm_log)

			# Fall back to Frappe SMS Settings
			sms_settings = frappe.get_single("SMS Settings", cache=True)
			if sms_settings and sms_settings.get("sms_gateway_url"):
				return self._send_via_frappe_sms(message, comm_log)

			# If no SMS gateway configured, log as pending
			comm_log.status = "Pending"
			comm_log.error_message = "No SMS gateway configured"
			comm_log.save()

		except Exception as e:
			comm_log.status = "Failed"
			comm_log.error_message = str(e)
			comm_log.save()
			frappe.log_error(f"SMS send failed for {self.name}: {e}")

		return None

	def _send_via_twilio(self, message, comm_log):
		"""Send SMS via Twilio"""
		twilio_settings = frappe.get_single("Twilio Settings")
		if not twilio_settings.twilio_account_sid or not twilio_settings.twilio_auth_token:
			return None

		try:
			from twilio.rest import Client

			client = Client(
				twilio_settings.twilio_account_sid,
				twilio_settings.twilio_auth_token,
			)

			message_obj = client.messages.create(
				body=message,
				from_=twilio_settings.twilio_phone_number,
				to=self.customer_phone,
			)

			comm_log.status = "Sent"
			comm_log.save()
			return message_obj.sid

		except ImportError:
			comm_log.status = "Failed"
			comm_log.error_message = "Twilio library not installed"
			comm_log.save()
		except Exception as e:
			comm_log.status = "Failed"
			comm_log.error_message = str(e)
			comm_log.save()

		return None

	def _send_via_frappe_sms(self, message, comm_log):
		"""Send SMS via Frappe SMS Settings"""
		try:
			from frappe.core.doctype.sms_settings.sms_settings import send_sms

			send_sms(
				receiver_list=[self.customer_phone],
				msg=message,
			)

			comm_log.status = "Sent"
			comm_log.save()

		except Exception as e:
			comm_log.status = "Failed"
			comm_log.error_message = str(e)
			comm_log.save()
			raise

		return True

	def _send_email(self, subject, html_body):
		"""Send email notification"""
		if not self.enable_email_notifications:
			return None

		email = self.get_customer_email()
		if not email:
			return None

		# Log the communication attempt
		comm_log = self._log_communication("Email", "Outgoing", html_body, email, subject)

		try:
			frappe.sendmail(
				recipients=[email],
				subject=subject,
				message=html_body,
				reference_doctype=self.doctype,
				reference_name=self.name,
				queued=True,
			)

			comm_log.status = "Sent"
			comm_log.save()

		except Exception as e:
			comm_log.status = "Failed"
			comm_log.error_message = str(e)
			comm_log.save()
			frappe.log_error(f"Email send failed for {self.name}: {e}")

		return None

	def get_customer_email(self):
		"""Get customer email from Customer record"""
		if not self.customer:
			return None
		return frappe.db.get_value("Customer", self.customer, "email_id")

	def _log_communication(self, comm_type, direction, content, sent_via, subject=None):
		"""Log a communication entry"""
		if not hasattr(self, "communications") or self.communications is None:
			self.load_from_db()

		comm = {
			"doctype": "Repair Communication",
			"parenttype": "Repair Order",
			"parentfield": "communications",
			"parent": self.name,
			"communication_type": comm_type,
			"direction": direction,
			"content": content,
			"sent_via": sent_via,
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}

		if subject:
			comm["subject"] = subject

		# Append to child table and save
		self.append("communications", comm)
		self.save(ignore_permissions=True)

		# Return the newly created communication
		return self.communications[-1]

	def log_manual_communication(self, comm_type, direction, content, sent_via=None, subject=None):
		"""Log a manual communication entry (e.g., phone call, in-person)"""
		comm = {
			"doctype": "Repair Communication",
			"parenttype": "Repair Order",
			"parentfield": "communications",
			"parent": self.name,
			"communication_type": comm_type,
			"direction": direction,
			"content": content,
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}

		if sent_via:
			comm["sent_via"] = sent_via
		if subject:
			comm["subject"] = subject

		self.append("communications", comm)
		self.save()
		return self.communications[-1]

	def _get_base_email_context(self):
		"""Get base context for email templates"""
		customer_name = self.customer
		if self.customer:
			customer_name = frappe.db.get_value("Customer", self.customer, "customer_name")

		repair_type_name = self.repair_type
		if self.repair_type:
			repair_type_name = frappe.db.get_value("Repair Type", self.repair_type, "repair_name")

		return {
			"repair_number": self.name,
			"customer_name": customer_name,
			"repair_type": repair_type_name,
			"item_description": self.item_description or "N/A",
			"estimated_cost": f"${self.total_cost:.2f}" if self.total_cost else "TBD",
			"promised_date": self.promised_date or "TBD",
		}

	def _get_received_email_body(self):
		"""Get email body for received notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Received - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>We have received your repair request:</p>
			<table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
				<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Repair #:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{ctx["repair_number"]}</td></tr>
				<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Item:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{ctx["item_description"]}</td></tr>
				<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Repair Type:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{ctx["repair_type"]}</td></tr>
			</table>
			<p>We will review your item and send you an estimate shortly.</p>
			<p>Thank you for choosing Zevar Jewelers!</p>
		</div>
		"""

	def _get_estimate_email_body(self):
		"""Get email body for estimate notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Estimate Ready - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>We have completed our assessment of your repair:</p>
			<table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
				<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Repair #:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{ctx["repair_number"]}</td></tr>
				<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Estimated Cost:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{ctx["estimated_cost"]}</td></tr>
				<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Promised Date:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{ctx["promised_date"]}</td></tr>
			</table>
			<p>Please reply to this email or call us to approve the estimate so we can begin work.</p>
			<p>Thank you,<br>Zevar Jewelers</p>
		</div>
		"""

	def _get_approved_email_body(self):
		"""Get email body for approved notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Approved - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>Great news! Your estimate for repair #{ctx["repair_number"]} has been approved.</p>
			<p>We will begin work on your item shortly and keep you updated on our progress.</p>
			<p>Thank you for your patience!</p>
		</div>
		"""

	def _get_in_progress_email_body(self):
		"""Get email body for in progress notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair In Progress - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>Work has begun on your repair #{ctx["repair_number"]}.</p>
			<p>We are working on your {ctx["item_description"]} and will notify you when it's ready.</p>
			<p>Thank you for choosing Zevar Jewelers!</p>
		</div>
		"""

	def _get_waiting_parts_email_body(self):
		"""Get email body for waiting parts notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Update - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>Your repair #{ctx["repair_number"]} is currently waiting for parts to arrive.</p>
			<p>We have ordered the necessary components and will notify you as soon as they arrive.</p>
			<p>Thank you for your understanding!</p>
		</div>
		"""

	def _get_ready_pickup_email_body(self):
		"""Get email body for ready pickup notification"""
		ctx = self._get_base_email_context()
		# Get store address if available
		store_address = ""
		if self.warehouse:
			store_address = frappe.db.get_value("Warehouse", self.warehouse, "warehouse_address") or ""

		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Ready for Pickup! - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>Great news! Your repair #{ctx["repair_number"]} is complete and ready for pickup!</p>
			<p>Please visit us during store hours to collect your item.</p>
			{f"<p><strong>Store:</strong> {store_address}</p>" if store_address else ""}
			<p>Don't forget to bring your claim ticket!</p>
			<p>Thank you for choosing Zevar Jewelers!</p>
		</div>
		"""

	def _get_delivered_email_body(self):
		"""Get email body for delivered notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Completed - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>Your repair #{ctx["repair_number"]} has been delivered to you.</p>
			<p>We hope you are satisfied with our work. If you have any questions or concerns, please don't hesitate to contact us.</p>
			<p>Thank you for your business!</p>
		</div>
		"""

	def _get_overdue_email_body(self):
		"""Get email body for overdue notification"""
		ctx = self._get_base_email_context()
		return f"""
		<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
			<h2 style="color: #d4af37;">Repair Update - Zevar Jewelers</h2>
			<p>Dear {ctx["customer_name"]},</p>
			<p>We apologize, but your repair #{ctx["repair_number"]} is taking longer than expected.</p>
			<p>We are working diligently to complete your repair and will notify you as soon as it is ready.</p>
			<p>Thank you for your patience and understanding.</p>
		</div>
		"""

	def approve_estimate(self, customer_name, approval_notes=None):
		"""Approve the estimate and move to Approved status"""
		if self.estimate_status != "Sent":
			frappe.throw(_("Estimate must be sent before it can be approved"))

		self.estimate_status = "Approved"
		self.estimate_approved_date = frappe.utils.now()
		self.estimate_approved_by = customer_name
		self.status = "Approved"

		if approval_notes:
			if not self.estimate_notes:
				self.estimate_notes = ""
			self.estimate_notes += f"\n\nApproval Notes: {approval_notes}"

		self.save()
		self.db_set(
			{
				"estimate_status": "Approved",
				"estimate_approved_date": self.estimate_approved_date,
				"estimate_approved_by": self.estimate_approved_by,
				"status": "Approved",
			}
		)

		# Log the approval
		self._log_communication(
			"Email",
			"Incoming",
			f"Estimate approved by {customer_name}",
			"Customer Portal",
			"Estimate Approved",
		)

		# Send notification
		self._send_approved_notification()

		return {"success": True, "message": "Estimate approved successfully", "repair_order": self.name}

	def reject_estimate(self, customer_name, rejection_reason):
		"""Reject the estimate and record reason"""
		if self.estimate_status != "Sent":
			frappe.throw(_("Estimate must be sent before it can be rejected"))

		if not rejection_reason:
			frappe.throw(_("Please provide a reason for rejection"))

		self.estimate_status = "Rejected"
		self.estimate_notes = f"Rejected by {customer_name}\n\nReason: {rejection_reason}"
		self.status = "Estimated"  # Keep in Estimated status for revision

		self.save()
		self.db_set(
			{"estimate_status": "Rejected", "estimate_notes": self.estimate_notes, "status": "Estimated"}
		)

		# Log the rejection
		self._log_communication(
			"Email",
			"Incoming",
			f"Estimate rejected by {customer_name}. Reason: {rejection_reason}",
			"Customer Portal",
			"Estimate Rejected",
		)

		# Notify store staff
		self._notify_estimate_rejection(customer_name, rejection_reason)

		return {
			"success": True,
			"message": "Estimate rejection recorded. Store staff will contact you.",
			"repair_order": self.name,
		}

	def revise_estimate(self, new_total_cost, revision_notes=None):
		"""Revise the estimate with new cost"""
		if self.estimate_status not in ["Rejected", "Sent"]:
			frappe.throw(_("Estimate must be sent or rejected before it can be revised"))

		self.estimate_status = "Revised"
		self.total_cost = new_total_cost

		if revision_notes:
			if not self.estimate_notes:
				self.estimate_notes = ""
			self.estimate_notes += f"\n\nRevision Notes ({frappe.utils.now()}): {revision_notes}"

		self.save()
		self.db_set({"estimate_status": "Revised", "total_cost": new_total_cost})

		return {"success": True, "message": "Estimate revised successfully", "repair_order": self.name}

	def send_for_approval(self):
		"""Send estimate to customer for approval"""
		if not self.total_cost or self.total_cost <= 0:
			frappe.throw(_("Please set a total cost before sending for approval"))

		self.status = "Estimated"
		self.estimate_status = "Sent"
		self.estimate_sent_date = frappe.utils.now()

		# Set valid until date (30 days from now)
		from frappe.utils import add_to_date

		self.estimate_valid_until = add_to_date(frappe.utils.now(), days=30)

		self.save()
		self.db_set(
			{
				"status": "Estimated",
				"estimate_status": "Sent",
				"estimate_sent_date": self.estimate_sent_date,
				"estimate_valid_until": self.estimate_valid_until,
			}
		)

		# Send notifications
		self._send_estimate_notification()

		return {
			"success": True,
			"message": "Estimate sent to customer for approval",
			"repair_order": self.name,
		}

	def generate_estimate_pdf(self):
		"""Generate PDF for the estimate"""
		from frappe.utils.pdf import get_pdf

		# Get base context
		ctx = self._get_base_email_context()
		ctx.update(
			{
				"estimate_sent_date": self.estimate_sent_date,
				"estimate_valid_until": self.estimate_valid_until,
				"labor_cost": f"${self.labor_cost:.2f}" if self.labor_cost else "$0.00",
				"material_cost": f"${self.material_cost:.2f}" if self.material_cost else "$0.00",
				"total_cost": f"${self.total_cost:.2f}" if self.total_cost else "$0.00",
				"item_description": self.item_description or "N/A",
				"customer_notes": self.customer_notes or "None",
			}
		)

		# Get store address
		if self.warehouse:
			warehouse_address = frappe.db.get_value("Warehouse", self.warehouse, "warehouse_address") or ""
			ctx["store_address"] = warehouse_address

		# Generate HTML
		html = frappe.render_template(  # nosemgrep
			"zevar_core/templates/emails/estimate_pdf.html", context=ctx
		)  # nosemgrep

		# Generate PDF
		pdf_data = get_pdf(html)

		# Save as attached file
		filename = f"estimate_{self.name.replace(' ', '_')}.pdf"
		frappe.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": "Repair Order",
				"attached_to_name": self.name,
				"file_name": filename,
				"content": pdf_data,
				"is_private": 1,
			}
		).insert()

		return {"success": True, "filename": filename, "message": "Estimate PDF generated successfully"}

	def get_estimate_approval_link(self):
		"""Generate public link for estimate approval"""
		# Generate a unique token
		import hashlib
		import secrets

		from frappe.utils import get_url

		token = secrets.token_urlsafe(32)

		# Store token in cache for 30 days
		cache_key = f"estimate_approval_{self.name}_{token}"
		frappe.cache().set_value(
			cache_key,
			{"repair_order": self.name, "created": frappe.utils.now()},
			expires_in_sec=30 * 24 * 60 * 60,
		)

		# Return public URL
		return f"{get_url()}/api/method/zevar_core.api.public_estimate_approval?token={token}"

	def _notify_estimate_rejection(self, customer_name, reason):
		"""Notify store staff about estimate rejection"""
		try:
			from frappe.desk.doctype.notification.log import add_notification_log

			# Get all users with Sales User role
			users = frappe.get_all("Has Role", filters={"role": "Sales User"}, pluck="parent")

			for user in users:
				add_notification_log(
					{
						"subject": f"Estimate Rejected - {self.name}",
						"for_user": user,
						"type": "Alert",
						"document_type": "Repair Order",
						"document_name": self.name,
						"message": f"Customer {customer_name} rejected the estimate. Reason: {reason}",
					}
				)
		except Exception as e:
			frappe.log_error(f"Failed to notify estimate rejection: {e}")

	def check_estimate_validity(self):
		"""Check if estimate is still valid"""
		if not self.estimate_valid_until:
			return {"valid": True, "message": "No validity date set"}

		from frappe.utils import getdate

		today = getdate()
		valid_until = getdate(self.estimate_valid_until)

		if today > valid_until:
			return {"valid": False, "message": f"Estimate expired on {self.estimate_valid_until}"}

		return {"valid": True, "message": f"Estimate valid until {self.estimate_valid_until}"}


	def set_warranty_defaults(self):
		"""Auto-set warranty_months from Repair Type if not set"""
		if self.repair_type and not self.warranty_months:
			self.warranty_months = (
				frappe.db.get_value("Repair Type", self.repair_type, "warranty_months") or 0
			)

	def validate_warranty_repair(self):
		"""Validate warranty repair settings"""
		if self.is_warranty_repair:
			if not self.original_repair_order:
				frappe.throw(_("Original Repair Order is required for warranty repairs"))

			# Validate warranty is still valid
			original = frappe.get_doc("Repair Order", self.original_repair_order)
			validation = self.check_warranty_validity(original)
			if not validation["valid"]:
				frappe.throw(_(validation["message"]))

			# Auto-set warranty claim type if not set
			if not self.warranty_claim_type:
				self.warranty_claim_type = "Full Warranty"

			# Auto-zero costs for full warranty repairs
			if self.warranty_claim_type == "Full Warranty":
				self.labor_cost = 0
				self.material_cost = 0
				self.total_cost = 0

	def calculate_warranty_expiry(self):  # nosemgrep
		"""Calculate warranty expiry date when delivered"""
		if self.delivered_date and self.warranty_months and self.warranty_months > 0:
			from frappe.utils import add_to_date, getdate

			delivery_date = getdate(self.delivered_date)
			self.warranty_expiry_date = add_to_date(delivery_date, months=self.warranty_months)
		elif not self.delivered_date:
			# Clear expiry date if not delivered
			self.warranty_expiry_date = None

	def check_warranty_validity(self, original_repair=None):
		"""Check if warranty is still valid for a repair"""
		if not original_repair:
			if not self.original_repair_order:
				return {"valid": False, "message": "No original repair order specified"}
			original_repair = frappe.get_doc("Repair Order", self.original_repair_order)

		if not original_repair.warranty_expiry_date:
			return {"valid": False, "message": "Original repair has no warranty"}

		from frappe.utils import getdate

		today = getdate()
		expiry_date = getdate(original_repair.warranty_expiry_date)

		if today > expiry_date:
			return {"valid": False, "message": f"Warranty expired on {original_repair.warranty_expiry_date}"}

		return {"valid": True, "message": f"Warranty valid until {original_repair.warranty_expiry_date}"}

	def verify_customer_id(self, id_type, id_number, id_state=None):
		"""Verify customer identification for compliance (JVC)"""
		if not id_type or not id_number:
			return {"success": False, "message": "ID type and number are required"}

		# Update fields
		self.customer_id_type = id_type
		self.customer_id_number = id_number
		self.customer_id_state = id_state
		self.id_verified_by = frappe.session.user
		from frappe.utils import now

		self.id_verified_date = now()

		# Log the verification
		self._log_audit_event(
			"id_verification",
			{
				"id_type": id_type,
				"id_number": "***" + (id_number[-4:] if len(id_number) > 4 else "****"),
				"id_state": id_state,
				"verified_by": self.id_verified_by,
			},
		)

		self.save()

		return {
			"success": True,
			"message": "Customer ID verified successfully",
			"verified_by": self.id_verified_by,
			"verified_date": self.id_verified_date,
		}

	def sign_intake_checklist(self, signature_data):
		"""Sign the intake checklist (customer signature)"""
		if not signature_data:
			return {"success": False, "message": "Signature data is required"}

		# Save signature as attached file
		import base64
		import os

		try:
			# Decode base64 signature if needed
			if isinstance(signature_data, str) and signature_data.startswith("data:image"):
				signature_data = signature_data.split(",")[1]

			# Create file
			filename = f"intake_signature_{self.name.replace(' ', '_')}.png"
			file_path = frappe.get_site_path("private", "files", filename)

			# Write file
			with open(file_path, "wb") as f:  # nosemgrep
				f.write(base64.b64decode(signature_data))

			# Save file doc
			from frappe.utils.file_manager import save_file

			file_doc = save_file(filename, file_path, self.doctype, self.name, is_private=1)

			# Update field
			self.intake_checklist_signature = file_doc.file_url
			self.intake_checklist_signed = 1

			# Log the signature
			self._log_audit_event(
				"intake_signed", {"signature_file": file_doc.file_url, "signed_by": frappe.session.user}
			)

			self.save()

			return {
				"success": True,
				"message": "Intake checklist signed successfully",
				"signature_url": file_doc.file_url,
			}

		except Exception as e:
			frappe.log_error(f"Failed to save intake signature for {self.name}: {e}")
			return {"success": False, "message": f"Failed to save signature: {e!s}"}

	def get_compliance_report(self):
		"""Generate comprehensive compliance report for this repair order"""
		from frappe.utils import nowdate

		report = {
			"repair_order": self.name,
			"report_date": nowdate(),
			"compliance": self.get_compliance_summary(),
			"audit_trail": {
				"versions": len(self.get_audit_trail().get("version_history", [])),
				"audit_events": len(
					[c for c in (self.communications or []) if c.communication_type == "Audit"]
				),
			},
			"item_details": {
				"has_gemstones": bool(self.gemstones),
				"gemstone_count": len(self.gemstones) if self.gemstones else 0,
				"has_metal": bool(self.metal_type),
				"metal_type": self.metal_type,
				"metal_purity": self.purity,
			},
			"financial_compliance": {
				"has_deposit": bool(self.deposit_amount and self.deposit_amount > 0),
				"deposit_amount": self.deposit_amount,
				"total_payments": self.get_total_paid(),
				"balance_due": self.balance_due,
				"payment_status": self.payment_status,
			},
			"warranty_compliance": {
				"is_warranty_repair": self.is_warranty_repair,
				"has_warranty": bool(self.warranty_months and self.warranty_months > 0),
				"warranty_months": self.warranty_months,
				"warranty_expiry": self.warranty_expiry_date,
			},
		}

		return report
