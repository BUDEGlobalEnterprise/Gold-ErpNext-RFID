"""CRM <-> POS Integration Hooks.

Document event hooks that automatically create CRM Leads when new customers
are captured in POS, and CRM Deals when high-value sales occur.
"""

import frappe
from frappe import _
from frappe.utils import flt


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------

def _get_crm_setting(field, default=None):
	"""Safely read a custom setting from FCRM Settings."""
	try:
		return frappe.db.get_single_value("FCRM Settings", field)
	except Exception:
		return default


def _is_crm_app_installed():
	"""Check if the Frappe CRM app is installed."""
	return "crm" in frappe.get_installed_apps()


# ---------------------------------------------------------------------------
# Customer after_insert: Walk-in Lead capture
# ---------------------------------------------------------------------------

def on_customer_created(doc, method=None):
	"""
	after_insert hook on Customer.

	Automatically creates a CRM Lead for new walk-in customers,
	unless the customer originated from the CRM app itself.
	"""
	if not _is_crm_app_installed():
		return

	if not _get_crm_setting("custom_auto_create_lead_on_new_customer", 1):
		return

	# Skip if customer was created from CRM Deal flow (already has crm_deal field set)
	crm_deal_value = None
	try:
		crm_deal_value = doc.get("crm_deal") or doc.get("custom_crm_deal")
	except Exception:
		pass
	if crm_deal_value:
		return

	# Skip if flagged as CRM-origin (from erpnext.crm.frappe_crm_api.create_customer)
	if getattr(doc, "flags", None) and getattr(doc.flags, "from_crm", False):
		return

	# Skip bulk imports / data migration
	if getattr(doc, "flags", None) and getattr(doc.flags, "ignore_permissions", False):
		return

	# Duplicate prevention: check if a lead already exists for this email or mobile
	if _existing_lead_for_customer(doc):
		return

	_create_walkin_lead(doc)


def _existing_lead_for_customer(customer_doc):
	"""Check if a CRM Lead already exists matching this customer's email or phone."""
	if customer_doc.email_id:
		if frappe.db.exists("CRM Lead", {"email": customer_doc.email_id, "converted": 0}):
			return True
	if customer_doc.mobile_no:
		if frappe.db.exists("CRM Lead", {"mobile_no": customer_doc.mobile_no, "converted": 0}):
			return True
	# Also check if customer already has a linked lead
	lead_link = None
	try:
		lead_link = customer_doc.get("custom_crm_lead")
	except Exception:
		pass
	if lead_link:
		return True
	return False


def _create_walkin_lead(customer_doc):
	"""Create a CRM Lead from a new walk-in customer."""
	# Parse name into first/last
	name_parts = (customer_doc.customer_name or "").strip().split(" ", 1)
	first_name = name_parts[0] if name_parts else "Unknown"
	last_name = name_parts[1] if len(name_parts) > 1 else ""

	# Ensure Walk-in source exists
	if not frappe.db.exists("CRM Lead Source", "Walk-in"):
		try:
			frappe.get_doc({
				"doctype": "CRM Lead Source",
				"source_name": "Walk-in",
				"details": "Customer walked into the store",
			}).insert(ignore_permissions=True)
		except Exception:
			pass

	# Get default open status
	lead_status = "Open"
	if not frappe.db.exists("CRM Lead Status", lead_status):
		status_row = frappe.db.get_value(
			"CRM Lead Status", {"type": "Open"}, "name", order_by="position asc"
		)
		lead_status = status_row or None

	lead = frappe.get_doc({
		"doctype": "CRM Lead",
		"first_name": first_name,
		"last_name": last_name,
		"lead_name": customer_doc.customer_name,
		"mobile_no": customer_doc.mobile_no,
		"email": customer_doc.email_id,
		"source": "Walk-in" if frappe.db.exists("CRM Lead Source", "Walk-in") else None,
		"status": lead_status,
		"territory": customer_doc.territory,
		"custom_lead_origin": "POS Walk-in",
		"custom_pos_customer": customer_doc.name,
	})

	try:
		lead.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Failed to create CRM Lead for customer {customer_doc.name}",
		)
		return

	# Back-link on customer
	try:
		frappe.db.set_value("Customer", customer_doc.name, "custom_crm_lead", lead.name)
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Failed to link CRM Lead {lead.name} back to Customer {customer_doc.name}",
		)

	# Notify store managers
	_notify_new_walkin_lead(lead, customer_doc)

	return lead.name


# ---------------------------------------------------------------------------
# Sales Invoice on_submit: High-Value Deal creation
# ---------------------------------------------------------------------------

def on_invoice_submit_crm(doc, method=None):
	"""
	on_submit hook on Sales Invoice.

	1. For high-value POS sales, auto-creates a CRM Deal.
	2. For any POS sale with a linked customer deal, updates the deal value.
	"""
	if not _is_crm_app_installed():
		return

	# Only process POS invoices that are not returns
	if not doc.is_pos or doc.is_return:
		return

	if not doc.customer:
		return

	# Update existing deal if linked
	existing_deal = _get_customer_deal(doc.customer)
	if existing_deal:
		_update_deal_with_purchase(existing_deal, doc)
		return

	# Auto-create deal for high-value sales
	if not _get_crm_setting("custom_auto_create_deal_on_high_value", 1):
		return

	threshold = flt(_get_crm_setting("custom_high_value_threshold", 5000))
	if flt(doc.grand_total) < threshold:
		return

	_create_high_value_deal(doc)


def _get_customer_deal(customer_name):
	"""Get the active (open) CRM Deal for a customer, if any."""
	deal_link = None
	try:
		deal_link = frappe.db.get_value("Customer", customer_name, "custom_crm_deal")
	except Exception:
		pass

	if deal_link:
		# Verify deal is still open (not Won/Lost)
		deal_status_type = frappe.db.get_value(
			"CRM Deal Status",
			frappe.db.get_value("CRM Deal", deal_link, "status"),
			"type",
		)
		if deal_status_type in ("Open", "Ongoing", "On Hold"):
			return deal_link

	return None


def _update_deal_with_purchase(deal_name, invoice_doc):
	"""Update an existing CRM Deal with new purchase information."""
	try:
		deal = frappe.get_doc("CRM Deal", deal_name)

		# Accumulate deal value
		current_value = flt(deal.deal_value)
		deal.deal_value = current_value + flt(invoice_doc.grand_total)
		deal.save(ignore_permissions=True)

		# Link invoice to deal
		frappe.db.set_value("Sales Invoice", invoice_doc.name, "custom_crm_deal", deal_name)

		# Add activity log
		_add_deal_activity(
			deal_name,
			f"New purchase: Invoice {invoice_doc.name} for ${flt(invoice_doc.grand_total):,.2f}. "
			f"Total deal value now ${flt(deal.deal_value):,.2f}."
		)
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Failed to update CRM Deal {deal_name} with invoice {invoice_doc.name}",
		)


def _create_high_value_deal(invoice_doc):
	"""Create a CRM Deal from a high-value POS sale."""
	customer = frappe.get_doc("Customer", invoice_doc.customer)

	# Ensure Qualification status exists
	deal_status = "Qualification"
	if not frappe.db.exists("CRM Deal Status", deal_status):
		status_row = frappe.db.get_value(
			"CRM Deal Status", {"type": "Open"}, "name", order_by="position asc"
		)
		deal_status = status_row or None

	# Determine deal owner (salesperson or invoice owner)
	deal_owner = invoice_doc.owner
	# Try to get salesperson from Sales Team child table
	if hasattr(invoice_doc, "sales_team") and invoice_doc.sales_team:
		primary_sp = invoice_doc.sales_team[0]
		if primary_sp.sales_person:
			user = frappe.db.get_value(
				"Sales Person", primary_sp.sales_person, "employee"
			)
			if user:
				deal_owner = frappe.db.get_value("Employee", user, "user_id") or deal_owner

	deal = frappe.get_doc({
		"doctype": "CRM Deal",
		"lead_name": customer.customer_name,
		"organization_name": customer.customer_name,
		"deal_owner": deal_owner,
		"status": deal_status,
		"deal_value": flt(invoice_doc.grand_total),
		"probability": 50,  # Warm lead - they just made a high-value purchase
		"source": "Walk-in" if frappe.db.exists("CRM Lead Source", "Walk-in") else None,
		"territory": customer.territory,
		"custom_pos_customer": invoice_doc.customer,
		"custom_originating_invoice": invoice_doc.name,
	})

	# Link contact info from customer
	if customer.email_id:
		deal.email = customer.email_id
	if customer.mobile_no:
		deal.mobile_no = customer.mobile_no

	try:
		deal.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Failed to create CRM Deal for invoice {invoice_doc.name}",
		)
		return

	# Back-link on customer and invoice
	try:
		frappe.db.set_value("Customer", invoice_doc.customer, "custom_crm_deal", deal.name)
		frappe.db.set_value("Sales Invoice", invoice_doc.name, "custom_crm_deal", deal.name)
	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Failed to back-link CRM Deal {deal.name}",
		)

	# If customer has a CRM Lead, mark it as converted
	lead_link = None
	try:
		lead_link = frappe.db.get_value("Customer", invoice_doc.customer, "custom_crm_lead")
	except Exception:
		pass
	if lead_link:
		try:
			lead = frappe.get_doc("CRM Lead", lead_link)
			if not lead.converted:
				lead.converted = 1
				converted_status = "Converted"
				if not frappe.db.exists("CRM Lead Status", converted_status):
					converted_status = frappe.db.get_value(
						"CRM Lead Status", {"type": "Won"}, "name"
					)
				if converted_status:
					lead.status = converted_status
				lead.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Failed to mark CRM Lead {lead_link} as converted",
			)

	# Notify
	_notify_high_value_deal(deal, invoice_doc)

	return deal.name


# ---------------------------------------------------------------------------
# Activity / notification helpers
# ---------------------------------------------------------------------------

def _add_deal_activity(deal_name, message):
	"""Add a comment/activity to a CRM Deal."""
	try:
		deal = frappe.get_doc("CRM Deal", deal_name)
		deal.add_comment("Info", message)
	except Exception:
		pass


def _notify_new_walkin_lead(lead, customer_doc):
	"""Send notification when a walk-in lead is captured."""
	try:
		title = f"New Walk-in Lead: {lead.lead_name}"
		message = (
			f"A new customer '{customer_doc.customer_name}' was captured in POS. "
			f"Lead {lead.name} created automatically."
		)

		# Notify store managers via notification log
		managers = frappe.get_all(
			"Has Role",
			filters={"role": ["in", ["Store Manager", "Sales Manager"]]},
			fields=["parent"],
			distinct=True,
		)
		for m in managers:
			frappe.get_doc({
				"doctype": "Notification Log",
				"for_user": m.parent,
				"type": "Alert",
				"subject": title,
				"email_content": message,
				"document_type": "CRM Lead",
				"document_name": lead.name,
			}).insert(ignore_permissions=True)

		# Push realtime event for POS dashboard
		frappe.publish_realtime(
			event="crm_new_lead",
			message={"lead": lead.name, "customer": customer_doc.name, "title": title},
		)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to send walk-in lead notification")


def _notify_high_value_deal(deal, invoice_doc):
	"""Send notification when a high-value deal is auto-created."""
	try:
		title = f"High-Value Deal Created: {deal.lead_name}"
		message = (
			f"A deal worth ${flt(deal.deal_value):,.2f} was auto-created from "
			f"invoice {invoice_doc.name}. Deal {deal.name} is now in Qualification."
		)

		managers = frappe.get_all(
			"Has Role",
			filters={"role": ["in", ["Store Manager", "Sales Manager"]]},
			fields=["parent"],
			distinct=True,
		)
		for m in managers:
			frappe.get_doc({
				"doctype": "Notification Log",
				"for_user": m.parent,
				"type": "Alert",
				"subject": title,
				"email_content": message,
				"document_type": "CRM Deal",
				"document_name": deal.name,
			}).insert(ignore_permissions=True)

		frappe.publish_realtime(
			event="crm_new_deal",
			message={
				"deal": deal.name,
				"customer": invoice_doc.customer,
				"value": deal.deal_value,
				"title": title,
			},
		)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to send high-value deal notification")


# ---------------------------------------------------------------------------
# Manual lead creation API (for POS sales associates)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def create_lead_for_customer(customer: str) -> dict:
	"""Manually trigger CRM Lead creation for an existing customer from POS."""
	if not _is_crm_app_installed():
		frappe.throw(_("CRM app is not installed."))

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer))

	if _existing_lead_for_customer(frappe.get_doc("Customer", customer)):
		frappe.throw(_("A CRM Lead already exists for this customer."))

	doc = frappe.get_doc("Customer", customer)
	lead_name = _create_walkin_lead(doc)
	return {"success": True, "lead": lead_name}
