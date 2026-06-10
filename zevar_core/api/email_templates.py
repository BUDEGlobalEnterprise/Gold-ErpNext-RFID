"""
Email Template Migration Utility

Creates Frappe Email Template records for all transactional emails.
Run once via bench console: zevar_core.api.email_templates.install_all_templates()
"""

import frappe
from frappe import _

TEMPLATES = [
	{
		"name": "Repair Order Received",
		"subject": "Repair {{ doc.name }} Received - {{ doc.customer_name }}",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>We have received your repair order <strong>{{ doc.name }}</strong>.</p>"
			"<p>Item: <strong>{{ doc.item_description }}</strong></p>"
			"<p>Our technicians will assess the item and provide an estimate. "
			"We'll notify you once the estimate is ready.</p>"
			"<p>Estimated completion: <strong>{{ doc.estimated_completion or 'TBD' }}</strong></p>"
			"<p>Thank you for trusting us with your repair.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Repair Estimate Ready",
		"subject": "Estimate Ready - Repair {{ doc.name }}",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>The estimate for your repair <strong>{{ doc.name }}</strong> is ready.</p>"
			"<p>Estimated cost: <strong>${{ doc.estimated_cost or '0.00' }}</strong></p>"
			"<p>Please visit our store or call us to approve or discuss the estimate.</p>"
			"<p>{{ company }}</p>"
		),
	},
	{
		"name": "Repair Approved",
		"subject": "Repair {{ doc.name }} Approved - Work Starting",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Your repair <strong>{{ doc.name }}</strong> has been approved and work is starting.</p>"
			"<p>We'll keep you updated on progress.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Repair In Progress",
		"subject": "Repair {{ doc.name }} - Work In Progress",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Work has begun on your repair <strong>{{ doc.name }}</strong>.</p>"
			"<p>Assigned technician: <strong>{{ doc.assigned_technician or 'Our team' }}</strong></p>"
			"<p>We'll notify you when it's ready for pickup.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Repair Waiting Parts",
		"subject": "Repair {{ doc.name }} - Waiting for Parts",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Your repair <strong>{{ doc.name }}</strong> is on hold while we wait for parts to arrive.</p>"
			"<p>We'll notify you as soon as work resumes.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Repair Ready Pickup",
		"subject": "Your Repair {{ doc.name }} is Ready for Pickup!",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Great news! Your repair <strong>{{ doc.name }}</strong> is complete and ready for pickup.</p>"
			"<p>Balance due: <strong>${{ doc.balance_due or '0.00' }}</strong></p>"
			"<p>Please visit us at your earliest convenience.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Repair Delivered",
		"subject": "Repair {{ doc.name }} Delivered - Thank You!",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Your repair <strong>{{ doc.name }}</strong> has been delivered. Thank you for your business!</p>"
			"<p>{{ company }}</p>"
		),
	},
	{
		"name": "Repair Overdue",
		"subject": "Repair {{ doc.name }} - Follow Up Required",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Your completed repair <strong>{{ doc.name }}</strong> is waiting for pickup.</p>"
			"<p>Please pick up your item at your earliest convenience.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Special Order Arrival",
		"subject": "Your Special Order {{ doc.name }} Has Arrived!",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Great news! Your special order <strong>{{ doc.name }}</strong> "
			"has arrived at our store.</p>"
			"<p>Please visit us at your earliest convenience to pick up your item(s).</p>"
			"<p>Balance due: <strong>${{ doc.balance_due or '0.00' }}</strong></p>"
			"<p>{{ company }}</p>"
		),
	},
	{
		"name": "Dunning Level 1 Reminder",
		"subject": "Friendly Reminder - Account {{ doc.account_id }} Payment Due",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>We hope this message finds you well. This is a friendly reminder that your account "
			"<strong>{{ doc.account_id }}</strong> has a balance of "
			"<strong>${{ doc.total_balance }}</strong>.</p>"
			"<p>Minimum payment due: <strong>${{ doc.minimum_due }}</strong></p>"
			"<p>You can make a payment at our store or contact us to arrange a payment schedule.</p>"
			"<p>Thank you for being a valued customer.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Dunning Level 2 Final Notice",
		"subject": "FINAL NOTICE - Account {{ doc.account_id }} Payment Overdue",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Our records indicate that your account <strong>{{ doc.account_id }}</strong> "
			"has an overdue balance of <strong>${{ doc.overdue_amount }}</strong>.</p>"
			"<p>Total balance: <strong>${{ doc.total_balance }}</strong></p>"
			"<p>Minimum payment due: <strong>${{ doc.minimum_due }}</strong></p>"
			"<p>This is your <strong>final notice</strong> before your account is referred to collections.</p>"
			"<p>{{ company }}</p>"
		),
	},
	{
		"name": "Dunning Level 3 Collections",
		"subject": "COLLECTIONS NOTICE - Account {{ doc.account_id }}",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>This is our <strong>final notice</strong> regarding your overdue balance of "
			"<strong>${{ doc.overdue_amount }}</strong> on account "
			"<strong>{{ doc.account_id }}</strong>.</p>"
			"<p>Your account has been referred to our collections department.</p>"
			"<p>Please contact us immediately to arrange payment.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Customer Monthly Statement",
		"subject": "Your {{ doc.period_label }} Statement - Account {{ doc.account_id }}",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Please find your account statement for "
			"<strong>{{ doc.period_label }}</strong> below.</p>"
			"<p><strong>Opening Balance:</strong> ${{ doc.opening_balance }}<br>"
			"<strong>Total Charges:</strong> ${{ doc.total_debits }}<br>"
			"<strong>Total Payments:</strong> ${{ doc.total_credits }}<br>"
			"<strong>Closing Balance:</strong> ${{ doc.closing_balance }}<br>"
			"<strong>Minimum Payment Due:</strong> ${{ doc.minimum_due }}</p>"
			"<p>Thank you for your business.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Layaway Payment Reminder",
		"subject": "Layaway Payment Reminder - {{ doc.name }}",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>This is a reminder that your layaway payment for "
			"<strong>{{ doc.name }}</strong> is due.</p>"
			"<p>Balance remaining: <strong>${{ doc.outstanding_amount or '0.00' }}</strong></p>"
			"<p>Please visit our store to make your payment.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Layaway Overdue Notice",
		"subject": "OVERDUE: Layaway Payment - {{ doc.name }}",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Your layaway <strong>{{ doc.name }}</strong> payment is overdue.</p>"
			"<p>Please make a payment within 7 days to keep your layaway active.<br>{{ company }}</p>"
		),
	},
	{
		"name": "Layaway Forfeit Warning",
		"subject": "URGENT: Layaway {{ doc.name }} At Risk of Forfeiture",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>Your layaway <strong>{{ doc.name }}</strong> is at risk of forfeiture due to non-payment.</p>"
			"<p>Please contact us immediately to discuss your options.<br>{{ company }}</p>"
		),
	},
	{
		"name": "IRS Form 8300 Notification",
		"subject": "Cash Transaction Notification",
		"response_html": (
			"<p>Dear {{ doc.customer_name }},</p>"
			"<p>This is to notify you that a cash transaction report (IRS Form 8300) has been filed "
			"for your recent purchase as required by federal law.</p>"
			"<p>Please retain this for your records.<br>{{ company }}</p>"
		),
	},
	{
		"name": "EOD Brief",
		"subject": "End of Day Summary - {{ date }}",
		"response_html": (
			"<p>End of Day Summary for <strong>{{ date }}</strong></p>"
			"<p>Total Sales: <strong>${{ total_sales }}</strong><br>"
			"Transactions: <strong>{{ transaction_count }}</strong><br>"
			"Cash Variance: <strong>${{ cash_variance }}</strong></p>"
		),
	},
]


def install_all_templates():
	"""Create or update all Email Templates. Run via bench console."""
	installed = 0
	updated = 0

	for tmpl in TEMPLATES:
		if frappe.db.exists("Email Template", tmpl["name"]):
			doc = frappe.get_doc("Email Template", tmpl["name"])
			doc.subject = tmpl["subject"]
			doc.response_html = tmpl["response_html"]
			doc.save(ignore_permissions=True)
			updated += 1
		else:
			doc = frappe.get_doc(
				{
					"doctype": "Email Template",
					"name": tmpl["name"],
					"subject": tmpl["subject"],
					"response_html": tmpl["response_html"],
					"owner": "Administrator",
				}
			)
			doc.insert(ignore_permissions=True)
			installed += 1

	frappe.db.commit()
	return {"installed": installed, "updated": updated, "total": len(TEMPLATES)}


@frappe.whitelist(methods=["GET"])
def get_email_template(template_name: str, context: dict | None = None) -> dict:
	"""Render an email template with context variables."""
	frappe.only_for(["System Manager", "Sales Manager", "Accounts Manager"])

	if not frappe.db.exists("Email Template", template_name):
		frappe.throw(_("Email Template '{0}' not found.").format(template_name))

	from frappe.email.doctype.email_template.email_template import get_email_template as _get
	from frappe.utils.jinja import render_template

	subject, body = _get(template_name, context or {})
	return {"subject": subject, "body": body}
