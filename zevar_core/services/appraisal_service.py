"""Appraisal management service.

Handles jewelry appraisal lifecycle: creation, expiry tracking,
and reminder scheduling.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_months, flt, now_datetime, nowdate


def create_appraisal(
	item_code: str,
	serial_no: str | None = None,
	template_name: str | None = None,
	customer: str | None = None,
	appraised_value: float | None = None,
	notes: str | None = None,
) -> dict:
	"""Create a new Jewelry Appraisal."""
	appraisal = frappe.new_doc("Jewelry Appraisal")
	appraisal.item_code = item_code
	appraisal.serial_no = serial_no or ""
	appraisal.customer = customer or ""
	appraisal.appraised_value = flt(appraised_value or 0)

	if template_name:
		template = frappe.get_doc("Zevar Appraisal Template", template_name)
		appraisal.appraisal_template = template_name
		validity_months = template.default_validity_months or 24
	else:
		validity_months = 24

	appraisal.valid_until = add_months(nowdate(), validity_months)
	appraisal.notes = notes or ""

	appraisal.insert(ignore_permissions=True)

	return {"success": True, "appraisal": appraisal.name, "valid_until": appraisal.valid_until}


def get_expiring_appraisals(days_ahead: int = 90) -> list[dict]:
	"""Get appraisals expiring within the given days window."""
	from frappe.utils import add_days

	cutoff = add_days(nowdate(), days_ahead)

	return frappe.get_all(
		"Jewelry Appraisal",
		filters={
			"valid_until": ["<=", cutoff],
			"valid_until": [">=", nowdate()],
			"docstatus": ["!=", 2],
		},
		fields=[
			"name", "item_code", "serial_no", "customer",
			"appraised_value", "valid_until", "appraisal_template",
		],
		order_by="valid_until asc",
	)


def send_expiry_reminders() -> dict:
	"""Send 90/60/30-day expiry reminders. Called by scheduler."""
	now = nowdate()
	reminders_sent = {"90_day": 0, "60_day": 0, "30_day": 0}

	# 90-day reminder
	appraisals_90 = frappe.get_all(
		"Jewelry Appraisal",
		filters={
			"valid_until": add_months(now, 3),
			"reminder_90_sent": 0,
			"docstatus": ["!=", 2],
		},
		pluck="name",
	)
	for name in appraisals_90:
		_send_reminder(name, 90)
		frappe.db.set_value("Jewelry Appraisal", name, "reminder_90_sent", 1)
		reminders_sent["90_day"] += 1

	# 60-day reminder
	appraisals_60 = frappe.get_all(
		"Jewelry Appraisal",
		filters={
			"valid_until": add_months(now, 2),
			"reminder_60_sent": 0,
			"docstatus": ["!=", 2],
		},
		pluck="name",
	)
	for name in appraisals_60:
		_send_reminder(name, 60)
		frappe.db.set_value("Jewelry Appraisal", name, "reminder_60_sent", 1)
		reminders_sent["60_day"] += 1

	# 30-day reminder
	from frappe.utils import add_days
	appraisals_30 = frappe.get_all(
		"Jewelry Appraisal",
		filters={
			"valid_until": add_days(now, 30),
			"reminder_30_sent": 0,
			"docstatus": ["!=", 2],
		},
		pluck="name",
	)
	for name in appraisals_30:
		_send_reminder(name, 30)
		frappe.db.set_value("Jewelry Appraisal", name, "reminder_30_sent", 1)
		reminders_sent["30_day"] += 1

	frappe.db.commit()
	return reminders_sent


def get_appraisal_history(item_code: str, serial_no: str | None = None) -> list[dict]:
	"""Get all appraisals for an item, newest first."""
	filters = {"item_code": item_code}
	if serial_no:
		filters["serial_no"] = serial_no

	return frappe.get_all(
		"Jewelry Appraisal",
		filters=filters,
		fields=[
			"name", "item_code", "serial_no", "customer",
			"appraised_value", "appraisal_date", "valid_until",
			"appraisal_template", "docstatus",
		],
		order_by="appraisal_date desc",
	)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _send_reminder(appraisal_name: str, days: int):
	appraisal = frappe.get_doc("Jewelry Appraisal", appraisal_name)
	frappe.log_error(
		f"Appraisal expiry reminder ({days} days): {appraisal_name}",
		f"Item: {appraisal.item_code}, Serial: {appraisal.serial_no}, "
		f"Customer: {appraisal.customer}, Expires: {appraisal.valid_until}",
	)
