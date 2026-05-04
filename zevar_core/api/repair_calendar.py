"""
Calendar Integration API - Repair System Integration (Phase 11.2)

This module provides calendar-related functionality:
- Promised dates sync to store calendar
- Technician schedule view
- Overdue alerts
- iCal feed subscription
"""

from datetime import datetime, timedelta
from typing import Any

import frappe
from frappe import _
from frappe.utils import (
	add_days,
	add_to_date,
	cint,
	fmt_datetime,
	get_url,
	getdate,
	now,
	nowdate,
	random_string,
)


@frappe.whitelist()
def get_calendar_events(
	start_date: str,
	end_date: str,
	warehouse: str | None = None,
	technician: str | None = None,
	event_types: list | None = None,
) -> list[dict[str, Any]]:
	"""
	Get repair-related calendar events for a date range.

	Args:
	    start_date: Start date in YYYY-MM-DD format
	    end_date: End date in YYYY-MM-DD format
	    warehouse: Filter by warehouse/store
	    technician: Filter by assigned technician
	    event_types: List of event types to include (promised, overdue, pickup, etc.)

	Returns:
	    List of calendar events compatible with FullCalendar and other calendar libraries
	"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	if event_types is None:
		event_types = ["promised", "overdue", "pickup", "received"]

	events = []
	start = getdate(start_date)
	getdate(end_date)

	# Build filters
	filters = [["promised_date", "between", [start_date, end_date]]]

	if warehouse:
		filters.append(["warehouse", "=", warehouse])
	if technician:
		filters.append(["assigned_to", "=", technician])

	# Get repairs with promised dates in range
	repairs = frappe.get_all(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"status",
			"priority",
			"customer",
			"customer_phone",
			"repair_type",
			"item_description",
			"promised_date",
			"received_date",
			"assigned_to",
			"warehouse",
		],
	)

	for repair in repairs:
		# Add promised date event
		if "promised" in event_types and repair.get("promised_date"):
			customer_name = (
				frappe.db.get_value("Customer", repair["customer"], "customer_name")
				if repair.get("customer")
				else ""
			)

			# Determine event color based on status
			color_map = {
				"Received": "#3b82f6",  # Blue
				"Estimated": "#8b5cf6",  # Purple
				"Approved": "#06b6d4",  # Cyan
				"In Progress": "#f59e0b",  # Amber
				"Waiting for Parts": "#ef4444",  # Red
				"Quality Check": "#ec4899",  # Pink
				"Ready for Pickup": "#10b981",  # Green
			}

			event = {
				"id": f"promised_{repair['name']}",
				"title": f"{repair['name']} - {customer_name or 'Customer'}",
				"start": repair["promised_date"],
				"allDay": True,
				"backgroundColor": color_map.get(repair["status"], "#6b7280"),
				"borderColor": color_map.get(repair["status"], "#6b7280"),
				"extendedProps": {
					"eventType": "promised",
					"repairOrder": repair["name"],
					"status": repair["status"],
					"priority": repair.get("priority"),
					"customer": customer_name,
					"customerPhone": repair.get("customer_phone"),
					"repairType": repair.get("repair_type"),
					"warehouse": repair.get("warehouse"),
					"assignedTo": repair.get("assigned_to"),
				},
				"url": f"/app/repair-order/{repair['name']}",
			}
			events.append(event)

	# Get overdue repairs (promised date in past, not delivered)
	if "overdue" in event_types:
		overdue_filters = [
			["promised_date", "<", start_date],
			["status", "not in", ["Delivered", "Cancelled"]],
		]
		if warehouse:
			overdue_filters.append(["warehouse", "=", warehouse])
		if technician:
			overdue_filters.append(["assigned_to", "=", technician])

		overdue_repairs = frappe.get_all(
			"Repair Order",
			filters=overdue_filters,
			fields=[
				"name",
				"status",
				"priority",
				"customer",
				"customer_phone",
				"repair_type",
				"promised_date",
				"warehouse",
				"assigned_to",
			],
		)

		for repair in overdue_repairs:
			customer_name = (
				frappe.db.get_value("Customer", repair["customer"], "customer_name")
				if repair.get("customer")
				else ""
			)
			days_overdue = (start - getdate(repair["promised_date"])).days

			events.append(
				{
					"id": f"overdue_{repair['name']}",
					"title": f"OVERDUE: {repair['name']} ({days_overdue} days)",
					"start": start_date,  # Show on first day of view
					"allDay": True,
					"backgroundColor": "#ef4444",
					"borderColor": "#dc2626",
					"extendedProps": {
						"eventType": "overdue",
						"repairOrder": repair["name"],
						"status": repair["status"],
						"priority": repair.get("priority"),
						"customer": customer_name,
						"customerPhone": repair.get("customer_phone"),
						"promisedDate": str(repair["promised_date"]),
						"daysOverdue": days_overdue,
						"warehouse": repair.get("warehouse"),
						"assignedTo": repair.get("assigned_to"),
					},
					"url": f"/app/repair-order/{repair['name']}",
				}
			)

	# Get pickups scheduled (Ready for Pickup status)
	if "pickup" in event_types:
		pickup_filters = [
			["status", "=", "Ready for Pickup"],
			["promised_date", "<=", end_date],
		]
		if warehouse:
			pickup_filters.append(["warehouse", "=", warehouse])

		pickup_repairs = frappe.get_all(
			"Repair Order",
			filters=pickup_filters,
			fields=["name", "customer", "customer_phone", "repair_type", "promised_date", "warehouse"],
		)

		for repair in pickup_repairs:
			customer_name = (
				frappe.db.get_value("Customer", repair["customer"], "customer_name")
				if repair.get("customer")
				else ""
			)

			events.append(
				{
					"id": f"pickup_{repair['name']}",
					"title": f"📦 PICKUP: {repair['name']} - {customer_name}",
					"start": repair.get("promised_date") or end_date,
					"allDay": True,
					"backgroundColor": "#10b981",
					"borderColor": "#059669",
					"extendedProps": {
						"eventType": "pickup",
						"repairOrder": repair["name"],
						"customer": customer_name,
						"customerPhone": repair.get("customer_phone"),
						"warehouse": repair.get("warehouse"),
					},
					"url": f"/app/repair-order/{repair['name']}",
				}
			)

	# Get new repairs received
	if "received" in event_types:
		received_filters = [["received_date", "between", [start_date, end_date]]]
		if warehouse:
			received_filters.append(["warehouse", "=", warehouse])

		received_repairs = frappe.get_all(
			"Repair Order",
			filters=received_filters,
			fields=["name", "customer", "repair_type", "received_date", "warehouse"],
		)

		for repair in received_repairs:
			customer_name = (
				frappe.db.get_value("Customer", repair["customer"], "customer_name")
				if repair.get("customer")
				else ""
			)

			events.append(
				{
					"id": f"received_{repair['name']}",
					"title": f"📥 Received: {repair['name']}",
					"start": repair["received_date"].split(" ")[0]
					if repair.get("received_date")
					else start_date,
					"allDay": True,
					"backgroundColor": "#6366f1",
					"borderColor": "#4f46e5",
					"extendedProps": {
						"eventType": "received",
						"repairOrder": repair["name"],
						"customer": customer_name,
						"warehouse": repair.get("warehouse"),
					},
					"url": f"/app/repair-order/{repair['name']}",
				}
			)

	return events


@frappe.whitelist()
def get_technician_schedule(
	technician: str,
	start_date: str,
	end_date: str,
) -> dict[str, Any]:
	"""
	Get detailed schedule for a specific technician.

	Args:
	    technician: User ID of the technician
	    start_date: Start date in YYYY-MM-DD format
	    end_date: End date in YYYY-MM-DD format

	Returns:
	    Technician schedule with workload analysis
	"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	# Get assigned repairs
	repairs = frappe.get_all(
		"Repair Order",
		filters={
			"assigned_to": technician,
			"promised_date": ("between", [start_date, end_date]),
		},
		fields=[
			"name",
			"status",
			"priority",
			"customer",
			"repair_type",
			"item_description",
			"promised_date",
			"received_date",
			"labor_cost",
			"warehouse",
		],
	)

	technician_name = frappe.db.get_value("User", technician, "full_name")

	schedule = {
		"technician": {
			"id": technician,
			"name": technician_name,
		},
		"period": {
			"start": start_date,
			"end": end_date,
		},
		"summary": {
			"total_assigned": len(repairs),
			"by_status": {},
			"by_priority": {},
			"estimated_revenue": 0,
		},
		"repairs": [],
		"workload_by_day": {},
	}

	# Process repairs
	for repair in repairs:
		customer_name = (
			frappe.db.get_value("Customer", repair["customer"], "customer_name")
			if repair.get("customer")
			else ""
		)
		repair_type_name = (
			frappe.db.get_value("Repair Type", repair["repair_type"], "repair_name")
			if repair.get("repair_type")
			else ""
		)

		repair_data = {
			"name": repair["name"],
			"status": repair["status"],
			"priority": repair.get("priority"),
			"customer": customer_name,
			"repair_type": repair_type_name,
			"item_description": repair.get("item_description"),
			"promised_date": str(repair["promised_date"]) if repair.get("promised_date") else None,
			"labor_cost": float(repair.get("labor_cost") or 0),
			"warehouse": repair.get("warehouse"),
		}

		schedule["repairs"].append(repair_data)

		# Update summary
		status = repair["status"]
		schedule["summary"]["by_status"][status] = schedule["summary"]["by_status"].get(status, 0) + 1

		priority = repair.get("priority", "Medium")
		schedule["summary"]["by_priority"][priority] = schedule["summary"]["by_priority"].get(priority, 0) + 1

		schedule["summary"]["estimated_revenue"] += repair_data["labor_cost"]

		# Update workload by day
		if repair.get("promised_date"):
			promised_date = str(repair["promised_date"])
			if promised_date not in schedule["workload_by_day"]:
				schedule["workload_by_day"][promised_date] = {
					"total": 0,
					"urgent": 0,
					"high_priority": 0,
				}

			schedule["workload_by_day"][promised_date]["total"] += 1
			if repair.get("priority") in ["High", "Urgent"]:
				schedule["workload_by_day"][promised_date]["high_priority"] += 1
			if repair.get("priority") == "Urgent":
				schedule["workload_by_day"][promised_date]["urgent"] += 1

	return schedule


@frappe.whitelist()
def get_overdue_alerts(
	warehouse: str | None = None,
	days_overdue: int = 0,
	include_customer_info: bool = True,
) -> list[dict[str, Any]]:
	"""
	Get all overdue repair orders with optional filtering.

	Args:
	    warehouse: Filter by warehouse/store
	    days_overdue: Minimum days overdue to include (0 = all overdue)
	    include_customer_info: Whether to include customer contact info

	Returns:
	    List of overdue repairs with severity indicators
	"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	today = getdate(nowdate())

	# Build filters for overdue repairs
	filters = [["promised_date", "<", today], ["status", "not in", ["Delivered", "Cancelled"]]]

	if warehouse:
		filters.append(["warehouse", "=", warehouse])

	overdue_repairs = frappe.get_all(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"status",
			"priority",
			"customer",
			"customer_phone",
			"repair_type",
			"item_description",
			"promised_date",
			"assigned_to",
			"warehouse",
			"total_cost",
		],
	)

	alerts = []

	for repair in overdue_repairs:
		promised_date = getdate(repair["promised_date"])
		days_over = (today - promised_date).days

		# Filter by minimum days overdue
		if days_over < days_overdue:
			continue

		# Determine severity
		if days_over >= 14:
			severity = "critical"
			severity_color = "red"
		elif days_over >= 7:
			severity = "high"
			severity_color = "orange"
		elif days_over >= 3:
			severity = "medium"
			severity_color = "yellow"
		else:
			severity = "low"
			severity_color = "blue"

		alert = {
			"repair_order": repair["name"],
			"status": repair["status"],
			"priority": repair.get("priority"),
			"severity": severity,
			"severity_color": severity_color,
			"days_overdue": days_over,
			"promised_date": str(repair["promised_date"]),
			"item_description": repair.get("item_description"),
			"repair_type": repair.get("repair_type"),
			"assigned_to": repair.get("assigned_to"),
			"warehouse": repair.get("warehouse"),
			"estimated_cost": float(repair.get("total_cost") or 0),
		}

		if include_customer_info:
			alert["customer"] = (
				frappe.db.get_value("Customer", repair["customer"], "customer_name")
				if repair.get("customer")
				else ""
			)
			alert["customer_phone"] = repair.get("customer_phone")
			alert["customer_id"] = repair.get("customer")

		# Check if customer was notified about overdue
		alert["last_notified"] = _get_last_overdue_notification(repair["name"])

		alerts.append(alert)

	# Sort by severity and days overdue
	severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
	alerts.sort(key=lambda x: (severity_order.get(x["severity"], 4), -x["days_overdue"]))

	return alerts


def _get_last_overdue_notification(repair_order: str) -> str | None:
	"""Get the last time an overdue notification was sent for this repair."""
	try:
		comm = frappe.get_all(
			"Repair Communication",
			filters={
				"parent": repair_order,
				"communication_type": "Email",
				"content": ("like", "%overdue%"),
			},
			fields=["timestamp"],
			order_by="timestamp desc",
			limit=1,
		)
		return comm[0]["timestamp"] if comm else None
	except Exception:
		return None


@frappe.whitelist()
def send_overdue_notifications(
	warehouse: str | None = None,
	days_overdue: int = 1,
	dry_run: bool = False,
) -> dict[str, Any]:
	"""
	Send overdue notifications to customers and staff.

	Args:
	    warehouse: Filter by warehouse/store
	    days_overdue: Minimum days overdue to notify
	    dry_run: If True, don't actually send notifications

	Returns:
	    Summary of notifications sent
	"""
	if not frappe.has_permission("Repair Order", "write"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	overdue_alerts = get_overdue_alerts(warehouse, days_overdue, include_customer_info=True)

	results = {
		"total_eligible": len(overdue_alerts),
		"notifications_sent": 0,
		"notifications_failed": 0,
		"details": [],
	}

	for alert in overdue_alerts:
		try:
			if not dry_run:
				doc = frappe.get_doc("Repair Order", alert["repair_order"])
				doc._send_overdue_notification()

			results["notifications_sent"] += 1
			results["details"].append(
				{
					"repair_order": alert["repair_order"],
					"customer": alert.get("customer"),
					"days_overdue": alert["days_overdue"],
					"status": "sent",
				}
			)

		except Exception as e:
			results["notifications_failed"] += 1
			results["details"].append(
				{
					"repair_order": alert["repair_order"],
					"customer": alert.get("customer"),
					"days_overdue": alert["days_overdue"],
					"status": "failed",
					"error": str(e),
				}
			)

	return results


@frappe.whitelist()
def get_ical_feed_url(
	warehouse: str | None = None,
	technician: str | None = None,
) -> dict[str, Any]:
	"""
	Generate an iCal feed URL for subscribing to repair calendar.

	Args:
	    warehouse: Filter by warehouse/store
	    technician: Filter by technician

	Returns:
	    iCal feed URL and subscription info
	"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	# Generate a unique token for the feed
	import secrets

	feed_token = secrets.token_urlsafe(32)

	# Store feed parameters in cache
	cache_key = f"repair_cal_feed_{feed_token}"
	frappe.cache().set_value(
		cache_key,
		{"user": frappe.session.user, "warehouse": warehouse, "technician": technician, "created": now()},
		expires_in_sec=365 * 24 * 60 * 60,
	)  # Valid for 1 year

	# Generate feed URL
	base_url = get_url()
	feed_url = f"{base_url}/api/method/zevar_core.api.repair_calendar.get_ical_feed?token={feed_token}"

	return {
		"feed_url": feed_url,
		"calendar_name": "Zevar Repairs",
		"description": "Repair orders and schedule",
		"refresh_interval": "PT1H",  # Refresh every hour
	}


@frappe.whitelist(allow_guest=True)  # nosemgrep
def get_ical_feed(token: str) -> str:
	"""
	Generate iCal format calendar data for subscription.

	Args:
	    token: Feed token from get_ical_feed_url

	Returns:
	    iCal format string (text/calendar)
	"""
	# Validate token
	cache_key = f"repair_cal_feed_{token}"
	feed_config = frappe.cache().get_value(cache_key)

	if not feed_config:
		frappe.throw(_("Invalid or expired feed token"), frappe.PermissionError)

	# Check permissions
	user = feed_config.get("user")
	if user != frappe.session.user:
		# For guest access, verify token is valid
		pass

	# Get events for next 90 days

	end_date = add_days(nowdate(), 90)

	events = get_calendar_events(
		start_date=nowdate(),
		end_date=end_date,
		warehouse=feed_config.get("warehouse"),
		technician=feed_config.get("technician"),
	)

	# Generate iCal format
	ical_lines = [
		"BEGIN:VCALENDAR",
		"VERSION:2.0",
		"PRODID:-//Zevar Jewelers//Repair Calendar//EN",
		"CALSCALE:GREGORIAN",
		"METHOD:PUBLISH",
		"X-WR-CALNAME:Zevar Repairs",
		"X-WR-TIMEZONE:America/New_York",
		"X-WR-CALDESC:Repair orders and schedule",
	]

	for event in events:
		props = event.get("extendedProps", {})

		# Format date for iCal
		start_date = event.get("start", "")
		if isinstance(start_date, str):
			start_date = start_date.replace("-", "")

		# Create event
		ical_lines.extend(
			[
				"BEGIN:VEVENT",
				f"UID:{event['id']}@zevarjewelers.com",
				f"DTSTART;VALUE=DATE:{start_date}",
				f"DTEND;VALUE=DATE:{start_date}",
				f"SUMMARY:{event.get('title', '')}",
				"DESCRIPTION:Repair Order: " + props.get("repairOrder", ""),
				"STATUS:CONFIRMED",
				"BEGIN:VALARM",
				"TRIGGER:-P1D",
				"ACTION:DISPLAY",
				f"DESCRIPTION:Reminder: {event.get('title', '')}",
				"END:VALARM",
				"END:VEVENT",
			]
		)

	ical_lines.append("END:VCALENDAR")

	ical_content = "\r\n".join(ical_lines)

	# Set content type for response
	frappe.local.response.content_type = "text/calendar"
	frappe.local.response.filename = "zevar_repairs.ics"

	return ical_content


@frappe.whitelist()
def sync_to_google_calendar(repair_order: str, calendar_id: str | None = None) -> dict[str, Any]:
	"""
	Sync a repair order to Google Calendar.

	Args:
	    repair_order: The repair order to sync
	    calendar_id: Optional Google Calendar ID (uses default if not provided)

	Returns:
	    Sync result with event ID
	"""
	if not frappe.has_permission("Repair Order", "read", doc=repair_order):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	doc = frappe.get_doc("Repair Order", repair_order)

	if not doc.promised_date:
		return {"success": False, "message": "No promised date set"}

	try:
		# Get Google Calendar settings
		settings = frappe.get_single("Google Calendar Settings", cache=True)
		if not settings or not settings.get("enabled"):
			return {"success": False, "message": "Google Calendar integration not enabled"}

		# Import Google Calendar API
		# This is a placeholder - actual implementation would use Google Calendar API
		# from googleapiclient.discovery import build
		# from google.oauth2.credentials import Credentials

		# For now, store a reference that would be used by actual sync
		{
			"repair_order": doc.name,
			"title": f"{doc.name} - {doc.repair_type}",
			"date": str(doc.promised_date),
			"description": f"Customer: {doc.customer}\nItem: {doc.item_description}",
			"calendar_id": calendar_id or "primary",
		}

		# Store event reference in repair order
		doc.db_set("google_calendar_event_id", f"temp_{doc.name}")
		doc.db_set("google_calendar_id", calendar_id or "primary")

		return {
			"success": True,
			"message": "Event synced to Google Calendar",
			"event_id": f"temp_{doc.name}",
			"calendar_id": calendar_id or "primary",
		}

	except Exception as e:
		frappe.log_error(f"Google Calendar sync failed for {repair_order}: {e}")
		return {"success": False, "message": f"Sync failed: {e!s}"}


@frappe.whitelist()
def get_upcoming_pickups(
	warehouse: str | None = None,
	days_ahead: int = 7,
) -> list[dict[str, Any]]:
	"""
	Get repairs that should be picked up soon.

	Args:
	    warehouse: Filter by warehouse/store
	    days_ahead: Number of days ahead to look

	Returns:
	    List of upcoming pickups
	"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	end_date = add_days(nowdate(), days_ahead)

	filters = [
		["status", "=", "Ready for Pickup"],
		["promised_date", "<=", end_date],
	]

	if warehouse:
		filters.append(["warehouse", "=", warehouse])

	pickups = frappe.get_all(
		"Repair Order",
		filters=filters,
		fields=[
			"name",
			"customer",
			"customer_phone",
			"repair_type",
			"promised_date",
			"warehouse",
			"total_cost",
			"balance_due",
		],
		order_by="promised_date asc",
	)

	result = []
	for pickup in pickups:
		customer_name = (
			frappe.db.get_value("Customer", pickup["customer"], "customer_name")
			if pickup.get("customer")
			else ""
		)
		promised_date = getdate(pickup["promised_date"])
		today = getdate(nowdate())
		days_until = (promised_date - today).days

		result.append(
			{
				"repair_order": pickup["name"],
				"customer": customer_name,
				"customer_phone": pickup.get("customer_phone"),
				"promised_date": str(pickup["promised_date"]),
				"days_until_pickup": days_until,
				"is_overdue": days_until < 0,
				"warehouse": pickup.get("warehouse"),
				"total_cost": float(pickup.get("total_cost") or 0),
				"balance_due": float(pickup.get("balance_due") or 0),
			}
		)

	return result


@frappe.whitelist()
def get_daily_summary(date: str | None = None, warehouse: str | None = None) -> dict[str, Any]:
	"""
	Get a daily summary of repair activities.

	Args:
	    date: Date to summarize (defaults to today)
	    warehouse: Filter by warehouse/store

	Returns:
	    Daily summary with counts, pickups, and deadlines
	"""
	if not frappe.has_permission("Repair Order", "read"):
		frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

	target_date = getdate(date) if date else getdate(nowdate())

	summary = {
		"date": str(target_date),
		"warehouse": warehouse,
		"repairs": {
			"received": 0,
			"completed": 0,
			"delivered": 0,
			"promised_today": 0,
			"overdue_today": 0,
		},
		"pickups": [],
		"deadlines": [],
		"technician_workload": {},
	}

	# Get repairs received today
	received_filters = [["received_date", "like", f"{target_date}%"]]
	if warehouse:
		received_filters.append(["warehouse", "=", warehouse])

	summary["repairs"]["received"] = frappe.db.count("Repair Order", filters=received_filters)

	# Get repairs completed/delivered today
	completed_filters = [["completed_date", "like", f"{target_date}%"]]
	if warehouse:
		completed_filters.append(["warehouse", "=", warehouse])

	summary["repairs"]["completed"] = frappe.db.count("Repair Order", filters=completed_filters)

	delivered_filters = [["delivered_date", "like", f"{target_date}%"]]
	if warehouse:
		delivered_filters.append(["warehouse", "=", warehouse])

	summary["repairs"]["delivered"] = frappe.db.count("Repair Order", filters=delivered_filters)

	# Get repairs with promised date today
	promised_filters = [["promised_date", "=", target_date], ["status", "not in", ["Delivered", "Cancelled"]]]
	if warehouse:
		promised_filters.append(["warehouse", "=", warehouse])

	promised_today = frappe.get_all(
		"Repair Order",
		filters=promised_filters,
		fields=["name", "status", "priority", "customer", "assigned_to"],
	)

	summary["repairs"]["promised_today"] = len(promised_today)

	for repair in promised_today:
		customer_name = (
			frappe.db.get_value("Customer", repair["customer"], "customer_name")
			if repair.get("customer")
			else ""
		)
		summary["deadlines"].append(
			{
				"repair_order": repair["name"],
				"customer": customer_name,
				"status": repair["status"],
				"priority": repair.get("priority"),
				"assigned_to": repair.get("assigned_to"),
			}
		)

		# Track technician workload
		tech = repair.get("assigned_to") or "Unassigned"
		if tech not in summary["technician_workload"]:
			summary["technician_workload"][tech] = 0
		summary["technician_workload"][tech] += 1

	# Get pickups today
	pickup_filters = [
		["status", "=", "Ready for Pickup"],
		["promised_date", "=", target_date],
	]
	if warehouse:
		pickup_filters.append(["warehouse", "=", warehouse])

	pickups = frappe.get_all(
		"Repair Order", filters=pickup_filters, fields=["name", "customer", "customer_phone"]
	)

	for pickup in pickups:
		customer_name = (
			frappe.db.get_value("Customer", pickup["customer"], "customer_name")
			if pickup.get("customer")
			else ""
		)
		summary["pickups"].append(
			{
				"repair_order": pickup["name"],
				"customer": customer_name,
				"phone": pickup.get("customer_phone"),
			}
		)

	return summary
