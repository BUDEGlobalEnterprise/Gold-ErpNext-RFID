"""
Tax Exemption API - Exemption oversight, approval, and misuse detection

Provides endpoints for:
- Requesting a tax exemption on a POS invoice
- Approving/rejecting exemption requests
- Querying exemption logs and misuse flags
- Manager dashboard data for tax exemptions
"""

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, now_datetime, today


@frappe.whitelist(methods=["POST"])
def request_tax_exemption(
	sales_invoice: str,
	customer: str,
	exemption_reason: str,
	certificate_ref: str | None = None,
) -> dict:
	"""
	Cashier requests a tax exemption on a POS invoice.
	Creates a POS Tax Exemption Log with Pending status and notifies manager.
	"""
	frappe.only_for(["Sales User", "Sales Manager", "Store Manager", "System Manager"])

	if not sales_invoice or not frappe.db.exists("Sales Invoice", sales_invoice):
		frappe.throw(_("Sales Invoice '{0}' not found.").format(sales_invoice or ""))

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer or ""))

	if exemption_reason == "Resale Certificate" and not certificate_ref:
		frappe.throw(_("Certificate reference is required for Resale exemptions."))

	# Validate certificate if provided
	if certificate_ref:
		if not frappe.db.exists("Tax Exemption Certificate", certificate_ref):
			frappe.throw(_("Tax Exemption Certificate '{0}' not found.").format(certificate_ref))

		cert = frappe.get_doc("Tax Exemption Certificate", certificate_ref)
		if cert.status != "Active":
			frappe.throw(
				_("Certificate '{0}' is {1}. Only Active certificates are accepted.").format(
					certificate_ref, cert.status
				)
			)
		if cert.expiry_date and getdate(cert.expiry_date) < getdate():
			frappe.throw(_("Certificate '{0}' expired on {1}.").format(certificate_ref, cert.expiry_date))
		if cert.customer != customer:
			frappe.throw(
				_("Certificate '{0}' does not belong to customer '{1}'.").format(certificate_ref, customer)
			)

	# Check for misuse: count exemptions for this customer in rolling 30 days
	misuse_flag, misuse_details = _check_misuse(customer)

	log = frappe.new_doc("POS Tax Exemption Log")
	log.sales_invoice = sales_invoice
	log.customer = customer
	log.exemption_reason = exemption_reason
	log.certificate_ref = certificate_ref
	log.applied_by = frappe.session.user
	log.applied_at = now_datetime()
	log.approval_status = "Pending"
	log.misuse_flag = 1 if misuse_flag else 0
	log.misuse_details = misuse_details or ""
	log.insert(ignore_permissions=True)

	# Mark the invoice as tax-exempt pending
	frappe.db.set_value(
		"Sales Invoice",
		sales_invoice,
		{
			"custom_no_tax_override": 1,
			"custom_tax_override_reason": exemption_reason,
			"custom_tax_exemption_status": "Pending",
			"custom_tax_exemption_log": log.name,
		},
	)

	# Notify managers
	_notify_managers_exemption(
		"tax_exemption_requested",
		{
			"event_type": "tax_exemption_requested",
			"log_name": log.name,
			"sales_invoice": sales_invoice,
			"customer": customer,
			"exemption_reason": exemption_reason,
			"misuse_flag": misuse_flag,
			"requested_by": frappe.session.user,
			"timestamp": str(now_datetime()),
		},
	)

	return {
		"success": True,
		"log_name": log.name,
		"approval_status": "Pending",
		"misuse_flag": misuse_flag,
		"message": _("Tax exemption request submitted. Awaiting manager approval."),
	}


@frappe.whitelist(methods=["POST"])
def approve_tax_exemption(log_name: str, rejection_reason: str | None = None) -> dict:
	"""
	Manager approves or rejects a tax exemption request.
	Set rejection_reason to reject; omit to approve.
	"""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	if not log_name or not frappe.db.exists("POS Tax Exemption Log", log_name):
		frappe.throw(_("Tax Exemption Log '{0}' not found.").format(log_name or ""))

	log = frappe.get_doc("POS Tax Exemption Log", log_name)

	if log.approval_status != "Pending":
		frappe.throw(_("This exemption request is already {0}.").format(log.approval_status))

	if rejection_reason:
		log.approval_status = "Rejected"
		log.approved_by = frappe.session.user
		log.approved_at = now_datetime()
		log.rejection_reason = rejection_reason
		log.save(ignore_permissions=True)

		# Re-enable tax on the invoice
		frappe.db.set_value(
			"Sales Invoice",
			log.sales_invoice,
			{
				"custom_no_tax_override": 0,
				"custom_tax_override_reason": "",
				"custom_tax_exemption_status": "Rejected",
			},
		)

		_notify_managers_exemption(
			"tax_exemption_rejected",
			{
				"event_type": "tax_exemption_rejected",
				"log_name": log_name,
				"sales_invoice": log.sales_invoice,
				"rejection_reason": rejection_reason,
			},
		)

		return {
			"success": True,
			"status": "Rejected",
			"message": _("Tax exemption rejected. Tax will be applied to the invoice."),
		}
	else:
		# Re-validate certificate before approving
		if log.certificate_ref:
			cert = frappe.get_doc("Tax Exemption Certificate", log.certificate_ref)
			if cert.status != "Active":
				frappe.throw(_("Certificate is no longer Active. Cannot approve."))
			if cert.expiry_date and getdate(cert.expiry_date) < getdate():
				frappe.throw(_("Certificate expired on {0}. Cannot approve.").format(cert.expiry_date))

		log.approval_status = "Approved"
		log.approved_by = frappe.session.user
		log.approved_at = now_datetime()
		log.save(ignore_permissions=True)

		frappe.db.set_value(
			"Sales Invoice",
			log.sales_invoice,
			{
				"custom_tax_exemption_status": "Approved",
				"custom_tax_override_approved_by": frappe.session.user,
			},
		)

		_notify_managers_exemption(
			"tax_exemption_approved",
			{
				"event_type": "tax_exemption_approved",
				"log_name": log_name,
				"sales_invoice": log.sales_invoice,
				"approved_by": frappe.session.user,
			},
		)

		return {
			"success": True,
			"status": "Approved",
			"message": _("Tax exemption approved."),
		}


@frappe.whitelist(methods=["GET"])
def get_pending_exemptions() -> dict:
	"""Get all pending tax exemption requests for the manager dashboard."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	logs = frappe.get_all(
		"POS Tax Exemption Log",
		filters={"approval_status": "Pending"},
		fields=[
			"name",
			"sales_invoice",
			"customer",
			"exemption_reason",
			"certificate_ref",
			"applied_by",
			"applied_at",
			"misuse_flag",
			"misuse_details",
		],
		order_by="applied_at asc",
	)

	# Enrich with user names and customer names
	for log in logs:
		log["applied_by_name"] = frappe.db.get_value("User", log.applied_by, "full_name") or log.applied_by
		log["customer_name"] = frappe.db.get_value("Customer", log.customer, "customer_name") or log.customer
		log["invoice_total"] = flt(
			frappe.db.get_value("Sales Invoice", log.sales_invoice, "grand_total") or 0
		)

	return {"exemptions": logs, "count": len(logs)}


@frappe.whitelist(methods=["GET"])
def get_exemption_history(customer: str | None = None, days: int = 30) -> dict:
	"""Get tax exemption history, optionally filtered by customer."""
	frappe.only_for(["Sales Manager", "Store Manager", "System Manager"])

	filters = {"creation": [">=", add_days(today(), -int(days))]}
	if customer:
		filters["customer"] = customer

	logs = frappe.get_all(
		"POS Tax Exemption Log",
		filters=filters,
		fields=[
			"name",
			"sales_invoice",
			"customer",
			"exemption_reason",
			"approval_status",
			"applied_by",
			"applied_at",
			"approved_by",
			"approved_at",
			"misuse_flag",
		],
		order_by="applied_at desc",
		limit=200,
	)

	for log in logs:
		log["customer_name"] = frappe.db.get_value("Customer", log.customer, "customer_name") or log.customer

	return {"exemptions": logs, "count": len(logs)}


@frappe.whitelist(methods=["GET"])
def get_customer_certificates(customer: str) -> dict:
	"""Get all tax exemption certificates for a customer."""
	frappe.only_for(["Sales User", "Sales Manager", "Store Manager", "System Manager"])

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer '{0}' not found.").format(customer or ""))

	certificates = frappe.get_all(
		"Tax Exemption Certificate",
		filters={"customer": customer},
		fields=[
			"name",
			"certificate_number",
			"certificate_type",
			"issuing_state",
			"issue_date",
			"expiry_date",
			"status",
		],
		order_by="creation desc",
	)

	# Auto-expire certificates past their expiry date
	for cert in certificates:
		if cert.status == "Active" and cert.expiry_date and getdate(cert.expiry_date) < getdate():
			frappe.db.set_value("Tax Exemption Certificate", cert.name, "status", "Expired")
			cert.status = "Expired"

	return {"certificates": certificates, "count": len(certificates)}


def validate_exemption_on_submit(doc, method=None):
	"""
	Hook: Sales Invoice before_submit.
	Block submission if tax exemption is pending approval.
	"""
	if not doc.is_pos:
		return

	if not getattr(doc, "custom_no_tax_override", 0):
		return

	exemption_status = getattr(doc, "custom_tax_exemption_status", None)
	if exemption_status == "Pending":
		frappe.throw(
			_(
				"This invoice has a pending tax exemption request. "
				"Manager approval is required before submission."
			),
			title=_("Tax Exemption Pending Approval"),
		)

	if exemption_status == "Rejected":
		frappe.throw(
			_(
				"Tax exemption was rejected for this invoice. "
				"Please remove the tax override or resolve the exemption."
			),
			title=_("Tax Exemption Rejected"),
		)


def _check_misuse(customer: str, threshold_days: int = 30, threshold_count: int = 5) -> tuple[bool, str]:
	"""
	Check if a customer has been tax-exempted suspiciously often.
	Returns (is_misuse, details_string).
	"""
	cutoff = add_days(today(), -threshold_days)
	recent = frappe.get_all(
		"POS Tax Exemption Log",
		filters={
			"customer": customer,
			"creation": [">=", cutoff],
		},
		fields=["name", "exemption_reason", "applied_at"],
		order_by="applied_at desc",
	)

	count = len(recent)
	if count >= threshold_count:
		reasons = ", ".join(set(r.exemption_reason for r in recent))
		details = (
			f"Customer has {count} tax exemptions in {threshold_days} days "
			f"(threshold: {threshold_count}). Reasons: {reasons}"
		)
		return True, details

	return False, ""


def _notify_managers_exemption(event_name: str, data: dict) -> None:
	"""Send a realtime event to all manager-role users about a tax exemption event."""
	try:
		managers = frappe.get_all(
			"Has Role",
			filters={"role": ["in", ["Sales Manager", "Store Manager"]], "parenttype": "User"},
			fields=["parent"],
		)
		for mgr in managers:
			frappe.publish_realtime(event_name, data, user=mgr.parent)
	except Exception:
		frappe.log_error("Tax Exemption Manager Notification Failed", frappe.get_traceback())
