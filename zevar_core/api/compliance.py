"""
Compliance API - IRS Form 8300 and AML/KYC Automation

Automated tracking of cash transactions, structuring detection,
and identity verification workflows.
"""

import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, flt, getdate, now_datetime, today


@frappe.whitelist()
def check_cash_reporting_required(customer):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.irs_8300_tracking_enabled:
		return {"required": False, "message": "8300 tracking is disabled"}
	threshold = flt(settings.get("cash_threshold_8300") or 10000)
	total_cash = _get_customer_cash_total(customer)
	records = frappe.get_all(
		"IRS Form 8300 Record",
		filters={"customer": customer, "docstatus": ["!=", 2]},
		fields=["name", "total_cash_amount", "status", "trigger_date"],
		order_by="trigger_date desc",
	)
	return {
		"required": total_cash >= threshold,
		"total_cash": flt(total_cash),
		"threshold": threshold,
		"existing_records": records,
	}


@frappe.whitelist(methods=["POST"])
def trigger_form_8300(customer, total_amount, transaction_details=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "POS User", "POS Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.irs_8300_tracking_enabled:
		return {"success": False, "message": "8300 tracking is disabled"}
	customer_doc = frappe.get_doc("Customer", customer)
	customer_name = customer_doc.customer_name or ""
	record = frappe.new_doc("IRS Form 8300 Record")
	record.customer = customer
	record.status = "Triggered"
	record.trigger_date = now_datetime()
	record.total_cash_amount = flt(total_amount)
	if isinstance(transaction_details, dict):
		record.transaction_details = frappe.as_json(transaction_details)
		irs_details = transaction_details.get("irs_8300_details", {})
		if irs_details:
			if irs_details.get("bypassed_by"):
				notes_text = f"Bypass Authorized By: {irs_details['bypassed_by']}\nReason: {irs_details.get('bypass_reason', 'None')}"
				record.notes = notes_text
			else:
				record.recipient_name = irs_details.get("recipient_name") or customer_name
				record.recipient_tin = irs_details.get("recipient_tin")
				record.recipient_address = irs_details.get("recipient_address")
				record.recipient_dob = irs_details.get("recipient_dob")
				record.recipient_id_type = irs_details.get("recipient_id_type")
				record.recipient_id_number = irs_details.get("recipient_id_number")
	else:
		record.transaction_details = transaction_details or "{}"
		record.recipient_name = customer_name

	if settings.auto_populate_8300 and not record.recipient_address:
		customer_email = frappe.db.get_value("Contact Email", {"parent": customer}, "email_id")
		customer_address = frappe.db.get_value(
			"Address", {"link_name": customer}, ["address_line1", "city", "state", "pincode"], as_dict=True
		)
		if customer_email:
			record.notes = (record.notes + f"\nCustomer email: {customer_email}") if record.notes else f"Customer email: {customer_email}"
		if customer_address:
			record.recipient_address = f"{customer_address.get('address_line1', '')}, {customer_address.get('city', '')}, {customer_address.get('state', '')} {customer_address.get('pincode', '')}"
	
	record.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"success": True, "record_name": record.name, "message": _("Form 8300 record created.")}


@frappe.whitelist(methods=["POST"])
def verify_customer_identity(customer, id_type, id_number, id_state=None, id_expiration=None, scan_data=None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.aml_kyc_enabled:
		return {"success": False, "message": "AML/KYC is disabled"}
	customer_doc = frappe.get_doc("Customer", customer)
	customer_name = customer_doc.customer_name or ""
	record = frappe.new_doc("AML KYC Record")
	record.customer = customer
	record.verification_type = "High-Value Transaction"
	record.status = "Pending"
	id_type_map = {
		"Driver License": "Driver's License",
		"Drivers License": "Driver's License",
		"drivers license": "Driver's License",
		"drivers_license": "Driver's License",
		"driversLicense": "Driver's License",
	}
	record.id_type = id_type_map.get(id_type, id_type)
	record.id_number = id_number
	record.id_issuing_state = id_state
	record.id_expiration = id_expiration
	record.full_name = customer_name
	record.id_scan_data = scan_data or "{}"
	if scan_data:
		try:
			import json

			scan = json.loads(scan_data)
			record.full_name = scan.get("name", customer_name)
			record.address = scan.get("address", "")
			record.date_of_birth = scan.get("dob", "")
		except Exception:
			pass
	risk_level = _assess_risk_level(customer)
	record.risk_level = risk_level
	record.insert(ignore_permissions=True)
	if risk_level in ("High", "Critical"):
		record.status = "Flagged"
		record.risk_flags = _generate_risk_flags(customer)
		record.save(ignore_permissions=True)
		if settings.aml_officer_email:
			_notify_aml_officer(record.name, customer_name, risk_level)
	frappe.db.commit()
	return {
		"success": True,
		"record_name": record.name,
		"risk_level": risk_level,
		"status": record.status,
	}


def _get_customer_cash_total(customer, window_days=365):
	from frappe.query_builder import DocType

	SalesInvoice = DocType("Sales Invoice")
	SalesInvoicePayment = DocType("Sales Invoice Payment")
	cutoff = getdate(add_days(today(), -window_days))
	si_result = (
		frappe.qb.from_(SalesInvoicePayment)
		.join(SalesInvoice)
		.on(SalesInvoice.name == SalesInvoicePayment.parent)
		.select(Sum(SalesInvoicePayment.amount).as_("total_cash"))
		.where(SalesInvoice.customer == customer)
		.where(SalesInvoice.docstatus == 1)
		.where(SalesInvoice.is_return == 0)
		.where(SalesInvoice.posting_date >= cutoff)
		.where(SalesInvoicePayment.mode_of_payment == "Cash")
		.run(as_dict=True)
	)
	si_cash = flt(si_result[0].get("total_cash", 0)) if si_result else 0.0

	LayawayContract = DocType("Layaway Contract")
	LayawayPayment = DocType("Layaway Payment Schedule")
	layaway_result = (
		frappe.qb.from_(LayawayPayment)
		.join(LayawayContract)
		.on(LayawayContract.name == LayawayPayment.parent)
		.select(Sum(LayawayPayment.paid_amount).as_("total_cash"))
		.where(LayawayContract.customer == customer)
		.where(LayawayContract.docstatus == 1)
		.where(LayawayPayment.status == "Paid")
		.where(LayawayPayment.payment_date >= cutoff)
		.where(LayawayPayment.mode_of_payment == "Cash")
		.run(as_dict=True)
	)
	layaway_cash = flt(layaway_result[0].get("total_cash", 0)) if layaway_result else 0.0

	return si_cash + layaway_cash


def _assess_risk_level(customer):
	recent_cash = _get_customer_cash_total(customer, window_days=90)
	if recent_cash > 50000:
		return "Critical"
	if recent_cash > 25000:
		return "High"
	if recent_cash > 10000:
		return "Medium"
	return "Low"


def _generate_risk_flags(customer):
	flags = []
	recent_cash = _get_customer_cash_total(customer, window_days=30)
	if recent_cash > 10000:
		flags.append("High cash volume in 30 days")
	transactions = frappe.get_all(
		"Sales Invoice",
		filters={
			"customer": customer,
			"docstatus": 1,
			"is_return": 0,
			"posting_date": [">=", add_days(today(), -30)],
		},
		fields=["count(*) as cnt"],
	)
	if transactions and transactions[0].cnt > 10:
		flags.append("Frequent transactions (possible structuring)")
	return "; ".join(flags)


def _notify_aml_officer(record_name, customer_name, risk_level):
	try:
		subject = f"AML Alert: {risk_level} Risk - {customer_name}"
		message = f"""
A customer has been flagged with {risk_level} risk level during KYC verification.

KYC Record: {record_name}
Customer: {customer_name}
Risk Level: {risk_level}

Please review this record and take appropriate action.
"""
		frappe.sendmail(
			recipients=[frappe.get_single("Payment Gateway Settings").aml_officer_email],
			subject=subject,
			message=message,
			reference_doctype="AML KYC Record",
			reference_name=record_name,
		)
	except Exception:
		frappe.log_error("Failed to send AML notification", "AML/KYC")


def check_cash_transaction_for_8300(customer, cash_amount):
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.irs_8300_tracking_enabled:
		return False
	threshold = flt(settings.get("cash_threshold_8300") or 10000)
	total_cash = _get_customer_cash_total(customer) + flt(cash_amount)
	return total_cash >= threshold


@frappe.whitelist()
def check_pre_8300_status(customer, cash_amount):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "POS User", "POS Manager"])
	triggered = check_cash_transaction_for_8300(customer, cash_amount)
	return {"triggered": triggered}


def scan_cash_transactions():
	"""
	Scheduled Job: Scan all customers for cash transactions exceeding the 8300 threshold.
	Runs daily at 6 AM. Evaluates cash transactions within a 12-month rolling window.
	"""
	settings = frappe.get_single("Payment Gateway Settings")
	if not settings.irs_8300_tracking_enabled:
		return
	threshold = flt(settings.get("cash_threshold_8300") or 10000)
	from frappe.query_builder import DocType, functions

	SalesInvoice = DocType("Sales Invoice")
	SalesInvoicePayment = DocType("Sales Invoice Payment")
	cutoff = getdate(add_days(today(), -365))
	results = (
		frappe.qb.from_(SalesInvoicePayment)
		.join(SalesInvoice)
		.on(SalesInvoice.name == SalesInvoicePayment.parent)
		.select(
			SalesInvoice.customer,
			functions.Sum(SalesInvoicePayment.amount).as_("total_cash"),
		)
		.where(SalesInvoice.docstatus == 1)
		.where(SalesInvoice.is_return == 0)
		.where(SalesInvoice.posting_date >= cutoff)
		.where(SalesInvoicePayment.mode_of_payment == "Cash")
		.groupby(SalesInvoice.customer)
		.having(functions.Sum(SalesInvoicePayment.amount) >= threshold)
		.run(as_dict=True)
	)
	for row in results:
		customer = row.customer
		total_cash = flt(row.total_cash)
		existing = frappe.get_all(
			"IRS Form 8300 Record",
			filters={"customer": customer, "status": "Triggered"},
			limit=1,
		)
		if existing:
			continue
		try:
			trigger_form_8300(customer, total_cash)
		except Exception:
			frappe.log_error(f"Failed to create 8300 record for {customer}", "Compliance Scanner")
