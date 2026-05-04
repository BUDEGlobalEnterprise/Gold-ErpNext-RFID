"""
Audit Log API - Transaction logging and security tracking

Provides comprehensive audit logging for all POS operations.
"""

import json

import frappe
from frappe import _
from frappe.utils import get_datetime, now_datetime

# Audit event types
AUDIT_EVENTS = {
	# Invoice events
	"invoice_created": {"category": "Sales", "severity": "Info"},
	"invoice_submitted": {"category": "Sales", "severity": "Info"},
	"invoice_cancelled": {"category": "Sales", "severity": "Warning"},
	"invoice_voided": {"category": "Sales", "severity": "Warning"},
	"invoice_returned": {"category": "Sales", "severity": "Warning"},
	# Payment events
	"payment_received": {"category": "Payment", "severity": "Info"},
	"payment_refunded": {"category": "Payment", "severity": "Warning"},
	"split_payment_processed": {"category": "Payment", "severity": "Info"},
	"finance_payment": {"category": "Payment", "severity": "Info"},
	"gift_card_used": {"category": "Payment", "severity": "Info"},
	"gift_card_issued": {"category": "Payment", "severity": "Info"},
	"trade_in_processed": {"category": "Payment", "severity": "Info"},
	# Discount events
	"discount_applied": {"category": "Discount", "severity": "Info"},
	"large_discount_applied": {"category": "Discount", "severity": "Warning"},
	"discount_override_approved": {"category": "Discount", "severity": "Warning"},
	# Session events
	"session_opened": {"category": "Session", "severity": "Info"},
	"session_closed": {"category": "Session", "severity": "Info"},
	"cash_variance_detected": {"category": "Session", "severity": "Warning"},
	# Security events
	"login_success": {"category": "Security", "severity": "Info"},
	"login_failed": {"category": "Security", "severity": "Warning"},
	"manager_override_requested": {"category": "Security", "severity": "Warning"},
	"manager_override_approved": {"category": "Security", "severity": "Warning"},
	"manager_override_rejected": {"category": "Security", "severity": "Warning"},
	"permission_denied": {"category": "Security", "severity": "Warning"},
	# Layaway events
	"layaway_created": {"category": "Layaway", "severity": "Info"},
	"layaway_payment": {"category": "Layaway", "severity": "Info"},
	"layaway_cancelled": {"category": "Layaway", "severity": "Warning"},
	"layaway_completed": {"category": "Layaway", "severity": "Info"},
	# Customer events
	"customer_created": {"category": "Customer", "severity": "Info"},
	"customer_updated": {"category": "Customer", "severity": "Info"},
	# Inventory events
	"stock_adjusted": {"category": "Inventory", "severity": "Warning"},
	"low_stock_alert": {"category": "Inventory", "severity": "Warning"},
}


@frappe.whitelist()
def log_event(
	event_type: str,
	details: str | dict | None = None,
	reference_document: str | None = None,
	reference_type: str | None = None,
):
	"""
	Log an audit event.

	Args:
		event_type: Type of event (must be in AUDIT_EVENTS)
		details: Event details (dict or JSON string)
		reference_document: Related document name
		reference_type: Related document type
	"""
	if event_type not in AUDIT_EVENTS:
		frappe.log_error(f"Unknown audit event type: {event_type}")
		return

	event_config = AUDIT_EVENTS[event_type]

	# Parse details if string
	if isinstance(details, str):
		try:
			details = json.loads(details)
		except (json.JSONDecodeError, TypeError):
			details = {"raw": details}

	# Get client info
	ip_address = None
	user_agent = None
	if hasattr(frappe.local, "request"):
		ip_address = frappe.local.request.get("REMOTE_ADDR")
		user_agent = frappe.local.request.get("HTTP_USER_AGENT", "")[:500]

	# Create audit log entry
	audit_log = frappe.new_doc("POS Audit Log")
	audit_log.user = frappe.session.user
	audit_log.event_type = event_type
	audit_log.category = event_config["category"]
	audit_log.severity = event_config["severity"]
	audit_log.details = json.dumps(details) if details else "{}"
	audit_log.timestamp = now_datetime()
	audit_log.ip_address = ip_address
	audit_log.user_agent = user_agent

	if reference_document:
		audit_log.reference_document = reference_document
	if reference_type:
		audit_log.reference_type = reference_type

	audit_log.insert(ignore_permissions=True)

	# Commit immediately for security events
	if event_config["severity"] == "Warning":
		frappe.db.commit()  # nosemgrep (needed for immediate security event logging)


def log_event_safely(
	event_type: str,
	details: str | dict | None = None,
	reference_document: str | None = None,
	reference_type: str | None = None,
) -> None:
	"""Best-effort audit logging that never interrupts the primary business flow."""
	try:
		log_event(
			event_type=event_type,
			details=details,
			reference_document=reference_document,
			reference_type=reference_type,
		)
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"Failed to log audit event: {event_type}")


@frappe.whitelist()
def get_audit_logs(
	from_date: str | None = None,
	to_date: str | None = None,
	user: str | None = None,
	category: str | None = None,
	severity: str | None = None,
	event_type: str | None = None,
	reference_document: str | None = None,
	page: int = 1,
	page_size: int = 50,
) -> dict:
	"""
	Get audit logs with filtering.

	Args:
		from_date: Start date filter
		to_date: End date filter
		user: User filter
		category: Category filter
		severity: Severity filter
		event_type: Event type filter
		reference_document: Reference document filter
		page: Page number
		page_size: Items per page

	Returns:
		Dictionary with logs and pagination info
	"""
	frappe.has_permission("POS Audit Log", "read", throw=True)

	# Default date range: last 7 days
	if not from_date:
		from_date = frappe.utils.add_days(frappe.utils.today(), -7)
	if not to_date:
		to_date = frappe.utils.today()

	# Build filters
	filters = {"timestamp": ["between", [from_date, to_date]]}

	if user:
		filters["user"] = user
	if category:
		filters["category"] = category
	if severity:
		filters["severity"] = severity
	if event_type:
		filters["event_type"] = event_type
	if reference_document:
		filters["reference_document"] = reference_document

	# Get total count
	total_count = frappe.db.count("POS Audit Log", filters)

	# Calculate offset
	offset = (page - 1) * page_size

	# Get logs
	logs = frappe.get_all(
		"POS Audit Log",
		filters=filters,
		fields=[
			"name",
			"user",
			"event_type",
			"category",
			"severity",
			"details",
			"timestamp",
			"reference_document",
			"reference_type",
			"ip_address",
		],
		order_by="timestamp desc",
		start=offset,
		page_length=page_size,
	)

	# Parse details JSON and batch fetch user full names to avoid N+1
	if logs:
		user_ids = list({log.user for log in logs if log.user})
		user_names = {}
		if user_ids:
			users = frappe.get_all("User", filters={"name": ("in", user_ids)}, fields=["name", "full_name"])
			user_names = {u.name: u.full_name for u in users}

		for log in logs:
			try:
				log["details"] = json.loads(log.get("details", "{}"))
			except (json.JSONDecodeError, TypeError):
				log["details"] = {}

			# Get user full name
			log["user_full_name"] = user_names.get(log.user) or log.user

	return {
		"logs": logs,
		"pagination": {
			"page": page,
			"page_size": page_size,
			"total_count": total_count,
			"total_pages": (total_count + page_size - 1) // page_size,
		},
	}


@frappe.whitelist()
def get_audit_summary(from_date: str | None = None, to_date: str | None = None) -> dict:
	"""
	Get audit log summary statistics.

	Args:
		from_date: Start date filter
		to_date: End date filter

	Returns:
		Summary statistics
	"""
	frappe.has_permission("POS Audit Log", "read", throw=True)

	if not from_date:
		from_date = frappe.utils.add_days(frappe.utils.today(), -7)
	if not to_date:
		to_date = frappe.utils.today()

	# Get counts by category
	category_counts = frappe.db.sql(  # nosemgrep
		"""
		SELECT category, COUNT(*) as count
		FROM `tabPOS Audit Log`
		WHERE timestamp BETWEEN %s AND %s
		GROUP BY category
		ORDER BY count DESC
	""",
		(from_date, to_date),
		as_dict=True,
	)

	# Get counts by severity
	severity_counts = frappe.db.sql(  # nosemgrep
		"""
		SELECT severity, COUNT(*) as count
		FROM `tabPOS Audit Log`
		WHERE timestamp BETWEEN %s AND %s
		GROUP BY severity
	""",
		(from_date, to_date),
		as_dict=True,
	)

	# Get counts by user
	user_counts = frappe.db.sql(  # nosemgrep
		"""
		SELECT user, COUNT(*) as count
		FROM `tabPOS Audit Log`
		WHERE timestamp BETWEEN %s AND %s
		GROUP BY user
		ORDER BY count DESC
		LIMIT 10
	""",
		(from_date, to_date),
		as_dict=True,
	)

	# Get total
	total_count = frappe.db.count("POS Audit Log", {"timestamp": ["between", [from_date, to_date]]})

	# Get warning count
	warning_count = frappe.db.count(
		"POS Audit Log", {"timestamp": ["between", [from_date, to_date]], "severity": "Warning"}
	)

	return {
		"total_events": total_count,
		"warning_events": warning_count,
		"by_category": category_counts,
		"by_severity": severity_counts,
		"by_user": user_counts,
	}


@frappe.whitelist()
def export_audit_logs(
	from_date: str | None = None,
	to_date: str | None = None,
	format: str = "csv",
) -> str:
	"""
	Export audit logs to CSV or Excel.

	Args:
		from_date: Start date filter
		to_date: End date filter
		format: Export format ('csv' or 'excel')

	Returns:
		File URL or content
	"""
	frappe.only_for(["Sales Manager", "System Manager"])

	if not from_date:
		from_date = frappe.utils.add_days(frappe.utils.today(), -30)
	if not to_date:
		to_date = frappe.utils.today()

	# Get logs
	logs = frappe.get_all(
		"POS Audit Log",
		filters={"timestamp": ["between", [from_date, to_date]]},
		fields=[
			"timestamp",
			"user",
			"event_type",
			"category",
			"severity",
			"details",
			"reference_document",
			"reference_type",
			"ip_address",
		],
		order_by="timestamp desc",
		limit_page_length=10000,
	)

	if format == "csv":
		return generate_csv_export(logs)
	else:
		return generate_excel_export(logs)


def generate_csv_export(logs: list) -> str:
	"""Generate CSV export of audit logs."""
	import csv
	import io

	output = io.StringIO()
	writer = csv.writer(output)

	# Header
	writer.writerow(
		[
			"Timestamp",
			"User",
			"Event Type",
			"Category",
			"Severity",
			"Reference Document",
			"Reference Type",
			"IP Address",
			"Details",
		]
	)

	# Data
	for log in logs:
		writer.writerow(
			[
				str(log.get("timestamp", "")),
				log.get("user", ""),
				log.get("event_type", ""),
				log.get("category", ""),
				log.get("severity", ""),
				log.get("reference_document", ""),
				log.get("reference_type", ""),
				log.get("ip_address", ""),
				log.get("details", ""),
			]
		)

	# Save file
	file_name = f"audit_log_export_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.csv"
	file_path = frappe.get_site_path("public", "files", file_name)

	with open(file_path, "w") as f:  # nosemgrep (safe site-internal file export)
		f.write(output.getvalue())

	return f"/files/{file_name}"


def generate_excel_export(logs: list) -> str:
	"""Generate Excel export of audit logs."""
	# For simplicity, fall back to CSV (Excel can open CSV)
	return generate_csv_export(logs)
